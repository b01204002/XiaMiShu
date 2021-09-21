from tools import path_join, read_json, save_json
from datetime import datetime
import re

user_path = path_join('cfg', 'users_info.json')
work_log_path = path_join('cfg', 'work_log_2021_Q2.json')

unregisted_r_text = '請先告訴魯夫你是哪一組的成員喔！請參考以下格式輸入\n\n新海賊來也\n我是XX組的YYY'

def error_function():
    r_text = '很抱歉，魯夫沒有聽懂你的意思\n可以輸入"海賊交戰手冊"看看魯夫可以怎麼一起合作喔！'
    return r_text

def register(*args):
    user_id = args[0]
    content_str = args[1]
    regex = r"我是(.*)組的(.*)"
    for match in re.finditer(regex, content_str):
        team = match.group(1)
        name = match.group(2)

    users = read_json(user_path)
    ori_team = ''
    ori_name = ''
    if user_id in users:
        ori_team = users[user_id]['team']
        ori_name = users[user_id]['name']
        if team == ori_team and name == ori_name:
            r_text = f'你已經是2020-Q2海賊爭霸賽<{team}組>的成員囉！'
            return r_text

    if user_id not in users:
        users[user_id] = {}
    users[user_id]['team'] = team
    users[user_id]['name'] = name
    save_json(user_path, users)
    if ori_name or ori_team:
        r_text = f'哈囉<{name}>\n已經將你轉換至<{team}組>囉！'
    else:
        r_text = f'恭喜<{name}>加入2020-Q2海賊爭霸賽~\n一起為<{team}組>衝刺吧！'
    return r_text

def check_registed(user_id):
    users = read_json(user_path)
    if user_id in users:
        return True
    return False

def work_log(*args):
    user_id = args[0]
    content_str = args[1]
    if not check_registed(user_id):
        return unregisted_r_text
    items = [
        '清單',
        '群組',
        'BV',
        'IBV'
    ]
    work_log = read_json(work_log_path)
    not_in_items = []
    r_text = ''
    content_list = content_str.split('/n')
    regex = r"(.*)([+＋-])([\d\.]+)"
    for match in re.finditer(regex, content_str):
        item = match.group(1)
        item = item.replace('Ｉ', 'I').replace('Ｂ', 'B').replace('Ｖ', 'V')
        amount = int(round(float(match.group(3))))
        amount *= -1 if match.group(2) == '-' else 1
        if item not in items:
            not_in_items.append(item)
            continue
        work_log.append({
            'user_id': user_id,
            'date': datetime.today().strftime("%Y-%m-%d"),
            'item': item,
            'amount': amount
        })
        r_text += f'{item} +{amount}\n'
    save_json(work_log_path, work_log)
    if r_text:
        r_text += f'================\n今天的工作日誌已登記，你真棒！'
    if not_in_items:
        if r_text:
            r_text += '\n'
        r_text += f'<{"、".join(not_in_items)}>這些項目無法登記，請重新輸入！'
    return r_text

def get_score(*args):
    content_str = args[1]
    item_score = {
        '清單': 50
    }
    users = read_json(user_path)
    work_log = read_json(work_log_path)
    today = datetime.today().strftime("%Y-%m-%d")
    
    team_score = {}
    today_action = {}
    for log in work_log:
        user_id = log.get('user_id')
        team = users.get(user_id, {}).get('team', 'NO TEAM')
        name = users.get(user_id, {}).get('name', 'NO NAME')
        item = log.get('item')
        amount = log.get('amount', 0)
        date = log.get('date', '')
        if team not in team_score:
            team_score[team] = 0
        team_score[team] += amount * item_score.get(item, 1)

        if date != today:
            continue
        if team not in today_action:
            today_action[team] = {}
        if user_id not in today_action[team]:
            today_action[team][user_id] = {'name': name, 'score': 0, 'action': {}}
        if item not in today_action[team][user_id]['action']:
            today_action[team][user_id]['action'][item] = 0
        today_action[team][user_id]['action'][item] += amount
        today_action[team][user_id]['score'] += amount * item_score.get(item, 1)
    
    r_text = '目前戰況：\n'
    top_score = 0
    top_team = ''
    for team in sorted(team_score.keys()):
        r_text += f'{team}組累計 <{team_score[team]}分>\n'
        if team_score[team] > top_score:
            top_score = team_score[team]
            top_team = team
    r_text += f'\n恭喜<{top_team}組>暫居第一！'

    if not today_action:
        return r_text
    r_text += '\n\n================\n\n'
    r_text += '今日行動：\n'

    top_score = 0
    top_user = ''
    for team, team_action in today_action.items():
        r_text += f'<{team}組>\n'
        for user_id, user_item in team_action.items():
            if user_item['score'] > top_score:
                top_score = user_item['score']
                top_user = user_item['name']
            r_text += f'{user_item["name"]}: '
            for item, amount in user_item['action'].items():
                r_text += f'{item}+{amount}、'
            r_text = r_text[:-1] + '\n'
    r_text += f'\n恭喜<{top_user}>成為今日行動王！'

    return r_text

def get_score_details(*args):
    action = {}
    for log in work_log:
        user_id = log.get('user_id')
        team = users.get(user_id, {}).get('team', 'NO TEAM')
        name = users.get(user_id, {}).get('name', 'NO NAME')
        item = log.get('item')
        amount = log.get('amount', 0)
        date = log.get('date', '')
        if team not in team_score:
            team_score[team] = 0
        team_score[team] += amount * item_score.get(item, 1)

        if team not in action:
            action[team] = {}
        if user_id not in action[team]:
            action[team][user_id] = {'name': name, 'score': 0, 'action': {}}
        if item not in action[team][user_id]['action']:
            action[team][user_id]['action'][item] = 0
        action[team][user_id]['action'][item] += amount
        action[team][user_id]['score'] += amount * item_score.get(item, 1)
    return 'get_score_details'

def get_my_score(*args):
    return 'get_my_score'

def get_partner_score(*args):
    return 'get_partner_score'

def get_rules(*args):
    return 'get_rules'

state_sentence = {
    '新海賊來也': register,
    '海賊上工': work_log,
    '海賊目前戰況': get_score,
    '海賊戰況分析': get_score_details,
    '我是海賊王': get_my_score,
    '海賊隊友': get_partner_score,
    '海賊交戰手冊': get_rules
}

def main_processor(user_id, text):
    topic = text.strip()
    content_str = ''
    if '\n' in text:
        topic, content_str = text[:text.index('\n')], text[text.index('\n')+1:]
        topic = topic.strip()

    if topic not in state_sentence:
        r_text = error_function()
        return r_text
    r_text = state_sentence[topic](user_id, content_str)
    return r_text