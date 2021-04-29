# coding=utf-8

from Utility.LittleTool import path_join, read_json
from Utility.logger import initial_log
from Utility.DB import db_query
from datetime import datetime

logger = initial_log('db_operator')
db_path = path_join('db', 'XiaMiShu.db')
db = db_query(db_path)

class customer:
    def __init__(self):
        pass

    def create_one(self, name, nickname=[], phone='', postal_code='', address='', birthday=''):
        query = f"SELECT customer_idx FROM customer_nickname WHERE nick_name == \'{name}\'"
        success, result = db.select_one(query)
        if success:
            logger.warning(f'[customer.create_one] name already exist. name: {name}')
            return False

        query = f"INSERT INTO customer (name, birthday, phone, address, postal_code)" \
            f"VALUES (\'{name}\', \'{birthday}\', \'{phone}\', \'{address}\', \'{postal_code}\');"
        success, result = db.insert_one(query)
        if not success:
            logger.error(f'[customer.create_one] customer insert failed. msg: {reuslt}')
            return False

        customer_idx = result
        for nick in nickname + [name]:
            query = f"INSERT INTO customer_nickname (customer_idx, nick_name)" \
                f"VALUES (\'{customer_idx}\', \'{nick}\');"
            success, result = db.insert_one(query)
            if not success:
                logger.warning(f'[customer.create_one] nickname insert failed. msg: {result}')

        logger.debug(f'[customer.create_one] create customer success. name: {name} => idx: {customer_idx}')
        return customer_idx
    
    def get_one_by_name(self, nickname):
        query = f"SELECT C.idx, C.name, C.phone, C.postal_code, C.address , C.birthday " \
            f"FROM customer C " \
            f"INNER JOIN customer_nickname CN ON C.idx=CN.customer_idx " \
            f"WHERE CN.nick_name == \'{nickname}\';"
        success, result = db.select_one(query)
        if not success:
            logger.error(f'[customer.get_one_by_name] failed msg: {result}')
            return False
        return result

    def update_one(self, nick, name='', nickname=[], phone='', postal_code='', address='', birthday=''):
        pass
        # query = f"UPDATE customer "


