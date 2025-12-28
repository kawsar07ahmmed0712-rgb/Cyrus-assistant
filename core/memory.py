import json
import os

def memory(prompt, response):
    new_entry = [
        {"role": "user", "content": prompt},
        {"role": "assistant", "content": response}
    ]

    file_path = "History.json"

    # ফাইল আছে কি না চেক করা
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            data = []
    else:
        data = []


    data.extend(new_entry)


    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
