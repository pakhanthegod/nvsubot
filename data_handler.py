import json

def load_json(file_name):
    with open(file_name, 'r', encoding='utf-8') as fs:
        return json.load(fs)