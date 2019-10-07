#!/usr/bin/python3
#
#  Call this every minute using Cron to set the NeoPixel clock
#  Cuckoo bird comes out at the top of the hour
#  and tweets once for every hour
#
#  sample crontab
#  * * * * * /root/bin/cuckoo/neoClock.py >> /var/log/neoClock.log 2>&1
#

# TIMEZONE
TZONE = "US/Pacific"	# Set your timezone
			# https://gist.github.com/heyalexej/8bf688fd67d7199be4a1682b3eec7568

# COLORS
HourColor   = (76,  0, 153)	# Hour Hand Color (RED, GREED, BLUE)
MinuteColor = (0, 127, 255)	# Minute Hand Color (RED, GREEN, BLUE)

# SOUNDS			(must be in the same directory as this script)
CLICKWAV    = "click.wav"	# Clock tick sound (set to "" for no click)
CUCKOOWAV   = "cuckoo.wav"	# Cuckoo sound (set to "" for no cuckoo)
VOLUME      = 0.5		# Value between 0.0 and 1.0

## RING PROPERTIES
ring_colors    = "GRBW"	# RGB, GRB, RGWB, GRBW
			# This is the color order for the ring. Different rings have different color orders
ring_pixels    = 24	# The number of pixels on your ring
ring_direction = "cw"	# cw = clockwise, ccw = counter clockwise
			# Yes, some rings are wired in the reverse direction. SMH
pixel_brightness = 0.3	# Value between 0.0 and 1.0

# minute to pixel mapping
# 24 pixel ring, clockwise
min2pix24cw  = [0,0,1,1,2,2,2,3,3,4,4,4,5,5,6,6,6,7,7,8,8,8,9,9,10,10,10,11,11,12,12,12,13,13,14,14,14,15,15,16,16,16,17,17,18,18,18,19,19,20,20,20,21,21,22,22,22,23,23,0,0]

# 24 pixel ring, counter clockwise
min2pix24ccw = [0,0,23,23,22,22,22,21,21,20,20,20,19,19,18,18,18,17,17,16,16,16,15,15,14,14,14,13,13,12,12,12,11,11,10,10,10,9,9,8,8,8,7,7,6,6,6,5,5,4,4,4,3,3,2,2,2,1,1,0,0]

# 16 pixel ring, clockwise
min2pix16cw  = [0,0,1,1,1,1,2,2,2,2,3,3,3,3,4,4,4,5,5,5,5,6,6,6,6,7,7,7,7,8,8,8,9,9,9,9,10,10,10,10,11,11,11,11,12,12,12,13,13,13,13,14,14,14,14,15,15,15,15,0,0]
hr2pix16cw   = [0,1,3,4,5,7,8,9,11,12,13,15,0]

# 16 pixel ring, counter clockwise
min2pix16ccw = [0,0,15,15,15,15,14,14,14,14,13,13,13,13,12,12,12,11,11,11,11,10,10,10,10,9,9,9,9,8,8,8,7,7,7,7,6,6,6,6,5,5,5,5,4,4,4,3,3,3,3,2,2,2,2,1,1,1,1,0,0]
hr2pix16ccw  = [0,15,13,12,11,9,8,7,5,4,3,1,0]

# PyGame support (for audio)
import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import contextlib
with contextlib.redirect_stdout(None):
    import pygame as pg

# setup time realted items
import time
os.environ['TZ'] = TZONE
time.tzset()

# turn on the Crickit amplifier
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(16,GPIO.OUT)
GPIO.output(16,GPIO.HIGH)

# load and play the click sound
wavdir = os.path.dirname(os.path.realpath(__file__)) + "/"
pg.mixer.init(44100, -16, 2, 2048)
pg.mixer.music.set_volume(VOLUME)
if CLICKWAV:
    pg.mixer.music.load(wavdir + CLICKWAV)
    pg.mixer.music.play()

# setup NeoPixels and Crickit hat
import time
import neopixel
from adafruit_crickit import crickit
from adafruit_seesaw.neopixel import NeoPixel

