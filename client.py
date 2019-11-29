#!/home/pi/nanoxmastree/venv/bin/python3

import asyncio
import json
import redis
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

REDIS_HOST = config.get('redis', 'host')
REDIS_PORT = config.get('redis', 'port')
REDIS_PW = config.get('redis', 'pw')


async def main():
    r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PW) 
    p = r.pubsub()

    p.subscribe('NanoXmasTree')

    while True:
        message = p.get_message()

        if message and message['type'] == 'message':
            json_data = json.loads(message['data'])
            r.lpush('XmasQueue', message['data'])
            print(f'Received notification that {json_data["sender"]} sent {json_data["amount"]} to the christmas tree account')

try:
    asyncio.get_event_loop().run_until_complete(main())
except KeyboardInterrupt:
    pass
except Exception as e:
    print(e)
    pass
