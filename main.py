#!/usr/bin/python
# -*- coding:utf-8 -*-
import traceback
import paho.mqtt.client as mqtt
from Logger import Logger
from RGB import RGB

BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883
SERVICE_NAME = "gyroporus"
DEBUG = True

logger = Logger("MAIN", DEBUG)

# MQTT Client
mqtt = mqtt.Client("Gyroporus", True, None, mqtt.MQTTv311, "tcp")  # create new instance


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    logger.info("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    # client.subscribe("$SYS/#")
    client.subscribe(SERVICE_NAME + "/control/#")
    client.publish(SERVICE_NAME + "/state/status", "ON", 1, True)


def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.error("Unexpected disconnection.")


# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    try:
        logger.debug(msg.topic + ": '" + str(msg.payload) + "'")
    except:
        logger.info("Error!")


mqtt.on_connect = on_connect
mqtt.on_disconnect = on_disconnect
mqtt.on_message = on_message
mqtt.will_set(SERVICE_NAME + "/state/status", "OFF", 1, True)
mqtt.reconnect_delay_set(min_delay=1, max_delay=60)
mqtt.connect(BROKER_ADDRESS, BROKER_PORT, 60)  # connect to broker
mqtt.publish(SERVICE_NAME + "/state/status", "ON", 1, True)

# Modules
rgb = RGB(mqtt, SERVICE_NAME, DEBUG)

logger.info("Press [CTRL+C] to exit")
try:
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    mqtt.loop_forever(retry_first_connection=True)
except KeyboardInterrupt:
    logger.error("Finishing up...")
except:
    logger.error("Unexpected Error!")
    traceback.print_exc()
finally:
    mqtt.publish(SERVICE_NAME + "/state/status", "OFF", 1, True)
    rgb.finalize()

