#!/root/nanoxmastree/venv/bin/python3

from decimal import Decimal

import asyncio
import configparser
import json
import redis
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

CONVERT_MULTIPLIER = {
    'nano': 1000000000000000000000000000000,
    'banano': 100000000000000000000000000000
}

def subscription(topic: str, ack: bool=False, options: dict=None):
    data = {'action': 'subscribe', 'topic': topic, 'ack': ack}
    if options is not None:
        data['options'] = options
    return data

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

