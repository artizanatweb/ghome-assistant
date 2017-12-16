#!/usr/bin/env python

import sys
import os
import time
import RPi.GPIO as GPIO

pin_nr = 23
PIN = int(pin_nr)
# nu afisa erorile
GPIO.setwarnings(False)
# seteaza mode pentru GPIO
GPIO.setmode(GPIO.BCM)
# seteaza pinul PIN ca GIPO.OUT
GPIO.setup(PIN, GPIO.OUT)
# reset the pin when program starts
GPIO.output(PIN, False)
time.sleep(1)
GPIO.output(PIN, True)

while True:
    time.sleep(2)

GPIO.cleanup()