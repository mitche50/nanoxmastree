#!/root/nanoxmastree/venv/bin/python3

from decimal import Decimal

import asyncio
import configparser
import json
import redis
import requests
import websockets

# Read config and parse constants
config = configparser.ConfigParser()
config.read('config.ini')

WS_HOST = config.get('ws', 'host')
WS_PORT = config.get('ws', 'port')
TREE_ACCOUNT = config.get('nano', 'account')
REDIS_HOST = config.get('redis', 'host')
REDIS_PORT = config.get('redis', 'port')
REDIS_PW = config.get('redis', 'pw')
NODE_IP = config.get('nano', 'node_ip')

CONVERT_MULTIPLIER = {
    'nano': 1000000000000000000000000000000,
    'banano': 100000000000000000000000000000
}

def subscription(topic: str, ack: bool=False, options: dict=None):
    data = {'action': 'subscribe', 'topic': topic, 'ack': ack}
    if options is not None:
        data['options'] = options
    return data


def get_fiat_conversion(symbol, crypto_currency, fiat_amount):
    """
    Get the current fiat price conversion for the provided fiat:crypto pair
    """
    
    fiat = symbol.lower()
    crypto_currency = crypto_currency.lower()
    post_url = 'https://api.coingecko.com/api/v3/coins/{}'.format(crypto_currency)
    try:
        # Retrieve price conversion from API
        response = requests.get(post_url)
        response_json = json.loads(response.text)
        price = Decimal(response_json['market_data']['current_price'][fiat])
        # Find value of 0.01 in the retrieved crypto
        penny_value = Decimal(0.01) / price
        # Find precise amount of the fiat amount in crypto
        precision = 1
        crypto_value = Decimal(fiat_amount) * price
        # Find the precision of 0.01 in crypto
        crypto_convert = precision * penny_value
        while Decimal(crypto_convert) < 1:
            precision *= 10
            crypto_convert = precision * penny_value
        # Round the expected amount to the nearest 0.01
        temp_convert = crypto_value * precision
        temp_convert = str(round(temp_convert))
        final_convert = Decimal(temp_convert) / Decimal(str(precision))

        return final_convert
    except Exception as e:
        print("Exception converting fiat price to crypto price")
        print("{}".format(e))
        raise e


def get_balance(account: str):
    balance_data = {'action': 'account_balance', 'account': account}
    balance_data_json = json.dumps(balance_data)
    r = requests.post(NODE_IP, data=balance_data_json)
    balance_return = r.json()
    balance = round((float(balance_return['balance']) / CONVERT_MULTIPLIER['nano']) + (float(balance_return['pending'])) / CONVERT_MULTIPLIER['nano'], 4)
    gbp_amount = get_fiat_conversion('gbp', 'nano', balance)

    return str(balance), str(gbp_amount)


async def main():
    # Set up the redis pub sub
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PW)
    p = r.pubsub()

    options = {'accounts': [TREE_ACCOUNT]}

    async with websockets.connect("ws://{}:{}".format(WS_HOST, WS_PORT)) as websocket:
        await websocket.send(json.dumps(subscription("confirmation", ack=True, options=options)))
    
        while 1:
            rec = json.loads(await websocket.recv())
            topic = rec.get("topic", None)
            if topic:
                message = rec["message"]
                if topic == "confirmation" and message['block']['subtype'] == 'send': # and Decimal(message['amount']) >= (CONVERT_MULTIPLIER['nano']):
                    # We send a message to the redis pub sub to be handled by the client.
                    amount = str(Decimal(message['amount']) / CONVERT_MULTIPLIER['nano'])
                    print(amount)
                    balance, gbp_amount = get_balance(TREE_ACCOUNT)
                    score_check = r.zrange("top-donations", 0, 9, withscores=True)
                    print(score_check)
                    if len(score_check) < 10:
                        r.zadd("top-donations", {message['account']: amount})
                    elif float(amount) > float(score_check[0][1]):
                        r.zremrangebyrank("top-donations", 0, 0)
                        r.zadd("top-donations", {message['account']: amount})

                    r.set('donations', balance)
                    r.set('donations-fiat', gbp_amount)
                    ps_message = {'sender': message['account'], 'amount': amount}
                    ps_string = json.dumps(ps_message)
                    r.rpush("animations", ps_string)

                    message_list = r.lrange('animations', 0, 9)
                    message_json_list = []
                    for message in message_list:
                        message_json_list.append(message.decode('utf-8'))
                    
                    message_list_str = json.dumps(message_json_list)
                    r.publish('PendingAnimations', message_list_str)
                    


try:
    asyncio.get_event_loop().run_until_complete(main())
except KeyboardInterrupt:
    pass
except ConnectionRefusedError:
    print("Error connecting to websocket server")

