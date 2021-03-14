# coding=utf-8

from Utility.LittleTool import path_join, read_json
from Utility.DB import db_query
from datetime import datetime

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

def insert_operation(name:str, date='', cost=0, price=0):
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    type = '產品課'
    for o_name, o_type in OPERATION_TYPE.items():
        if o_name in name:
            type = o_type
    operation_idx = d.insert_operation(date, name, type, cost, price)

def insert_customer(name:str, nick_name=[], phone='', address='', postal_code='', birthday=''):
    customer_idx = d.insert_customer(name, nick_name, birthday, phone, address, postal_code)

def insert_BV_product(name:str, nick_name=[], picture='', cost=0, exp_price=0, BV=0.0):
    BV_product_idx = d.insert_BV_product(name, nick_name, picture, cost, exp_price, BV)

def insert_IBV_store(name:str, IBV=0.0, online=True, nick_name=[]):
    IBV_store_idx = d.insert_IBV_store(name, nick_name, IBV, online)

def insert_BV_order(customer_name, products, order_date=''):
    if not order_date:
        order_date = datetime.now().strftime('%Y-%m-%d')
    BV_order_idx = d.insert_BV_order(customer_name, order_date, products)

def insert_IBV_order(store_name, product_name, cost, customer_info):
    date = datetime.now().strftime('%Y-%m-%d')
    IBV_purchase_idx = d.insert_IBV_purchase(store_name, date, cost, product_name)
    if not IBV_purchase_idx:
        return

    for info in customer_info:
        customer = info.get('customer', '')
        exp_price = info.get('exp_price', 0)
        product = info.get('product', product_name)
        IBV_order_idx = d.insert_IBV_order(IBV_purchase_idx, customer, product, exp_price)

def update_IBV_purchase_IBV(IBV_purchase_idx, IBV):
    d.update_IBV_purchase(IBV_purchase_idx, IBV)

def update_IBV_order_price(IBV_order_idx, price):
    date = datetime.now().strftime('%Y-%m-%d')
    d.update_IBV_order(IBV_order_idx, date, price)



if __name__ == '__main__':
    insert_customer('陳文婉', ['陳婉婉'], '0937888481', '台北市中正區臨沂街63巷9號4樓', '110')
    insert_IBV_store('普麗斯', 33.0)
    customer_info = [
        {
            'customer': '陳文婉',
            'exp_price': 1250
        }
    ]
    insert_IBV_order('普麗斯', '牙齒美白7-9天', 1150, customer_info)