class BV_order:
    def __init__(self):
        pass

    def create_product(self, name, nickname=[], picture='', cost=0, exp_price=0, BV=0.0):
        query = f'SELECT BV_product_idx FROM BV_product_nickname WHERE nick_name == \'{name}\''
        success, result = db.select_one(query)
        if success:
            logger.warning(f'[BV_order.create_product] name already exist. name: {name}')
            return False

        query = f"INSERT INTO BV_product (name, picture, cost, exp_price, BV)" \
            f"VALUES (\'{name}\', \'{picture}\', \'{cost}\', \'{exp_price}\', \'{BV}\');"
        success, result = db.insert_one(query)
        if not success:
            logger.error(f'[BV_order.create_product] product insert failed. msg: {reuslt}')
            return False

        BV_product_idx = result
        for nick in nickname+[name]:
            query = f"INSERT INTO BV_product_nickname (BV_product_idx, nick_name)" \
                f"VALUES (\'{BV_product_idx}\', \'{nick}\');"
            success, result = db.insert_one(query)
            if not success:
                logger.warning(f'[BV_order.create_product] create nickname failed. msg: {result}')

        logger.debug(f'[BV_order.create_product] create BV_product success. name: {name} => idx: {BV_product_idx}')
        return BV_product_idx
    
    def get_product_by_name(self, nickname):
        query = f"SELECT P.idx, P.name, P.picture, P.cost, P.exp_price, P.BV " \
            f"FROM BV_product P " \
            f"INNER JOIN BV_product_nickname PN ON P.idx=PN.BV_product_idx " \
            f"WHERE PN.nick_name == \'{nickname}\';"
        success, result = db.select_one(query)
        if not success:
            logger.error(f'[BV_order.get_product_by_name] failed. msg: {result}')
            return False
        return result
    
    def update_product(self, nick, name='', nickname=[], picture='', cost=0, exp_price=0, BV=0.0):
        pass

    def create_order(self, customer, products:list):
        total_BV = 0
        total_cost = 0
        total_exp_price = 0
        products_list = []
        for p in products:
            p_name = p.get('product_name', '')
            p_amount = p.get('amount', 1)
            p_info = self.get_product_by_name(p_name)
            if not p_info:
                self.logger.warning(f'No product! name = {p_name}')
                return 0
            total_BV += p_info[5] * p_amount
            total_cost += p_info[3] * p_amount
            total_exp_price += p_info[4] * p_amount
            products_list.append((p_info[0], p_amount, p.get('detail', '')))
        
        query = f"INSERT INTO BV_order (customer_idx, purchase_date, BV, cost, exp_price) " \
            f"SELECT customer_idx, \'{order_date}\', \'{total_BV}\', \'{total_cost}\', \'{total_exp_price}\' " \
            f"FROM customer_nickname CN WHERE CN.nick_name = \'{name}\';"
        success, result = db.insert_one(query)
        if not success:
            logger.error(f'[BV_order.create_order] insert BV_order failed. msg: {result}')
            return False
        
        BV_order_idx = result
        for p in products_list:
            query = f"INSERT INTO BV_order_product (BV_order_idx, BV_product_idx, amount, details) " \
                f"VALUES ({BV_order_idx}, {p[0]}, {p[1]}, \'{p[2]}\');"
            success, result = db.insert_one(query)
            if not success:
                logger.warning(f'[BV_order.create_order] insert BV_order_product failed. msg: {result}')
        
        logger.debug(f'[BV_order.create_order] success! customer: {customer} => BV_order_idx: {BV_order_idx}')
        return BV_order_idx
    
    def get_BV_order(self, customer='', date_range=[], unpaid=False):
        query = f"SELECT C.name, BV.purchase_date, BV.BV, BV.cost, BV.exp_price, BV.price FROM BV_order AS BV " \
            f"INNER JOIN customer AS C ON C.idx = BV.customer_idx "
        if customer:
            query += f"INNER JOIN customer_nickname AS CN ON CN.customer_idx = BV.customer_idx " \
                f"WHERE CN.nick_name = \'{customer}\' "
        if date_range:
            tmp = "AND" if "WHERE" in query else "WHERE"
            query += f"{tmp} BV.purchase_date BETWEEN \'{date_range[0]}\' AND \'{date_range[1]}\' "
        if unpaid:
            tmp = "AND" if "WHERE" in query else "WHERE"
            query += f"{tmp} BV.price IS NULL"
        
        success, result = db.select_many(query)
        if not success:
            logger.error(f'[BV_order.get_BV_order] failed. msg: {result}')
        return result

    def update_BV_order(self, BV_order_idx, customer='', products=[], price=0):
        pass

    def get_BV_info(self, date_range=[]):
        query = f"SELECT * FROM BV_order AS BV " \
            f"INNER JOIN customer AS C ON C.idx = BV.customer_idx WHERE BV.purchase_date BETWEEN \'{date_range[0]}\' AND \'{date_range[1]}\'"
        success, order_result = db.select_many(query)
        if not success:
            print(order_result)
            return

        query = f"SELECT * FROM BV_order_product AS BVOP " \
            f"INNER JOIN BV_product AS BVP ON BVOP.BV_product_idx = BVP.idx " \
            f"WHERE BVOP.BV_order_idx BETWEEN \'{order_result[0][0]-1}\' AND \'{order_result[-1][0]+1}\'"
        success, product_result = db.select_many(query)
        if not success:
            print(product_result)
            return

        result = [('日期', '客戶', '商品', 'amount', 'BV', 'cost', 'exp_price', 'total_price')]
        for order in order_result:
            for product in product_result:
                if order[0] == product[1]:
                    result.append((order[2], order[11], product[6], product[3], product[10], product[8], product[9], order[9]))
        for r in result:
            print(r)


