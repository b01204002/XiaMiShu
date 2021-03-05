# coding=utf-8

from Utility.LittleTool import path_join, read_json
from Utility.DB import db_query

db_path = path_join('db', 'XiaMiShu.db')
d = db_query(db_path)

OPERATION_TYPE = {
    '後台管理': '後台管理',
    'local': 'local',
    'B5': 'B5',
    '年會': '年會',
    'UBP': 'UBP',
    '新人加盟': '新人加盟'
}

def insert_operation():
    operation = read_json(path_join('cfg', 'operation.json'))
    for o_item in operation:
        name = o_item.get('name', '')
        date = o_item.get('date', '')
        cost = o_item.get('cost', 0)
        price = o_item.get('price', 0)
        type = '產品課'
        for o_name, o_type in OPERATION_TYPE.items():
            if o_name in name:
                type = o_type
        d.insert_operation(date, name, type, cost, price)

def insert_customer():
    customer = read_json(path_join('cfg', 'customers.json'))
    for name, c_item in customer.items():
        nick_name = c_item.get('nick_name', [])
        phone = c_item.get('phone', '')
        address = c_item.get('address', '')
        postal_code = c_item.get('postal_code', '')
        birthday = c_item.get('birthday', '')
        d.insert_customer(name, nick_name, birthday, phone, address, postal_code)

def insert_BV_product():
    BV_product = read_json(path_join('cfg', 'BV_products.json'))
    for name, BV_item in BV_product.items():
        nick_name = BV_item.get('nick_name', [])
        picture = BV_item.get('img', '')
        cost = BV_item.get('cost', 0)
        exp_price = BV_item.get('price', 0)
        BV = BV_item.get('BV', 0)
        if not (cost and exp_price and BV):
            print(f'{name}, {cost}, {exp_price}, {BV}')
        d.insert_BV_product(name, nick_name, picture, cost, exp_price, BV)

def insert_IBV_store():
    IBV_store = read_json(path_join('cfg', 'IBV_stores.json'))
    for name, s_item in IBV_store.items():
        nick_name = s_item.get('nick_name', [])
        IBV = s_item.get('IBV', 0.0)
        if not IBV:
            print(name, IBV)
        d.insert_IBV_store(name, nick_name, IBV)

def insert_BV_order():
    BV_order = read_json(path_join('cfg', 'BV_orders.json'))
    for BV_o in BV_order:
        for customer_name, o_item in BV_o.get('customer', dict()).items():
            customer_idx = d.select_customer_idx(customer_name)
            order_date = BV_o.get('date', '')
            purchase_date = BV_o.get('date', '')
            delivery_date = o_item.get('delivery_date', '')
            cost = o_item.get('cost', 0)
            price = o_item.get('price', 0)
            products = o_item.get('products', dict())
            d.insert_BV_order(customer_idx[0], order_date, purchase_date, delivery_date, products, cost, price)


if __name__ == '__main__':
    insert_BV_order()