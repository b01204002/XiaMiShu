import json
import os

def path_join(*args):
    path_ = os.path.abspath(__file__)
    path_ = path_[:path_.find('bin')]
    path_ = os.path.join(path_, *args)
    return path_

def save_json(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(content, f, indent=4, ensure_ascii=False)

def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

line_settings = read_json(path_join('cfg', 'line_settings.json'))
LINE_CHANNEL_SECRET = line_settings.get('LINE_CHANNEL_SECRET')
LINE_CHANNEL_ACCESS_TOKEN = line_settings.get('LINE_CHANNEL_ACCESS_TOKEN')
LINE_USER_ID = line_settings.get('LINE_USER_ID')