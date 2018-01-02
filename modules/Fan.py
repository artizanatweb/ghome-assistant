import time
import os
import threading
import RPi.GPIO as GPIO

from modules.Speech import Speech


class Fan(threading.Thread):
    def __init__(self):
        super(Fan, self).__init__()
        self.active = False
        # pin_nr = 23
        self.PIN = 23
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.PIN, GPIO.OUT)
        self.state = False
        GPIO.output(self.PIN, self.state)
        self.speech = Speech()

    def run(self):
        self.active = True
        self.on()

        while self.active:
            if not self.state:
                self.read_temp()
            time.sleep(2)

    def on(self):
        if self.state:
            return False

        self.state = True
        self.update()

        print("FAN ON")
        return self.state

    def off(self):
        if not self.state:
            return False

        self.state = False
        self.update()
        self.read_temp()

        print("FAN OFF")
        return True

    def update(self):
        GPIO.output(self.PIN, self.state)

    def read_temp(self):
        temp = os.popen("vcgencmd measure_temp").readline()
        tmp = temp.replace("temp=", "")
        literal_tmp = tmp.replace("'C\n", "")
        print('Temp read: ', literal_tmp)
        fl_temp = float(literal_tmp)
        if fl_temp >= 46:
            self.on()
            self.speech.say("CPU temperature is " + literal_tmp + " degrees. Ventilator started!")

    def clear(self):
        GPIO.cleanup()
        self.active = False

        try:
            self.join()
        except (ValueError, AttributeError, Exception) as e:
            print("*****Can't JOIN thread*****")
            print(e)

    def get_temperature(self):
        temp = os.popen("vcgencmd measure_temp").readline()
        tmp = temp.replace("temp=", "")
        literal_tmp = tmp.replace("'C\n", "")
        self.speech.say("CPU temperature is " + literal_tmp + " degrees Celsius.")
