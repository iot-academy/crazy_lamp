#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
import paho.mqtt.client as mqtt
import time
from threading import Thread
import random


MQTTSRV = "SERVER"
MQTTPRT = 1883
MQTTUSR = "MQTT_LOGIN"
MQTTPWD = "MQTT_PASSWORD"
MQTTBAS = "iot_practice"
seconds = 5
server_names = ("aws", "oracle", "azure", "thingworx", "cisco", "watson", "thethingsnetwork", "ibmcloud")


infected = dict()
servers = dict.fromkeys(server_names)
time_left = seconds

def on_connect(mqttc, obj, flags, rc):
    print("Connected to: " + MQTTSRV + ":" + str(MQTTPRT))


def on_message_srv(mqttc, obj, msg):
    global infected
    topics = msg.topic.split("/")
    dev = topics[1]
    srv = topics[len(topics)-1]
    status = 0
    # check device id and server name
    if infected.get(dev) is not None and srv in server_names:
        infected.get(dev)[srv] = str(msg.payload.decode('utf-8'))
        # check current protection status - if it is correct then remove from infected list
        for s in server_names:
            data = infected[dev][s]
            if data is not None and len(data) > 0:
                key = hashlib.md5((s + ":" + dev).encode('utf-8')).hexdigest().upper()[0:6]
                if data.upper() == key:
                    status += 1
        if status == len(server_names):
            print("Device " + dev + " in safety!")
            infected.pop(dev, None)

def on_message_init(mosq, obj, msg):
    global infected
    topics = msg.topic.split("/")
    dev = topics[1]
    print("Device " + dev + " infected!")
    infected[dev] = servers.copy()

def on_log(mqttc, obj, level, string):
    print(string)

def attack():
    global time_left
    global mqttc
    global infected
    while True:
        if len(infected):
            print("Attack on device(s): ", end="")
            for dev in infected:
                time_left -= 1
                value = random.randrange(0, 100)
                color_r = random.randrange(0, 255)
                color_g = random.randrange(0, 255)
                color_b = random.randrange(0, 255)
                state = random.choice(["on", "off"])
                mode = random.choice(["dimmer", "rgb"])
                # attack on devices
                mqttc.publish(MQTTBAS + "/" + dev + "/lamp/value", str(value))
                mqttc.publish(MQTTBAS + "/" + dev + "/lamp/color", "rgba(" + str(color_r) + "," + str(color_g) + "," + str(color_b) + ", 0)")
                mqttc.publish(MQTTBAS + "/" + dev + "/lamp/mode", mode)
                mqttc.publish(MQTTBAS + "/" + dev + "/lamp", state)
                if time_left == 0:
                    time_left = seconds
                    # destroy bad protection
                    for srv in server_names:
                        mqttc.publish(MQTTBAS + "/" + dev + "/servers/" + srv, "")
                print(dev, end=", ")
            print("\b\b ")
        time.sleep(1)

thread = Thread(target = attack, args = ())
mqttc = mqtt.Client()
mqttc.message_callback_add(MQTTBAS + "/+/lamp/init", on_message_init)
mqttc.message_callback_add(MQTTBAS + "/+/servers/#", on_message_srv)
mqttc.on_connect = on_connect
mqttc.username_pw_set(MQTTUSR, MQTTPWD)
mqttc.connect(MQTTSRV, MQTTPRT, 60)
thread.start()
mqttc.subscribe(MQTTBAS + "/#", 0)
mqttc.loop_forever()
