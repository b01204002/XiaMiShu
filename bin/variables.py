from utility.little_tool import path_join, read_json

CFG_PATH = path_join('cfg', 'cfg.dev.json')
cfg = read_json(CFG_PATH)
db_settings = cfg['db_settings']
line_channel = cfg['line_channel']

GOOGLE_SHEET_URL_FORMAT = 'https://docs.google.com/spreadsheets/d/{sheet_id}/edit#gid=0'