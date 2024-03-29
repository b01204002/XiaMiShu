# coding=utf-8

import os
import json


def path_join(*args):
    path_ = os.path.abspath(__file__)
    path_ = path_[:path_.find('bin')]
    path_ = os.path.join(path_, *args)
    return path_

def read_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        result = json.load(f)
    return result

def save_json(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(content, f, ensure_ascii=False, indent=4)