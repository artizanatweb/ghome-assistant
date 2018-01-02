from gtts import gTTS
import os


class Speech:
    __instance = None
    _path = './tmp'
    _file_name = 'speech.mp3'

    def __new__(cls):
        if Speech.__instance is None:
            Speech.__instance = object.__new__(cls)
        return Speech.__instance

    def say(self, text):
        self.checkTemp()
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(self._path + '/' + self._file_name)
        os.system("mpg321 " + self._path + "/" + self._file_name)

    def checkTemp(self):
        if os.path.exists(self._path) is False:
            os.mkdir(self._path)
