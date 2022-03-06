from variables import GOOGLE_SHEET_URL_FORMAT

REPLY_TEXT = 'text'


class LineReplyGenerator:
    def __init__(self):
        pass

    def reply_create_sheet(self, sheet_id):
        text = f'已創建Google試算表，請按「秘書開工囉！」開始記帳。\n\n' \
            f'您可以將試算表建立連結於您的Google Drive，以便查看\n' \
            f'{GOOGLE_SHEET_URL_FORMAT.format(sheet_id=sheet_id)}'
        return REPLY_TEXT, text

