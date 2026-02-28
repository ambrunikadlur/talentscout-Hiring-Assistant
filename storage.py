import json
from datetime import datetime
FILE_NAME = "candidates.json"
def save_candidate(data):
    data["timestamp"] = str(datetime.now())
    try:
        with open(FILE_NAME, "r") as file:
            existing = json.load(file)
    except:
        existing = []
    existing.append(data)
    with open(FILE_NAME, "w") as file:
        json.dump(existing, file, indent=4)