#!/usr/bin/env python

# Copyright (C) 2017 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from __future__ import print_function

import argparse
import os.path
import json

import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file

import time
import RPi.GPIO as GPIO
from modules.Player import Player

# set process title so it can be killed on stop
process_title = "google-assistant"
try:
    import setproctitle

    setproctitle.setproctitle(process_title)
except:
    print('no proc title')
    pass


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

mplayer = Player()


def process_event(event):
    """Pretty prints events.

    Prints all events that occur with two spaces between each new
    conversation and a single space between turns of a conversation.

    Args:
        event(event.Event): The current event to process.
    """

    stop_assistant = False

    if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
        if mplayer.running:
            mplayer.stop()
        print()
        os.system('aplay /root/sounds/transmission.wav')

    print(event)

    if (event.type == EventType.ON_CONVERSATION_TURN_FINISHED and
            event.args and not event.args['with_follow_on_turn']):
        print()
        os.system('aplay /root/sounds/mouseover.wav')

    if event.type == EventType.ON_RECOGNIZING_SPEECH_FINISHED:
        arg_text = event.args['text']
        print("recognized event")
        print(arg_text)
        if "stop" == arg_text:
            os.system('aplay /root/sounds/ttawht00.wav')
            os.system('killall ' + process_title)
        if "power off" == arg_text:
            os.system('aplay /root/sounds/utcwht01.wav')
            power_off()
            stop_assistant = True
        if "ventilator off" == arg_text:
            os.system('aplay /root/sounds/mousedown2.wav')
            fan_control(False)
            stop_assistant = True
        if "ventilator on" == arg_text:
            os.system('aplay /root/sounds/mousedown2.wav')
            fan_control(True)
            stop_assistant = True
        if "lights out" == arg_text:
            os.system('aplay /root/sounds/mousedown2.wav')
            lights_control(False)
            stop_assistant = True
        if "lights on" == arg_text:
            os.system('aplay /root/sounds/mousedown2.wav')
            lights_control(True)
            stop_assistant = True
        if "start playlist" == arg_text:
            os.system('aplay /root/sounds/pdrwht00.wav')
            mplayer.run()
            stop_assistant = True
        if "stop playlist" == arg_text:
            os.system('aplay /root/sounds/pdrwht00.wav')
            mplayer.stop()
            stop_assistant = True

    return stop_assistant


def power_off():
    os.system('poweroff')


def fan_control(param: bool):
    if param:
        print("FAN ON")
    if not param:
        print("FAN OFF")
    GPIO.output(PIN, param)


def lights_control(param: bool):
    if param:
        print("LIGHTS ON")
    if not param:
        print("LIGHTS OUT")

def main():
    GPIO.output(PIN, True)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('--credentials', type=existing_file,
                        metavar='OAUTH2_CREDENTIALS_FILE',
                        default=os.path.join(
                            os.path.expanduser('~/.config'),
                            'google-oauthlib-tool',
                            'credentials.json'
                        ),
                        help='Path to store and read OAuth2 credentials')
    args = parser.parse_args()
    with open(args.credentials, 'r') as f:
        credentials = google.oauth2.credentials.Credentials(token=None,
                                                            **json.load(f))

    with Assistant(credentials) as assistant:
        for event in assistant.start():
            stop_assistant = process_event(event)
            if stop_assistant:
                assistant.stop_conversation()


if __name__ == '__main__':
    main()
