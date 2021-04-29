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

    def connect_db(self):
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        return conn

    def close_connection(self):
        with self._locker:
            if self.conn:
                self.conn.close()
                self.conn = None

    def _execute_query(self, query='', action=SELECT):
        data = []
        try:
            with self._locker:
                if self.conn is None:
                    self.conn = self.connect_db()
                if self.conn:
                    c = self.conn.cursor()
                    c.execute(query)
                    data = c.fetchall()
                    if action == INSERT:
                        data = [c.lastrowid]
                    if action != SELECT:
                        self.conn.commit()
            self.close_connection()

        except BaseException as e:
            self.close_connection()
            self.logger.exception(f'While executing query:\n{query}\n'
                                  f'Other Exception:\n{e}')
            return False, []
        return True, data
    
    def select_one(self, query):
        if not query:
            self.logger.warning(f'[select_one] query is empty!')
            return False, 'query is empty'
        
        success, result = self._execute_query(query=query, action=SELECT)
        if not success:
            return False, 'query failed. query:\n{query}\n'
        if len(result) == 0:
            return False, 'no result!'
        if len(result) > 1:
            return False, 'too many result!'
        return True, result[0]

    def select_many(self, query):
        if not query:
            self.logger.warning(f'[select_many] query is empty!')
            return False, 'query is empty'
        
        success, result = self._execute_query(query=query, action=SELECT)
        if not success:
            return False, f'query failed. query:\n{query}\n'
        if len(result) == 0:
            return False, 'no result!'
        return True, result

    def insert_one(self, query):
        if not query:
            self.logger.warning(f'[insert_one] query is empty!')
            return False, 'query is empty'
        success, result = self._execute_query(query=query, action=INSERT)
        if not success:
            return False, f'query failed. query:\n{query}\n'
        return True, result[0]
    
    def update_one(self, query):
        if not query:
            self.logger.warning(f'[update_one] query is empty!')
            return False, 'query is empty'
        success, result = self._execute_query(query=query, action=UPDATE)
        if not success:
            return False, f'query failed. query:\n{query}\n'
        return True, result
    
    def delete_one(self, query):
        if not query:
            self.logger.warning(f'[delete_one] query is empty!')
            return False, 'query is empty'
        success, result = self._execute_query(query=query, action=DELETE)
        if not success:
            return False, f'query failed. query:\n{query}\n'
        return True, result








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

    def insert_IBV_store(self, name:str, nick_name:list, IBV:float, online:bool):
        online = int(online)
        query = f"INSERT INTO IBV_store (name, IBV, online) VALUES (\'{name}\', \'{IBV}\', \'{int(online)}\');"
        IBV_store_idx = self._execute_query(query, action=INSERT)

        for nick in nick_name + [name]:
            query = f"INSERT INTO IBV_store_nickname (IBV_store_idx, nick_name)" \
                f"VALUES (\'{IBV_store_idx[0]}\', \'{nick}\');"
            self._execute_query(query, action=INSERT)
        return

    def select_customer_idx(self, name):
        query = f"SELECT customer_idx FROM customer_nickname WHERE nick_name == \'{name}\'"
        q, idx = self._execute_query(query, action=SELECT)
        if not q:
            return [0]
        return idx[0][0]

    def select_BV_info(self, name):
        idx = 0
        BV = 0
        cost = 0
        exp_price = 0
        query = f"SELECT BV_product_idx FROM BV_product_nickname WHERE nick_name == \'{name}\'"
        success, q = self._execute_query(query, action=SELECT)
        if not q:
            return (idx, BV, cost, exp_price)

        query = f"SELECT idx, BV, cost, exp_price FROM BV_product WHERE idx == {q[0][0]}"
        success, q = self._execute_query(query, action=SELECT)
        if not q:
            return (idx, BV, cost, exp_price)
        return q[0]

    def insert_BV_order_product(self, BV_order_idx, BV_product_idx, amount, details):
        query = f"INSERT INTO BV_order_product (BV_order_idx, BV_product_idx, amount, details) " \
            f"VALUES ({BV_order_idx}, {BV_product_idx}, {amount}, \'{details}\');"
        return self._execute_query(query, action=INSERT)

    def insert_BV_order(self, customer:str, order_date:str, products:list):
        customer_idx = self.select_customer_idx(customer)
        if not customer_idx:
            self.logger.warning(f'No customer! name = {customer}')
            return 0

        total_BV = 0
        total_cost = 0
        total_exp_price = 0
        products_list = []
        for p in products:
            p_name = p.get('product_name', '')
            p_amount = p.get('amount', 1)
            p_idx, p_BV, p_cost, p_exp_price = self.select_BV_info(p_name)
            if not p_idx:
                self.logger.warning(f'No product! name = {p_name}')
                return 0
            total_BV += p_BV * p_amount
            total_cost += p_cost * p_amount
            total_exp_price += p_exp_price * p_amount
            products_list.append((p_idx, p_amount, p.get('detail', '')))

        query = f"INSERT INTO BV_order (customer_idx, order_date, BV, cost, exp_price) " \
            f"VALUES (\'{customer_idx}\', \'{order_date}\', \'{total_BV}\', \'{total_cost}\', \'{total_exp_price}\');"
        q = self._execute_query(query, action=INSERT)
        if not q:
            self.logger.error(f'insert_BV_order failed!')
            return 0

        for p in products_list:
            q = self.insert_BV_order_product(q[0], p[0], p[1], p[2])
            if not q:
                self.logger.warning('insert_BV_order_product failed.')

        self.logger.debug(f'insert_BV_order done: customer={customer}, order_date={order_date}')
        return

    def select_IBV_store(self, name:str):
        query = f"SELECT IBV_store_idx FROM IBV_store_nickname WHERE nick_name == \'{name}\'"
        q = self._execute_query(query, action=SELECT)
        if not q:
            return 0, 0.0
        IBV_store_idx = q[0][0]

        query = f"SELECT IBV FROM IBV_store WHERE idx == {IBV_store_idx}"
        q = self._execute_query(query, action=SELECT)
        if not q:
            return 0, 0.0
        return IBV_store_idx, q[0][0]

    def insert_IBV_purchase(self, IBV_store:str, date:str, cost:int, product:str):
        IBV_store_idx, store_IBV = self.select_IBV_store(IBV_store)
        if not IBV_store_idx:
            self.logger.warning(f'No IBV_store! IBV_store = {IBV_store}')
            return 0

        exp_IBV = cost / 30 * store_IBV / 100

        query = f"INSERT INTO IBV_purchase (IBV_store_idx, purchase_date, product, cost, exp_IBV) " \
            f"VALUES (\'{IBV_store_idx}\', \'{date}\', \'{product}\', \'{cost}\', \'{exp_IBV}\');"
        q = self._execute_query(query, action=INSERT)
        if not q:
            self.logger.error(f'insert_IBV_purchase failed!')
            return 0
        self.logger.debug(f'insert_IBV_purchase done: IBV_store={IBV_store}, purchase_date={date}')
        return q[0]

    def insert_IBV_order(self, IBV_purchase_idx:int, customer:str, product:str, exp_price:int):
        customer_idx = self.select_customer_idx(customer)
        if not customer_idx:
            self.logger.warning(f'No customer! name = {customer}')
            return 0

        query = f"INSERT INTO IBV_order (IBV_purchase_idx, customer_idx, product, exp_price) " \
            f"VALUES (\'{IBV_purchase_idx}\', \'{customer_idx}\', \'{product}\', \'{exp_price}\');"
        q = self._execute_query(query, action=INSERT)
        if not q:
            self.logger.error(f'insert_IBV_order failed!')
            return 0
        self.logger.debug(f'insert_IBV_order done: customer={customer} product={product}')
        return q[0]

    def update_IBV_purchase(self, IBV_purchase_idx, IBV):
        query = f"UPDATE IBV_purchase SET IBV={IBV} WHERE idx = \'{IBV_purchase_idx}\'"
        return self._execute_query(query, action=UPDATE)

    def update_IBV_order(self, IBV_order_idx, delivery_date, price):
        query = f"UPDATE IBV_order SET delivery_date=\'{delivery_date}\', price={price}" \
            f" WHERE idx = \'{IBV_order_idx}\'"
        return self._execute_query(query, action=UPDATE)

    def _get_BV_order_sum(self, start:str, end:str):
        query = f'SELECT SUM(cost), SUM(price), SUM(BV) FROM BV_order WHERE purchase_date BETWEEN \"{start}\" AND \"{end}\"'
        return self._execute_query(query, action=SELECT)[0]

    def _get_BV_order_self_use_cost(self, start:str, end:str):
        query = f'SELECT SUM(cost) FROM BV_order WHERE customer_idx < 4 AND purchase_date BETWEEN \"{start}\" AND \"{end}\"'
        return self._execute_query(query, action=SELECT)[0][0]

    def _get_IBV_purchase_sum(self, start, end):
        query = f'SELECT SUM(cost), SUM(exp_IBV), SUM(IBV) FROM IBV_purchase WHERE purchase_date BETWEEN \"{start}\" AND \"{end}\"'
        return self._execute_query(query, action=SELECT)[0]

    def _get_IBV_order_sum(self, start, end):
        query = f'SELECT SUM(IBV_order.exp_price), SUM(IBV_order.price) FROM IBV_purchase ' \
            f'INNER JOIN IBV_order ON IBV_purchase.idx = IBV_order.IBV_purchase_idx ' \
            f'WHERE IBV_purchase.purchase_date BETWEEN \"{start}\" AND \"{end}\"'
        return self._execute_query(query, action=SELECT)[0]

    def _get_order_summary(self, start, end):
        BV_order_cost, BV_order_price, BV_order_BV = self._get_BV_order_sum(start, end)
        BV_order_self_use_cost = self._get_BV_order_self_use_cost(start, end)
        
        IBV_purchase_cost, IBV_purchase_exp_IBV, IBV_purchase_IBV = self._get_IBV_purchase_sum(start, end)
        IBV_order_exp_price, IBV_order_price = self._get_IBV_order_sum(start, end)

        summary = {
            'BV': {
                'self_use_cost': BV_order_self_use_cost,
                'cost': BV_order_cost - BV_order_self_use_cost,
                'price': BV_order_price,
                'profit': BV_order_price - (BV_order_cost - BV_order_self_use_cost),
                'BV': BV_order_BV
            },
            'IBV': {
                'self_use_cost': IBV_purchase_cost - IBV_order_exp_price,
                'cost': IBV_order_exp_price,
                'price': IBV_order_price,
                'profit': IBV_order_price - IBV_order_exp_price,
                'exp_IBV': IBV_purchase_exp_IBV,
                'IBV': IBV_purchase_IBV
            },
            'total': {
                'self_use_cost': BV_order_self_use_cost + IBV_purchase_cost - IBV_order_exp_price,
                'business_cost': BV_order_cost - BV_order_self_use_cost + IBV_order_exp_price,
                'price': BV_order_price + IBV_order_price,
                'profit': BV_order_price - (BV_order_cost - BV_order_self_use_cost) + IBV_order_price - IBV_order_exp_price
            }
        }
        return summary

    def monthly_order_summary(self, year:int, month:int):
        start = f'{year}-{month:02}-01'
        end = f'{year}-{month+1:02}-01' if month < 12 else f'{year+1}-01-01'
        return self._get_order_summary(start, end)
    
    def quarterly_order_summary(self, year:int, quarter:int=0):
        mapping = {
            1: [1, 2, 3],
            2: [4, 5, 6],
            3: [7, 8, 9],
            4: [10, 11, 12]
        }
        this_month = datetime.now().month
        if not quarter or quarter > 4:
            for q, m_list in mapping.items():
                if this_month in m_list:
                    quarter = q
                    break 
        start = f'{year}-{mapping[quarter][0]:02}-01'
        end = f'{year}-{mapping[quarter][-1]:02}-01' if quarter != 4 else f'{year+1}-01-01'
        return self._get_order_summary(start, end)
        


if __name__ == '__main__':
    db_path = path_join('db', 'XiaMiShu.db')
    d = db_query(db_path)
    # r = d.monthly_order_summary(2021, 1)
    # print(r)
    # r = d.quarterly_order_summary(2021, 1)
    # print(r)

    