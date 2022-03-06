from googleapiclient.discovery import build
from google.oauth2 import service_account
from utility.LittleTool import path_join


SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]
KEY_FILE = path_join('cfg', 'gcp_key.json')


class GoogleSheetsController:
    def __init__(self):
        self.creds = self.init_creds()
        self.drive_service = build('drive', 'v3', credentials=self.creds)
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)

    def init_creds(self):
        creds = service_account.Credentials.from_service_account_file(
            filename=KEY_FILE, scopes=SCOPES)
        return creds

    def check_files_in_drive(self):
        files = self.drive_service.files().list().execute()
        return files.get('files')

    def delete_file_in_drive(self, sheet_id):
        delete = self.drive_service.files().delete(fileId=sheet_id).execute()
        return delete

    def change_permission(self, file_id, role, type):
        prop = {
            'role': role,
            'type': type
        }
        permission = self.drive_service.permissions().create(
            fileId=file_id,
            body=prop
        ).execute()

        return permission.get('id')

    def create_spreadsheets(self, title):
        prop = {
            'properties': {
                'title': title
            }
        }
        spreadsheet = self.sheets_service.spreadsheets().create(
            body=prop,
            fields='spreadsheetId'
        ).execute()

        return spreadsheet.get('spreadsheetId')

    def add_sheet(self):
        pass

    def read_value(self, spreadsheet_id, sheet_name, range='1:1069', value_render_option='FORMATTED_VALUE', date_time_render_option='FORMATTED_STRING'):
        # value_render_option: 'FORMATTED_VALUE', 'UNFORMATTED_VALUE', 'FORMULA'
        # date_time_render_option: 'FORMATTED_STRING', 'SERIAL_NUMBER'
        sheet = self.sheets_service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=spreadsheet_id,
            range=f'{sheet_name}!{range}',
            majorDimension='ROW',
            valueRenderOption = value_render_option,
            dateTimeRenderOption = date_time_render_option
        ).execute()
        values = result.get('values', [])
        return values

    def update_value(self, spreadsheet_id, sheet_name, range, values):
        sheet = self.sheets_service.spreadsheets()
        result = sheet.values.update(
            spreadsheetId=spreadsheet_id,
            range=f'{sheet_name}!{range}',
            valueInputOption='USER_ENTERED',
            body={
                'values': values
            }
        ).execute()
        return result.get('updatedCells')

if __name__ == '__main__':
    gs = GoogleSheetsController()

    # # drive 小工具
    # files = gs.drive_service.files().list().execute().get('files')
    # delete = gs.drive_service.files().delete(fileId='sheet_id').execute()

    # sheet_id = gs.create_spreadsheets('GGG')
    # print(sheet_id)
    # permission_id = gs.change_permission(sheet_id, 'writer', 'anyone')
    # values = gs.read_value('1I5D0ildIfmMBzAICcMTog2LHoukw0qJrAbAJ-D9eutI', '2021 Q3 BV', '1:1069')
    # for v in values:
    #     print(v)
