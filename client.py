import asyncio
import json
import redis


async def main():
    r = redis.StrictRedis(host='localhost', port=6379) 
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