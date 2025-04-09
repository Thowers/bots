import json

user_languages = {}

def load_language(lang):
    try:
        with open(f'languages/{lang}.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return json.load(f)