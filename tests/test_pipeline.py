import json
import os

# Get the directory of the current script
script_dir = os.path.dirname(__file__)
file_path = os.path.join(script_dir,'..', 'data', "user_data.json")

with open(file_path, "r") as f:
    user_data = json.load(f)

print(user_data[0])
