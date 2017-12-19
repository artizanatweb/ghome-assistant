from __future__ import print_function

import argparse
import os.path
import json
import nltk
import subprocess

import google.oauth2.credentials

from google.assistant.library import Assistant
from google.assistant.library.event import EventType
from google.assistant.library.file_helpers import existing_file
from modules.google_home_lights import lights

from modules.Player import Player
from modules.Fan import Fan


class GoogleAssistant:
    def __init__(self):
        self.fan = Fan()
        self.player = Player()
        self.process_title = ""
        self.response_volume = "40"

    def set_process_title(self, process_title):
        self.process_title = process_title

    def setup(self):
        self.fan.start()
        self.player.start()

        # setup done
        return subprocess.Popen(["aplay", "/root/sounds/tgowht01.wav"], stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def process_event(self, event):
        """Pretty prints events.

            Prints all events that occur with two spaces between each new
            conversation and a single space between turns of a conversation.

            Args:
                event(event.Event): The current event to process.
            """

        if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
            lights.wakeup()
            subprocess.Popen(["aplay", "/root/sounds/transmission.wav"], stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print()

        print(event)

        if event.type == EventType.ON_CONVERSATION_TURN_FINISHED:
            if event.args and event.args['with_follow_on_turn']:
                lights.listen()
            else:
                lights.off()
                subprocess.Popen(["aplay", "/root/sounds/mouseover.wav"], stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print()

        if event.type == EventType.ON_RESPONDING_STARTED:
            lights.speak()

    def loop(self):
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
                self.process_event(event)

                if event.type == EventType.ON_CONVERSATION_TURN_STARTED:
                    if self.player.running:
                        assistant.stop_conversation()
                        self.player.off()
                        lights.off()
                        subprocess.Popen(
                            ["espeak", "-a", self.response_volume, "-g", "9", "-ven+f3", '"Playlist stopped!"'],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        continue

                if event.type != EventType.ON_RECOGNIZING_SPEECH_FINISHED:
                    continue

                usrcmd = event.args
                if 'playlist'.lower() in str(usrcmd).lower():
                    assistant.stop_conversation()
                    self.player.playlist_actions(str(usrcmd).lower(), usrcmd)
                    continue

                if 'volume'.lower() in str(usrcmd).lower():
                    assistant.stop_conversation()
                    self.player.volume_actions(usrcmd)
                    continue

                if "power off".lower() in str(usrcmd).lower():
                    assistant.stop_conversation()
                    subprocess.Popen(["aplay", "/root/sounds/utcwht01.wav"], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.power_off()
                    continue

                if "reboot".lower() in str(usrcmd).lower():
                    assistant.stop_conversation()
                    subprocess.Popen(["aplay", "/root/sounds/utcwht01.wav"], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    self.reboot()
                    continue

                if 'ventilator'.lower() in str(usrcmd).lower():
                    assistant.stop_conversation()
                    if 'start'.lower() in str(usrcmd).lower() or 'on'.lower() in str(usrcmd).lower():
                        subprocess.Popen(["aplay", "/root/sounds/mousedown2.wav"], stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        self.fan.on()
                        continue
                    if 'stop'.lower() in str(usrcmd).lower() or 'off'.lower() in str(usrcmd).lower():
                        subprocess.Popen(["aplay", "/root/sounds/mousedown2.wav"], stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        self.fan.off()
                        continue

                if 'lights'.lower() in str(usrcmd).lower():
                    assistant.stop_conversation()
                    if 'start'.lower() in str(usrcmd).lower() or 'on'.lower() in str(usrcmd).lower():
                        subprocess.Popen(["aplay", "/root/sounds/mousedown2.wav"], stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        self.lights_control(True)
                        continue
                    if 'stop'.lower() in str(usrcmd).lower() or 'off'.lower() in str(usrcmd).lower():
                        subprocess.Popen(["aplay", "/root/sounds/mousedown2.wav"], stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        self.lights_control(False)
                        continue
                    if 'clear'.lower() in str(usrcmd).lower():
                        subprocess.Popen(["aplay", "/root/sounds/mousedown2.wav"], stdin=subprocess.PIPE,
                                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        lights.off
                        continue


    def power_off(self):
        os.system('poweroff')

    def reboot(self):
        os.system('reboot');

    def lights_control(self, param: bool):
        if param:
            print("LIGHTS ON")
        if not param:
            print("LIGHTS OUT")

    def clear(self):
        self.fan.clear()
        self.player.clear()

    def signal_term_handler(self):
        print("Catched KILL signal!")
