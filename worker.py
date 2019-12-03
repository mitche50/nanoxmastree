#!/home/pi/nanoxmastree/venv/bin/python3

import redis
import json
import time
import configparser

from single import purple_cycle_successive, purple_cycle, rainbow_colors, brightness_decrease, test_pixels, one_color_sparkle, rainbow_cycle, rainbow_cycle_successive, appear_from_back, rainbow_colors_alt, alt_red_green, snow, pacman_chase, nano_sparkles
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
            print(f'Received notification that {json_data["sender"]} sent {json_data["amount"]} to the christmas tree account from redis queue')
            pixels.clear()
            pixels.show()

            adjusted_amount = json_data["amount"].replace("0", "")

            if adjusted_amount[-1] == "1":
                rainbow_colors(pixels, wait=0.05)
                purple_cycle(pixels, wait=0.01)

            elif adjusted_amount[-1] == "2":
                one_color_sparkle(pixels, wait=0.05)
                purple_cycle(pixels, wait=0.01)

            elif adjusted_amount[-1] == "3":
                rainbow_cycle(pixels, wait=0.05)
                purple_cycle(pixels, wait=0.01)

            elif adjusted_amount[-1] == "4":
                rainbow_cycle_successive(pixels, wait=0.05)
                purple_cycle(pixels, wait=0.01)

            elif adjusted_amount[-1] == "5":
                nano_sparkles(pixels, wait=0.1)
                purple_cycle(pixels, wait=0.01)

            elif adjusted_amount[-1] == "6":
                alt_red_green(pixels, wait=1)
                purple_cycle(pixels, wait=0.01)

            elif adjusted_amount[-1] == "7":
                snow(pixels, wait=0.5)
                purple_cycle(pixels, wait=0.01)

            elif adjusted_amount[-1] == "8":
                pacman_chase(pixels, wait=0.1)
                purple_cycle(pixels, wait=0.01)

            # 5 = rainbow sparkle
            else:
                purple_cycle_successive(pixels, wait=0.01)
                purple_cycle(pixels, wait=0.01)
        
            # brightness_decrease(pixels)
