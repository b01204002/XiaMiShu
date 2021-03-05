# coding=utf-8

from Utility.LittleTool import path_join
from Utility.Singleton import Singleton
from Utility.logger import initial_log
from datetime import datetime, timedelta
from threading import Lock
import sqlite3

SELECT = 0
INSERT = 1
UPDATE = 2
DELETE = 3

class db_query(metaclass=Singleton):
    def __init__(self, db_path):
        self.logger = initial_log('db_query')
        self.db_path = db_path
        self.conn = None
        self._locker = Lock()
        self.last_date = None

    def connect_db(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return conn

    def close_connection(self):
        with self._locker:
            if self.conn:
                self.conn.close()
                self.conn = None

    def _execute_query(self, query='', action=SELECT):
        data = None
        last_id = 0
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
                    if action == INSERT:
                        last_id = c.lastrowid
                    if action != SELECT:
                        self.conn.commit()

        except BaseException as e:
            self.close_connection()
            self.logger.exception(f'While executing query:\n{query}\n'
                                  f'Other Exception:\n{e}')
            return False

        self.close_connection()

        if action == INSERT:
            return [last_id] or []
        else:
            return data or []

    def insert_BV_product(self, name:str, nick_name:list, picture:str, cost:int, exp_price:int, BV:float):
        query = f"INSERT INTO BV_product (name, picture, cost, exp_price, BV)" \
                f"VALUES (\'{name}\', \'{picture}\', \'{cost}\', \'{exp_price}\', \'{BV}\');"
        BV_product_idx = self._execute_query(query, action=INSERT)

        for nick in nick_name + [name]:
            query = f"INSERT INTO BV_product_nickname (BV_product_idx, nick_name)" \
                f"VALUES (\'{BV_product_idx[0]}\', \'{nick}\');"
            self._execute_query(query, action=INSERT)
        return

    def insert_customer(self, name:str, nick_name:list, birthday:str, phone:str, address:str, postal_code:str):
        query = f"INSERT INTO customer (name, birthday, phone, address, postal_code)" \
            f"VALUES (\'{name}\', \'{birthday}\', \'{phone}\', \'{address}\', \'{postal_code}\');"
        customer_idx = self._execute_query(query, action=INSERT)

        for nick in nick_name + [name]:
            query = f"INSERT INTO customer_nickname (customer_idx, nick_name)" \
                f"VALUES (\'{customer_idx[0]}\', \'{nick}\');"
            self._execute_query(query, action=INSERT)
        return

    def insert_operation(self, date:str, name:str, type:str, cost:int, price:int):
        query = f"INSERT INTO operation (date, type, name, cost, price)" \
            f"VALUES (\'{date}\', \'{type}\', \'{name}\', \'{cost}\', \'{price}\');"
        return self._execute_query(query, action=INSERT)

    def insert_IBV_store(self, name:str, nick_name:list, IBV:float):
        query = f"INSERT INTO IBV_store (name, IBV) VALUES (\'{name}\', \'{IBV}\');"
        IBV_store_idx = self._execute_query(query, action=INSERT)

        for nick in nick_name + [name]:
            query = f"INSERT INTO IBV_store_nickname (IBV_store_idx, nick_name)" \
                f"VALUES (\'{IBV_store_idx[0]}\', \'{nick}\');"
            self._execute_query(query, action=INSERT)
        return

    def select_customer_idx(self, name):
        query = f"SELECT customer_idx FROM customer_nickname WHERE nick_name == \'{name}\'"
        q = self._execute_query(query, action=SELECT)
        if not q:
            return [0]
        return q[0]

    def select_BV_info(self, name):
        idx = 0
        BV = 0
        cost = 0
        exp_price = 0
        query = f"SELECT BV_product_idx FROM BV_product_nickname WHERE nick_name == \'{name}\'"
        q = self._execute_query(query, action=SELECT)
        if not q:
            return (idx, BV, cost, exp_price)

        query = f"SELECT idx, BV, cost, exp_price FROM BV_product WHERE idx == {q[0][0]}"
        q = self._execute_query(query, action=SELECT)
        if not q:
            return (idx, BV, cost, exp_price)
        return q[0]

    def insert_BV_order_product(self, BV_order_idx, BV_product_idx, amount, details):
        query = f"INSERT INTO BV_order_product (BV_order_idx, BV_product_idx, amount, details) " \
            f"VALUES ({BV_order_idx}, {BV_product_idx}, {amount}, \'{details}\');"
        return self._execute_query(query, action=INSERT)

    def insert_BV_order(self, customer_idx:int, order_date:str, purchase_date:str, delivery_date:str, products:dict, cost:int, price:int):
        total_BV = 0
        total_cost = 0
        total_exp_price = 0
        products_list = []
        for p in products:
            p_name = p.get('product_name', '')
            p_amount = p.get('amount', 1)
            p_idx, p_BV, p_cost, p_exp_price = self.select_BV_info(p_name)
            total_BV += p_BV * p_amount
            total_cost += p_cost * p_amount
            total_exp_price += p_exp_price * p_amount
            products_list.append((p_idx, p_amount, p.get('detail', '')))

        if total_cost != cost:
            print(f'strange cost?! {order_date}, {products}, {cost}, {total_cost}')
            return

        if customer_idx > 3 and not delivery_date:
            print(f'no price?! {order_date}, {customer_idx}')

        query = f"INSERT INTO BV_order (customer_idx, order_date, purchase_date, delivery_date, BV, cost, exp_price, price) " \
            f"VALUES (\'{customer_idx}\', \'{order_date}\', \'{purchase_date}\', \'{delivery_date}\', \'{total_BV}\', \'{cost}\', \'{total_exp_price}\', \'{price}\');"
        q = self._execute_query(query, action=INSERT)
        if not q:
            return 0

        for p in products_list:
            self.insert_BV_order_product(q[0], p[0], p[1], p[2])

        return

    def insert_IBV_ordder(self):
        pass

if __name__ == '__main__':
    db_path = path_join('db', 'XiaMiShu.db')
    d = db_query(db_path)
