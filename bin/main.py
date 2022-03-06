from google_sheet_controller import GoogleSheetsController
from line_reply_generator import LineReplyGenerator
from utility.LittleTool import read_json
from variables import USER_INFO_PATH, GOOGLE_SHEET_URL_FORMAT

def text_processor(line_id, text):
    pass

class Accounting:
    def __init__(self):
        self.sheet_controller = GoogleSheetsController()
        self.reply_generator = LineReplyGenerator()
        self.user_info = read_json(USER_INFO_PATH)

    def create_sheet(self, line_id):
        sheet_id = self.sheet_controller.create_spreadsheets(f'蝦秘書_{line_id}')
        self.sheet_controller.change_permission(sheet_id, 'writer', 'anyone')
        self.user_info[line_id]['google_sheets'].append({
            "name": "我的帳本",
            "id": sheet_id
        })
        return True, sheet_id

    def view_sheets(self, line_id):
        gsheets = self.user_info[line_id]['google_sheets']
        return True, gsheets

    def set_default_sheet(self, line_id, gsheet_id):
        gsheets = self.user_info[line_id]['google_sheets']
        for idx, gsheet in enumerate(gsheets):
            if gsheet.get('id') == gsheet_id:
                if idx > 0:
                    gsheets.insert(0, gsheets[idx])
                    gsheets.pop(idx + 1)
                break
        return True, gsheets

    


if __name__ == '__main__':
    a = Accounting()

    LINE_ID = 'test'
    r_type, t_text = a.create_sheet(LINE_ID)
    print(r_type, t_text)


