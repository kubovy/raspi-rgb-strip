#!/usr/bin/python
# -*- coding:utf-8 -*-
import time
import threading
import traceback
import pigpio
from Logger import Logger


class RGB:

    PIN_RED   = 17
    PIN_GREEN = 22
    PIN_BLUE  = 24

    PATTERN_FADEIN  = "fade-in"
    PATTERN_FADEOUT = "fade-out"

    INTERVAL_DEFAULT = 0.05  # Seconds
    STEP_DEFAULT     = 5     # Percent

    red      = 0
    green    = 0
    blue     = 0
    pattern  = ""
    step = STEP_DEFAULT
    interval = INTERVAL_DEFAULT

    interrupted = False
    thread = None

    def __init__(self, client, service_name, debug=False):
        self.client = client
        self.serviceName = service_name
        self.logger = Logger("Pixels", debug)

        self.pi = pigpio.pi()

        self.set_color()
        self.client.message_callback_add(self.serviceName + "/control/rgb/#", self.on_message)

    def on_message(self, client, userdata, msg):
        self.logger.info(msg.topic + ": " + msg.payload)
        try:
            path = msg.topic.split("/")
            if len(path) > 1 and path[0] == self.serviceName and path[1] == "control": # $/control/#
                if len(path) > 2 and path[2] == "rgb":                                 # $/control/rgb/#
                    rgb = msg.payload.split(",")
                    self.red = int(rgb[0])
                    self.green = int(rgb[1])
                    self.blue = int(rgb[2])
                    self.logger.debug("Got " + str(self.red) + "," + str(self.green) + "," + str(self.blue))

                    if len(path) > 3:                                                  # $/control/rgb/[pattern]
                        if path[3] == self.PATTERN_FADEIN or path[3] == self.PATTERN_FADEOUT:
                            self.step = int(rgb[3]) if len(rgb) > 3 else self.STEP_DEFAULT
                            self.interval = float(rgb[4]) / 1000.0 if len(rgb) > 4 else self.INTERVAL_DEFAULT
                        self.pattern = path[3]
                        self.start()
                    else:                                                              # $/control/rgb
                        self.pattern = ""
                        self.set_color(update=True)

        except:
            self.logger.error("Unexpected Error!")
            traceback.print_exc()

    def set_color(self, red=None, green=None, blue=None, update=False):
        red = red if red is not None else self.red
        green = green if green is not None else self.green
        blue = blue if blue is not None else self.blue
        self.logger.debug("Setting to " + str(red) + "," + str(green) + "," + str(blue))
        self.pi.set_PWM_dutycycle(self.PIN_RED, red)
        self.pi.set_PWM_dutycycle(self.PIN_GREEN, green)
        self.pi.set_PWM_dutycycle(self.PIN_BLUE, blue)
        if update:
            self.client.publish(self.serviceName + "/state/rgb", str(red) + "," + str(green) + "," + str(blue), 1, True)

    def looper(self):
        try:
            if self.pattern == self.PATTERN_FADEIN or self.pattern == self.PATTERN_FADEOUT:
                percent_range = range(0, 100, self.step) if self.pattern == self.PATTERN_FADEIN \
                    else range(100, 0, -self.step)

                for percent in percent_range:
                    self.logger.debug("Percent: " + str(percent))
                    red = int(float(self.red) * float(percent) / 100.0)
                    green = int(float(self.green) * float(percent) / 100.0)
                    blue = int(float(self.blue) * float(percent) / 100.0)
                    self.set_color(red=red, green=green, blue=blue, update=False)
                    time.sleep(self.interval)
                    if self.interrupted: break

                if self.pattern == self.PATTERN_FADEOUT: self.red = self.green = self.blue = 0
                self.set_color(update=True)
        except:
            self.logger.error("Unexpected Error!")
            traceback.print_exc()

    def start(self):
        self.stop()
        if self.thread is None:
            self.interrupted = False
            self.thread = threading.Thread(target=self.looper)
            self.thread.start()
        return self.thread

    def stop(self):
        self.interrupted = True
        if self.thread is not None: self.thread.join(5)
        self.thread = None

    def finalize(self):
        self.pi.stop()

