from utility.logger import initial_log
from threading import Lock
import pymysql


db_settings = {
    'host': 'xiamishu.cwoykqzckygl.ap-northeast-1.rds.amazonaws.com',
    'port': 3306,
    'user': 'admin',
    'password': 'xiamishu.93',
    'db': 'dev',
    'charset': 'utf8'
}


class Mysql:
    def __init__(self, settings, logger=None):
        self.settings = settings
        self.logger = logger or initial_log('Mysql')
        self.conn = None
        self._locker = Lock()

    def connect_db(self):
        conn = pymysql.connect(**db_settings)
        return conn

    def close_connection(self):
        with self._locker:
            if self.conn:
                self.conn.close()
                self.conn = None

    def execute_one_query(self, query, commit=False):
        if not query:
            print(f'wrong query => {query}')
            return False
        
        try:
            with self._locker:
                if self.conn is None:
                    self.conn = self.connect_db()
                if self.conn:
                    c = self.conn.cursor()
                    c.execute(query)
                    data = c.fetchall()
                    if commit:
                        self.conn.commit()
        except BaseException as e:
            self.close_connection()
            self.logger.error(f'While executing query:\n{query}\nOther Exception:\n{e}')
            return False, []

        self.close_connection()
        return True, data or []


class GetMysql:
    my_instance = None
    def __new__(cls, db_settings, logger=None):
        if cls.my_instance is None:
            cls.my_instance = Mysql(db_settings, logger)
        return cls.my_instance


if __name__ == '__main__':
    db1 = GetMysql(db_settings)
    db2 = GetMysql(db_settings)
    print(id(db1) == id(db2))