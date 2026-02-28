import streamlit as st
import re
import time
from prompts import (
    SYSTEM_PROMPT,
    INFO_FIELDS,
    QUESTION_PROMPT_TEMPLATE,
    EVALUATION_PROMPT_TEMPLATE
)
from validators import (
    validate_email,
    validate_phone,
    validate_full_name,
    validate_experience,
    validate_tech_stack,
    is_exit_command
)
from llm_handler import generate_llm_response
from storage import save_candidate
st.set_page_config(page_title="TalentScout Hiring Assistant")
st.title("🤖 TalentScout Hiring Assistant")
# ANSWER VALIDATION
def validate_answer(text):
    text = text.strip()
    if len(text) < 30:
        return False
    words = re.findall(r"[A-Za-z]{3,}", text)
    if len(words) < 6:
        return False
    return True
# SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

if "stage" not in st.session_state:
    st.session_state.stage = "info"

if "field_index" not in st.session_state:
    st.session_state.field_index = 0

if "candidate_data" not in st.session_state:
    st.session_state.candidate_data = {}

if "question_list" not in st.session_state:
    st.session_state.question_list = []

if "question_index" not in st.session_state:
    st.session_state.question_index = 0

if "answers" not in st.session_state:
    st.session_state.answers = ""

if "questions_raw" not in st.session_state:
    st.session_state.questions_raw = ""

if "start_time" not in st.session_state:
    st.session_state.start_time = time.time()
# GREETING
if len(st.session_state.messages) == 0:
    st.session_state.messages.append({
        "role": "assistant",
        "content": "**👋Welcome to TalentScout Interview Portal.👋**"
        "\n\nI will guide you through a series of technical questions based on your selected technology stack. Your responses will be evaluated to assess your problem-solving ability, technical knowledge, and clarity of explanation."
        "\n\nPlease read each question carefully and provide your answer in the input box."
        "\n\nPlease enter your **Full Name**."
    })
# DISPLAY CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
user_input = st.chat_input("Type your response...")
if user_input:
    if is_exit_command(user_input):
        st.stop()
    st.session_state.messages.append({"role": "user", "content": user_input})
# INFO COLLECTION
    if st.session_state.stage == "info":
        field = INFO_FIELDS[st.session_state.field_index]
        valid = True
        if field == "Full Name":
            valid = validate_full_name(user_input)
        elif field == "Email Address":
            valid = validate_email(user_input)
        elif field == "Phone Number":
            valid = validate_phone(user_input)
        elif field == "Years of Experience":
            valid = validate_experience(user_input)
        elif field == "Tech Stack":
            valid = validate_tech_stack(user_input)
        if not valid:
            response = f"Invalid **{field}**. Please try again."
        else:
            st.session_state.candidate_data[field] = user_input
            st.session_state.field_index += 1
            if st.session_state.field_index < len(INFO_FIELDS):
                next_field = INFO_FIELDS[st.session_state.field_index]
                response = f"Please enter your **{next_field}**."
            else:
                tech = st.session_state.candidate_data["Tech Stack"]
                prompt = QUESTION_PROMPT_TEMPLATE.format(
                    tech_stack=tech
                )
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
                questions = generate_llm_response(messages)
                pattern = r"\d+\.\s.*"
                q_list = re.findall(pattern, questions)
                # fallback if LLM fails
                if len(q_list) < 5:
                    q_list = [
                        "1. Explain the difference between list and tuple in Python.",
                        "2. What is a Python decorator? Explain with example.",
                        "3. Explain how HTML and CSS work together.",
                        "4. What is the difference between GET and POST request?",
                        "5. What is Object Oriented Programming?"
                    ]
                st.session_state.question_list = q_list[:5]
                st.session_state.questions_raw = "\n".join(q_list[:5])
                st.session_state.stage = "questions"
                st.session_state.question_index = 0
                response = f"**Question 1 of 5**\n\n{q_list[0]}"
                save_candidate(st.session_state.candidate_data)
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
# QUESTION PHASE
    elif st.session_state.stage == "questions":
        if not validate_answer(user_input):
            response = "⚠ Please provide a meaningful technical answer."
        else:
            q = st.session_state.question_list[st.session_state.question_index]
            st.session_state.answers += f"{q}\n{user_input}\n\n"
            st.session_state.question_index += 1
            if st.session_state.question_index < 5:
                next_q = st.session_state.question_list[
                    st.session_state.question_index
                ]
                response = f"**Question {st.session_state.question_index+1} of 5**\n\n{next_q}"
            else:
                eval_prompt = EVALUATION_PROMPT_TEMPLATE.format(
                    questions=st.session_state.questions_raw,
                    answers=st.session_state.answers
                )
                messages = [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": eval_prompt}
                ]
                result = generate_llm_response(messages)
                response = "### Evaluation Result\n\n" + result
                st.session_state.stage = "completed"
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()
# COMPLETION
if st.session_state.stage == "completed":
    end_time = time.time()
    duration = int(end_time - st.session_state.start_time)
    st.success("✅ Interview Completed Successfully!")
    st.info(f"Interview Duration: {duration} seconds")
    st.markdown(
    """
### **🎉 Thank you for completing the interview!**
\n\nOur recruitment team will review your responses.
\n\n**Next Steps**
\n\n• Technical answers will be evaluated
\n\n• Shortlisted candidates will receive email communication"
\n\n• Further interview rounds may follow
\n\n We appreciate your interest in TalentScout."
"""
    )
    if st.button("Restart Interview"):
        st.session_state.clear()
        st.rerun()