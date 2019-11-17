import json
def read_file():
    with open("balance.json", "r") as read_json:
        result = json.load(read_json)
    return result