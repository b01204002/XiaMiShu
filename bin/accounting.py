from utility.database import GetMysql
from utility.logger import initial_log
from variables import db_settings
from datetime import datetime
import time


class Accounting:
    def __init__(self):
        self.logger = initial_log('Accounting')
        self.db = GetMysql(db_settings, logger=self.logger)

    def insert_user(self, name:str, line_id:str, email:str):
        now_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        query = f'INSERT INTO user (name, line_id, email, join_date) ' \
            f'VALUES ("{name}", "{line_id}", "{email}", "{now_date}");'
        success, _ = self.db.execute_one_query(query, commit=True)
        return success

    def insert_book(self):
        now_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
        book_uid = f'{now_date}-{round(time.time()*1000)}'
        query = f'INSERT INTO book (uid, create_date) VALUES ("{book_uid}", "{now_date}");'
        success, _ = self.db.execute_one_query(query, commit=True)
        if not success:
            self.logger.error('[insert_book] 新增記帳本失敗')
            return ''
        return book_uid

    def combine_user_book(self, user_name, book_id, book_name='default'):
        query = f'INSERT INTO user_book (user_id, book_id, book_name) VALUES (' \
            f'(SELECT id FROM user WHERE name = "{user_name}"), ' \
            f'(SELECT id FROM book WHERE uid = "{book_id}"), ' \
            f'"{book_name}");'
        success, _ = self.db.execute_one_query(query, commit=True)
        return success

    def set_category(self, user_name, category, category_group, is_income=False):
        query = f'SELECT id FROM category_group WHERE name = "{category_group}";'
        success, group_id = self.db.execute_one_query(query)
        if not success:
            self.logger.error('[set_category] select group_id failed.')
            return success

        if not group_id:
            query = f'INSERT INTO category_group (name) VALUES ("{category_group}");'
            success, group_id = self.db.execute_one_query(query, commit=True)
            if not success:
                self.logger.error('[set_category] insert group_id failed.')
                return success

        query = f'INSERT INTO category (name, income_expenses, group_id, user_id) VALUES (' \
            f'"{category}", {1 if is_income else -1}, ' \
            f'(SELECT id FROM category_group WHERE name = "{category_group}"), ' \
            f'(SELECT id FROM user WHERE name = "{user_name}"));'
        success, _ = self.db.execute_one_query(query, commit=True)
        if not success:
            self.logger.error('[set_category] insert category failed.')
            return success

        return success

    def insert_data(self, user_id, book_id, category_id, amount, notes):
        query = f'INSERT INTO (user_id, book_id, category_id, amount, notes) VALUES (' \
            f'{user_id}, {book_id}, {category_id}, {amount}, "notes";'
        # line_id進來時就知道有哪些category_id可用還有user_id



if __name__ == '__main__':
    a = Accounting()
    user_name = 'XiaMiShu'
    # a.insert_user(user_name, '', '')
    # book_id = a.insert_book()
    # a.combine_user_book(user_name, book_id)
    # category = {
    #     "支出": {
    #         "食品酒水": [
    #             "午餐",
    #             "晚餐",
    #             "消夜",
    #             "飲料",
    #             "零食點心"
    #         ],
    #         "交通": [
    #             "悠遊卡儲值",
    #             "計程車",
    #             "電信費",
    #             "油費",
    #             "稅金"
    #         ],
    #         "運動": [
    #             "健身房",
    #             "課程"
    #         ],
    #         "學習": [
    #             "書籍",
    #             "上課進修",
    #             "網路課程"
    #         ],
    #         "衣裝": [
    #             "衣服",
    #             "保養品",
    #             "化妝品",
    #             "配件",
    #             "剪髮"
    #         ],
    #         "醫療": [
    #             "掛號費",
    #             "藥品",
    #             "保健品"
    #         ],
    #         "娛樂": [
    #             "旅遊",
    #             "串流平台",
    #             "寵物",
    #             "休閒玩樂"
    #         ],
    #         "其他": [
    #             "紅包",
    #             "孝親"
    #         ]
    #     },
    #     "收入": {
    #         "主動收入": [
    #             "薪資",
    #             "兼職",
    #             "獎金"
    #         ],
    #         "被動收入": [
    #             "股息",
    #             "房租"
    #         ],
    #         "其他": [
    #             "紅包"
    #         ]
    #     }
    # }
    # for income, group_item in category.items():
    #     for group, c_list in group_item.items():
    #         for c in c_list:
    #             a.set_category(user_name, c, group, is_income=income == '收入')
    #             print(c, group)