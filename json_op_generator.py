import json
import os

# Load the JSON data from the file
with open("ops_data.json", "r") as f:
    data = json.load(f)

# Create the "OP" directory if it doesn't exist
os.makedirs("OP", exist_ok=True)

# Iterate over the data and write each dictionary to a separate file
for item in data:
    code = item["code"]
    filename = os.path.join("OP", f"{code}.json")
    with open(filename, "w") as f:
        json.dump([item], f, indent=2)
