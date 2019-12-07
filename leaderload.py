import requests
import configparser
import redis
import json

config = configparser.ConfigParser()
config.read('config.ini')

NODE_IP = config.get('nano', 'node_ip')

CONVERT_MULTIPLIER = {
    'nano': 1000000000000000000000000000000,
    'banano': 100000000000000000000000000000
}

balance_data = {'action': 'account_history', 'account': 'nano_1xmastreedxwfhpktqxppwgwwhdx1p6hiskpw7jt8g5y19khyy38axg4tohm', 'count': '10000'}
balance_data_json = json.dumps(balance_data)
r = requests.post(NODE_IP, data=balance_data_json)
balance_return = r.json()

REDIS_HOST = config.get('redis', 'host')
REDIS_PORT = config.get('redis', 'port')
REDIS_PW = config.get('redis', 'pw')

client = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PW)

for tx in balance_return['history']:
    if tx['type'] == 'receive':
        score_check = client.zrange("top-donations", 0, 9, withscores=True)
        amount = round((float(tx['amount']) / CONVERT_MULTIPLIER['nano']), 8)
        

        if len(score_check) < 10:
            print("no score, adding...")
            data = {tx['account']: amount}
            print(data)
            client.zadd("top-donations", data)
        elif float(amount) > float(score_check[0][1]):
            print("score is higher, adding and removing ...")
            client.zremrangebyrank("top-donations", 0, 0)
            data = {tx['account']: amount}
            client.zadd("top-donations", data)
        else:
            print("amount: {} - redis: {}".format(float(amount),float(score_check[0][1])))
