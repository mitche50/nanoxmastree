#!/root/nanoxmastree/venv/bin/python3

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

def subscription(topic: str, ack: bool=False, options: dict=None):
    data = {'action': 'subscribe', 'topic': topic, 'ack': ack}
    if options is not None:
        data['options'] = options
    return data

# async def redis_subscribe(p):
#     p.subscribe('AnimationProcessing', )
#     p.subscribe('PendingAnimations')

#     while True:
#         message = p.get_message()

#         if message and message['type'] == 'message':
#             json_message = json.loads(message['data'].decode('utf-8'))


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
                print(message)
                if topic == "confirmation" and message['block']['subtype'] == 'send':
                    # We send a message to the redis pub sub to be handled by the client.
                    ps_message = {'sender': message['account'], 'amount': message['amount']}
                    ps_string = json.dumps(ps_message)
                    r.publish('NanoXmasTree', ps_string)
                    r.lpush("animations", ps_string)


try:
    asyncio.get_event_loop().run_until_complete(main())
except KeyboardInterrupt:
    pass
except ConnectionRefusedError:
    print("Error connecting to websocket server")

