# Simple demo of of the WS2801/SPI-like addressable RGB LED lights.
import time, random
import RPi.GPIO as GPIO
 
# Import the WS2801 module.
import Adafruit_WS2801
import Adafruit_GPIO.SPI as SPI
 
 
# Configure the count of pixels:
PIXEL_COUNT = 250
 
# Alternatively specify a hardware SPI connection on /dev/spidev0.0:
SPI_PORT   = 0
SPI_DEVICE = 0
pixels = Adafruit_WS2801.WS2801Pixels(PIXEL_COUNT, spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE), gpio=GPIO)
 
 
# Define the wheel function to interpolate between different hues.
def wheel(pos):
    if pos < 85:
        return Adafruit_WS2801.RGB_to_color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Adafruit_WS2801.RGB_to_color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Adafruit_WS2801.RGB_to_color(0, pos * 3, 255 - pos * 3)

# Define rainbow cycle function to do a cycle of all hues.
def rainbow_cycle_successive(pixels, wait=0.1):
    for i in range(pixels.count()):
        # tricky math! we use each pixel as a fraction of the full 96-color wheel
        # (thats the i / strip.numPixels() part)
        # Then add in j which makes the colors go around per pixel
        # the % 96 is to make the wheel cycle around
        pixels.set_pixel(i, wheel(((i * 256 // pixels.count())) % 256) )
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def rainbow_cycle(pixels, wait=0.005):
    for j in range(256): # one cycle of all 256 colors in the wheel
        for i in range(pixels.count()):
            pixels.set_pixel(i, wheel(((i * 256 // pixels.count()) + j) % 256) )
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
# Define rainbow cycle function to do a cycle of all hues.
def purple_cycle_successive(pixels, wait=0.1):
    for i in range(pixels.count()):
        # tricky math! we use each pixel as a fraction of the full 96-color wheel
        # (thats the i / strip.numPixels() part)
        # Then add in j which makes the colors go around per pixel
        # the % 96 is to make the wheel cycle around
        pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color(89, 17, 88))# wheel(((i * 256 // pixels.count())) % 256) )
        pixels.show()
        print(i)
        if wait > 0:
            time.sleep(wait)

def background(pixels):
    for i in range(pixels.count()):
        pixels.set_pixel_rgb(i, 89, 17, 88)
    pixels.show()

def pacman_chase(pixels, wait=0.1):
    for i in range(10, pixels.count()):
        pixels.set_pixel_rgb( i - 8, 0,0,0   )
        pixels.set_pixel_rgb(i - 6, 255, 184, 82   )
        pixels.set_pixel_rgb(i - 4, 255, 184, 255   )
        pixels.set_pixel_rgb(i - 2, 0, 255, 255   )
        pixels.set_pixel_rgb(i, 255, 255, 0   )
        pixels.show()
        time.sleep(wait)


def one_color_sparkle(pixels, wait=0.05):
    count = 0
    while count <180:
        for i in range(pixels.count()):
            if random.getrandbits(1) == 1:
                pixels.set_pixel_rgb(i, 89, 17, 88   )
            else:
                pixels.set_pixel_rgb(i, 0,0,0   )

        pixels.show()
        if wait > 0:
            time.sleep(wait)
        count = count + 1

def snow(pixels, wait=0.5):
    for i in range(0,50):
        pixels.set_pixel_rgb(i, 255, 255, 255   )
    pixels.show()

    count = 0
    while count <40:
        for i in range(50, pixels.count()):
            if random.getrandbits(2) == 1:
                pixels.set_pixel_rgb(i, 255, 255, 255   )
            else:
                pixels.set_pixel_rgb(i, 0,0,0   )

        pixels.show()
        if wait > 0:
            time.sleep(wait)
        count = count + 1

def nano_sparkles(pixels, wait=0.1):
    count = 245
    while count > 0:
        for i in range(count, pixels.count()):
            if random.getrandbits(2) == 1:
                pixels.set_pixel_rgb(i,74, 144, 226 )
            else:
                pixels.set_pixel_rgb(i, 0,0,0   )

        pixels.show()
        if wait > 0:
            time.sleep(wait)
        count = count - 1


def alt_red_green(pixels, wait=1):
    count = 0
    while count < 20:
        if (count % 2) == 0:
            for i in range(pixels.count()):
                if (i % 2)  == 0:
                    pixels.set_pixel_rgb(i, 255, 0, 0   )
                else:
                    pixels.set_pixel_rgb(i, 0,255,0   )
        else:
            for i in range(pixels.count()):
                if (i % 2)  == 0:
                    pixels.set_pixel_rgb(i, 0, 255, 0   )
                else:
                    pixels.set_pixel_rgb(i, 255,0,0   )

        pixels.show()
        if wait > 0:
            time.sleep(wait)
            count = count + 1

def test_pixels(pixels, selected):
    for i in range(pixels.count()):
        pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color(89, 17, 88))
        pixels.show()
        print(i)
        time.sleep(2)


def purple_cycle(pixels, wait=0.005):
    for j in range(256): # one cycle of all 256 colors in the wheel
        for i in range(pixels.count()):
            pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color(89, 17, 88)) #wheel(((i * 256 // pixels.count()) + j) % 256) )
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def rainbow_colors(pixels, wait=0.005):
    for j in range(256): # one cycle of all 256 colors in the wheel
        for i in range(pixels.count()):
            pixels.set_pixel(i, wheel(((256 // pixels.count() + j)) % 256) )
        pixels.show()
        if wait > 0:
            time.sleep(wait)

def rainbow_colors_alt(pixels, wait=0.05):
    count = 0
    for j in range(256): # one cycle of all 256 colors in the wheel
        count = count + 1
        for i in range(pixels.count()):
            if (i % 2) == 0:
                pixels.set_pixel(i, wheel(((256 // pixels.count() + j)) % 256) )
            else:
                pixels.set_pixel_rgb(i, 0,0,0   )
        #    else:
        #        if (i % 2) == 0:
        #            pixels.set_pixel_rgb(i, 0,0,0   )
        #        else:
        #            pixels.set_pixel(i, wheel(((256 // pixels.count() + j)) % 256) )

        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def brightness_decrease(pixels, wait=0.01, step=1):
    for j in range(int(256 // step)):
        for i in range(pixels.count()):
            r, g, b = pixels.get_pixel_rgb(i)
            r = int(max(0, r - step))
            g = int(max(0, g - step))
            b = int(max(0, b - step))
            pixels.set_pixel(i, Adafruit_WS2801.RGB_to_color( r, g, b ))
        pixels.show()
        if wait > 0:
            time.sleep(wait)
 
def blink_color(pixels, blink_times=5, wait=0.5, color=(255,0,0)):
    for i in range(blink_times):
        # blink two times, then wait
        pixels.clear()
        for j in range(2):
            for k in range(pixels.count()):
                pixels.set_pixel(k, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
            pixels.show()
            time.sleep(0.08)
            pixels.clear()
            pixels.show()
            time.sleep(0.08)
        time.sleep(wait)
 
def appear_from_back(pixels, color=(89, 17, 88), wait=0.001):
    pos = 0
    for i in range(pixels.count()):
        for j in reversed(range(i, pixels.count())):
            pixels.clear()
            # first set all pixels at the begin
            for k in range(i):
                pixels.set_pixel(k, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
            # set then the pixel at position j
            pixels.set_pixel(j, Adafruit_WS2801.RGB_to_color( color[0], color[1], color[2] ))
            pixels.show()
            time.sleep(wait)
            
 
if __name__ == "__main__":

  while 1:
      # Clear all the pixels to turn them off.
      pixels.clear()
      pixels.show()  # Make sure to call show() after changing any pixels!
 
      # rainbow_cycle_successive(pixels, wait=0.01)
      # rainbow_cycle(pixels, wait=0.01)
 
      # brightness_decrease(pixels)

      test_pixels(pixels, [241,242,243,244,245,246,247,248,249])
