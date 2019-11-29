import redis
import json
import time
import configparser

from single import rainbow_cycle_successive, rainbow_cycle, brightness_decrease
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI
import RPi.GPIO as GPIO

config = configparser.ConfigParser()
config.read('config.ini')

REDIS_HOST = config.get('redis', 'host')
REDIS_PORT = config.get('redis', 'port')
REDIS_PW = config.get('redis', 'pw')

# Configure the count of pixels:
PIXEL_COUNT = 250
 
# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0

pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)

r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PW) 

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
            pixels.clear()
            pixels.show()

            rainbow_cycle_successive(pixels, wait=0.01)
            rainbow_cycle(pixels, wait=0.01)
        
            brightness_decrease(pixels)