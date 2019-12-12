import requests
import configparser
import redis
import json
import MySQLdb

config = configparser.ConfigParser()
config.read('config.ini')

NODE_IP = config.get('nano', 'node_ip')

CONVERT_MULTIPLIER = {
    'nano': 1000000000000000000000000000000,
    'banano': 100000000000000000000000000000
}

# DB connection settings
DB_HOST = config.get('mysql', 'host')
DB_USER = config.get('mysql', 'user')
DB_PW = config.get('mysql', 'password')
DB_SCHEMA = config.get('mysql', 'schema')


balance_data = {'action': 'account_history', 'account': 'nano_1xmastreedxwfhpktqxppwgwwhdx1p6hiskpw7jt8g5y19khyy38axg4tohm', 'count': '10000'}
balance_data_json = json.dumps(balance_data)
r = requests.post(NODE_IP, data=balance_data_json)
balance_return = r.json()

db = MySQLdb.connect(host=DB_HOST, port=3306, user=DB_USER, passwd=DB_PW, db=DB_SCHEMA, use_unicode=True,
                        charset="utf8mb4")
db_cursor = db.cursor()
db_cursor.execute("drop table if exists xmas_donations;")
db_cursor.execute("CREATE TABLE `xmas`.`xmas_donations` ( "
    "`id` INT NOT NULL AUTO_INCREMENT, "
    " `address` VARCHAR(80) NOT NULL, "
    " `amount` VARCHAR(100) NOT NULL, "
    " PRIMARY KEY (`id`));"
)
for tx in balance_return['history']:
    if tx['type'] == 'receive':
        amount = round((float(tx['amount']) / CONVERT_MULTIPLIER['nano']), 8)
        db_cursor.execute("insert into xmas_donations (address, amount) VALUES (%s, %s);", [tx['account'], amount])
        db.commit()


db_cursor.close()