class IBV_order:
    def __init__(self):
        pass

    def create_store(self, name, IBV:float, nickname=[], online=True):
        query = f'SELECT IBV_store_idx FROM IBV_store_nickname WHERE nick_name == \'{name}\''
        success, result = db.select_one(query)
        if success:
            logger.warning(f'[IBV_order.create_store] name already exist. name: {name}')
            return False

        online = int(online)
        query = f"INSERT INTO IBV_store (name, IBV, online) VALUES (\'{name}\', \'{IBV}\', \'{int(online)}\');"
        success, result = db.insert_one(query)
        if not success:
            logger.error(f'[IBV_order.create_store] store insert failed. msg: {reuslt}')
            return False

        IBV_store_idx = result
        for nick in nickname+[name]:
            query = f"INSERT INTO IBV_store_nickname (IBV_store_idx, nick_name)" \
                f"VALUES (\'{IBV_store_idx}\', \'{nick}\');"
            success, result = db.insert_one(query)
            if not success:
                logger.warning(f'[IBV_order.create_store] create nickname failed. msg: {result}')

        logger.debug(f'[IBV_order.create_store] create IBV_store success. name: {name} => idx: {IBV_store_idx}')
        return IBV_store_idx
    
    def get_store_by_name(self, nickname):
        query = f"SELECT S.idx, S.name, S.IBV, S.online " \
            f"FROM IBV_store S " \
            f"INNER JOIN IBV_store_nickname SN ON S.idx=SN.IBV_store_idx " \
            f"WHERE SN.nick_name == \'{nickname}\';"
        success, result = db.select_one(query)
        if not success:
            logger.error(f'[IBV_order.get_store_by_name] failed. msg: {result}')
            return False
        return result
    
    def update_store(self, nick, name='', nickname=[], IBV=0.0, online=None):
        pass

    def create_purchase_order(self, date, store, cost, order_info:list):
        query = f"INSERT INTO IBV_purchase (IBV_store_idx, purchase_date, cost, exp_IBV) " \
            f"SELECT SN.IBV_store_idx, \'{date}\', {cost}, {cost}*S.IBV/3000 " \
            f"FROM IBV_store AS S INNER JOIN IBV_store_nickname AS SN ON S.idx = SN.IBV_store_idx " \
            f"WHERE SN.nick_name = \'{store}\';"
        success, result = db.insert_one(query)
        if not success:
            logger.error(f'[IBV_order.create_purchase_order] insert IBV_purchase failed. msg: {result}')
            return False
        logger.debug(f'[IBV_order.create_purchase_order] insert IBV_purchase success! store: {store} => purchase_idx: {result}')

        IBV_purchase_idx = result
        for order in order_info:
            customer = order.get('customer', '')
            product_type = order.get('product_type', '')
            product = order.get('product', '')
            exp_price = order.get('exp_price', 0)
            self_cost = order.get('self_cost', 0)
            delivery_date = date if self_cost > 0 else ''
            query = f"INSERT INTO IBV_order (IBV_purchase_idx, customer_idx, product_type, product, delivery_date, exp_price, self_cost) " \
                f"SELECT {IBV_purchase_idx}, CN.customer_idx, \'{product_type}\', \'{product}\', \'{delivery_date}\', {exp_price}, {self_cost} " \
                f"FROM customer_nickname AS CN WHERE CN.nick_name=\'{customer}\';"
            success, result = db.insert_one(query)
            if not success:
                logger.error(f'[IBV_order.create_purchase_order] insert IBV_order failed. msg: {result}')
        
            logger.debug(f'[IBV_order.create_purchase_order] insert IBV_order success! customer: {customer} => order_idx: {result}')
        
        return IBV_purchase_idx

    def get_IBV_purchase(self, store='', date_range=[], noIBV=False):
        pass

    def get_IBV_order(self, customer='', date_range=[], unpaid=False):
        pass

    def get_IBV_info(self, date_range=[]):
        query = f"SELECT * FROM IBV_purchase AS IP " \
            f"INNER JOIN IBV_store AS IStore ON IP.IBV_store_idx = IStore.idx WHERE IP.purchase_date BETWEEN \'{date_range[0]}\' AND \'{date_range[1]}\'"
        success, purchase_result = db.select_many(query)
        if not success:
            print(purchase_result)
            return

        query = f"SELECT * FROM IBV_order AS IO " \
            f"INNER JOIN customer AS C ON C.idx = IO.customer_idx " \
            f"WHERE IO.IBV_purchase_idx BETWEEN \'{purchase_result[0][0]-1}\' AND \'{purchase_result[-1][0]+1}\'"
        success, order_result = db.select_many(query)
        if not success:
            print(order_result)
            return

        result = [('date', 'store', 'product', 'cost', 'IBV%', 'IBV', 'price', 'customer')]
        for purchase in purchase_result:
            idx = purchase[0]
            tmp = []
            price = 0
            for order in order_result:
                if idx == order[1]:
                    tmp.append(order[8])
                    if type(order[6]) == int:
                        price += order[6]
            result.append((purchase[2], purchase[8], purchase[3], purchase[4], purchase[9], purchase[6], price, tmp))
        
        for r in result:
            print(r)


        
            

class operation:
    def __init__(self):
        self.type_mapping = {
            '後台管理': '後台管理',
            'local': 'local',
            'B5': 'B5',
            '年會': '年會',
            'UBP': 'UBP',
            '新人加盟': '新人加盟'
        }


if __name__ == '__main__':
    # c = customer()
    # c_idx = c.create_one('測試用', phone='0912345678')
    # print(c_idx)

    # c_info = c.get_one_by_name('測試用')
    # print(c_info)

    # BV = BV_order()
    # p_info = BV.get_product_by_name('OPC')
    # print(p_info)

    # BV_orders = BV.get_BV_order(date_range=['2021-01-01', '2021-04-01'])
    # for BV in BV_orders:
    #     print(BV)

    BV = BV_order()
    BV.get_BV_info(['2019-10-01', '2020-01-01'])

    IBV = IBV_order()
    IBV.get_IBV_info(['2019-10-01', '2020-01-01'])


    # insert_customer('葉怡秀', ['辰勳媽媽'], '0931207236', '台北市內湖區康寧路一段195巷4弄1號3樓', '114')
    # insert_IBV_store('視鏡空間', 11.0)
    # customer_info = [
    #     {
    #         'customer': '媽媽',
    #         'exp_price': 800
    #     },
    #     {
    #         'customer': '艾利森',
    #         'exp_price': 0
    #     }
    # ]
    # insert_IBV_order('特力屋', '浴簾、錶帶、量杯', 930, customer_info)

    # products = [
    #     {
    #         'product_name': '魚油',
    #         'amount': 1
    #     }
    # ]
    # insert_BV_order('媽媽', products)

    print('DONE')