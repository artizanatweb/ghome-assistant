#!/usr/bin/env python

import os
import sys
import signal
from modules.GoogleAssistant import GoogleAssistant


# set process title so it can be killed on stop
process_title = "google-assistant"
try:
    import setproctitle

    setproctitle.setproctitle(process_title)
except:
    print('no proc title')

if __name__ == '__main__':
    service = GoogleAssistant()
    service.set_process_title(process_title)
    try:
        service.setup()
        service.loop()
    except (KeyboardInterrupt, SystemExit):
        print('Keyboard Interrupt or System Exit')
    except ValueError as e:
        print(e)

signal.signal(signal.SIGTERM, service.signal_term_handler)
service.clear()

print("Exiting")
sys.exit(1)