# setup pixel color order
if ring_colors == "GRB":
    ORDER = neopixel.GRB
elif ring_colors == "RGBW":
    ORDER = neopixel.RGBW
elif ring_colors == "GRBW":
    ORDER = neopixel.GRBW
else:
    ORDER = neopixel.RGB

# initialize the pixel ring
pixels = NeoPixel(crickit.seesaw, 20, ring_pixels, bpp=len(ring_colors), brightness=pixel_brightness, pixel_order=ORDER)

# bird functions
bird = crickit.dc_motor_1
beak = crickit.drive_1
beak.frequency = 1000

# push the bird out
def birdOut():
    bird.throttle = 1
    time.sleep(0.35)
    bird.throttle = 0

# pull the bird in
def birdIn():
    bird.throttle = -1
    time.sleep(0.35)
    bird.throttle = 0

# open the beak
def beakOpen():
    beak.fraction = 1.0

# close the beak
def beakClose():
    beak.fraction = 0.0

# if set, play the cuckoo sound
def tweet():
    if CUCKOOWAV:
        pg.mixer.music.play()

# go through the cuckoo sequence
def cuckoo(i):
    # convert to 12 hour clock
    if i > 12:
        i -= 12

    # if set, load the cuckoo sound
    if CUCKOOWAV:
        pg.mixer.music.load(wavdir + CUCKOOWAV)

    # push out the bird
    birdOut()

    # tweet and flap once for every hour
    for x in range(i):
        beakOpen()
        tweet()
        time.sleep(1)
        beakClose()
        time.sleep(1)
    birdIn()

# Turn off all pixels
BLACK = (0,0,0)
if len(ring_colors) == 4:
    BLACK = BLACK + (0,)
pixels.fill((BLACK))
pixels.show()

### FUNCTIONS

# convert minutes to pixel number
def minutePixel(i):
    # make sure i is an int
    i = int(i)

    # default px
    px = 0

    # 24 pixel ring
    if ring_pixels == 24:
      if ring_direction == "cw":
        px = min2pix24cw[i]
      elif ring_direction == "ccw":
        px = min2pix24ccw[i]

    # 16 pixel ring
    elif ring_pixels == 16:
      if ring_direction == "cw":
        px = min2pix16cw[i]
      elif ring_direction == "ccw":
        px = min2pix16ccw[i]

    # return pixel value
    return px

# convert hours to pixel number
def hourPixel(i):
    # if hour is greater than 12, subtract 12 to get the correct 12 hour time
    if i > 12:
        i -= 12

    # default px
    px = 0

    # 24 pixel ring
    if ring_pixels == 24:
        i = i * 2
        px = i

    # 16 pixel ring
    elif ring_pixels == 16:
        if ring_direction == "cw":
            px = hr2pix16cw[i]
        elif ring_direction == "ccw":
            px = hr2pix16ccw[i]

    # return pixel value
    return px

####
####  MAIN STARTS HERE
####

# get hour from clock
HOUR = int(time.strftime("%H"))

# get the ring pixel number
HR = hourPixel(HOUR)

# check for 4th color and append zero if necessary
if len(ring_colors) == 4:
    HourColor = HourColor + (0,)

# set the pixel color for the hour hand
pixels[HR] = HourColor

# get minute from clock
MINUTE = int(time.strftime("%M"))

# get the ring pixel number
MN = minutePixel(MINUTE)

# check for the 4th color and append zero if necessary
if len(ring_colors) == 4:
    MinuteColor = MinuteColor + (0,)

# set the pixel color for the minute hand
pixels[MN] = MinuteColor

# for debug, to see what the time is
print("Time: {:02d}:{:02d}  Pixel: {:02d},{:02d}".format(HOUR,MINUTE,HR,MN))

# display the new clock position
pixels.show()

# check for top of the hour and activate the bird!
if MINUTE == 0:
   cuckoo(HOUR)
