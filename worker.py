import redis
import json
import time

r = redis.StrictRedis(host='localhost', port=6379) 

if __name__ == '__main__':
    processing = False

    while True:
        if r.llen('XmasQueue') > 0:
            message_list = r.lrange('XmasQueue', 0, 10)
            message_data = r.lpop('XmasQueue')
            json_data = json.loads(message_data)
            print(message_list)
            # We will send the message_list to the web server so it can display the correct information
            # This is a dummy sleep task to simulate an animation
            print(f'Received notification that {json_data["sender"]} sent {json_data["amount"]} to the christmas tree account from redis queue')
            print('sleeping...')
            time.sleep(15)
