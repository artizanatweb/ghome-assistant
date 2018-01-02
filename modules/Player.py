import threading
import os
import subprocess
import time
import nltk

from modules.Speech import Speech


class Player(threading.Thread):
    def __init__(self):
        super(Player, self).__init__()
        self.path = "/home/pi/Music/"
        self.playlist = "good"
        self.files = "/*.mp3"
        self.running = False
        self.sp = None
        self.start_flag = False
        self.active = True
        self.minVol = -50
        self.maxVol = 10
        self.volume = -25
        self.response_volume = "40"
        self.speech = Speech()

    def run(self):
        while self.active:
            if self.start_flag and not self.running:
                print("I am going to start mplayer")
                self.running = True
                os.system('mplayer -af volume=' + str(self.volume) + ' ' + self.path + self.playlist + self.files)
                print("MPlayer started!")

            time.sleep(2)

    def on(self):
        if self.running:
            print('mplayer running')
            return

        self.start_flag = True

    def off(self):
        if not self.running:
            print('nothing to stop')
            return

        self.start_flag = False

        self.running = False
        os.system('killall mplayer')

    def clear(self):
        if self.running:
            self.off()

        self.active = False

        try:
            self.join()
        except (ValueError, AttributeError, Exception) as e:
            print("*****Can't JOIN thread*****")
            print(e)

    def get_playlists(self):
        playlists = []
        list_dir = os.listdir(self.path)
        for sub_dir in list_dir:
            if not os.path.isdir(self.path + sub_dir):
                continue

            playlists.append(sub_dir)

        return playlists

    def set_playlist(self, playlist_name: str):
        self.playlist = playlist_name
        return

    def get_volumes(self):
        return self.volumes

    def set_volume_literal(self, volume: str):
        if volume not in self.volumes.keys():
            return False

        int_volume = self.volumes[volume]
        new_volume = int_volume + self.minVol
        if new_volume <= self.maxVol:
            self.volume = new_volume

        return self.volume

    def set_volume(self, volume: int):
        new_volume = volume + self.minVol
        if new_volume <= self.maxVol:
            self.volume = new_volume

        return self.volume

    def playlist_actions(self, str_resp, raw_resp):
        if 'start' in str_resp:
            # os.system("espeak -a " + self.response_volume + " -g 9 -ven+f3 \"Starting playlist!\"")
            self.speech.say("Starting playlist!")
            return self.on()
        if 'stop' in str_resp:
            os.system('aplay /root/sounds/tdrwht01.wav')
            return self.off()

        if 'text' not in raw_resp:
            return
        tts_array_response = nltk.word_tokenize(raw_resp['text'])

        if 'set' in tts_array_response or 'change' in tts_array_response:
            new_playlist = None
            playlists = self.get_playlists()
            try:
                tts_array_response.remove('playlist')
                tts_array_response.remove('set')
                tts_array_response.remove('change')
            except ValueError as e:
                print(e)

            for word in tts_array_response:
                if word in playlists:
                    new_playlist = word
                    break

            if new_playlist is not None:
                self.set_playlist(new_playlist)
                # os.system("espeak -a " + self.respons + " -g 9 -ven+f3 \"Playlist found: " + new_playlist + "\"")
                self.speech.say("Playlist found: " + new_playlist)
            else:
                # os.system("espeak -a " + self.response_volume + " -g 9 -ven+f3 \"Playlist not found! Please try again!\"")
                self.speech.say("Playlist not found! Please try again!")

    def volume_actions(self, raw_resp):
        if 'text' not in raw_resp:
            return
        tts_array_response = nltk.word_tokenize(raw_resp['text'])

        if 'set' in tts_array_response:
            try:
                tts_array_response.remove('volume')
                tts_array_response.remove('set')
            except ValueError as e:
                print(e)

            vol = None
            number = 0
            for word in tts_array_response:
                try:
                    number = int(word)
                except ValueError as e:
                    continue

                new_volume = self.set_volume(number)
                print(new_volume)

                # os.system("espeak -a " + self.response_volume + " -g 9 -ven+f3 \"New volume set to : " + word + "\"")
                self.speech.say("New volume set to : " + word)
                vol = word

            if vol is None:
                # os.system("espeak -a " + self.response_volume + " -g 9 -ven+f3 \"Volume not changed!\"")
                self.speech.say("Volume not changed!")
