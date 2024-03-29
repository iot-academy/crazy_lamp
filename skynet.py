#!/usr/bin/python
# -*- coding: utf-8 -*-
import hashlib
import paho.mqtt.client as mqtt
import time
from threading import Thread
import random
from termcolor import colored
import colorama


MQTTSRV = "SERVER"
MQTTPRT = 1883
MQTTUSR = "MQTT_LOGIN"
MQTTPWD = "MQTT_PASSWORD"
MQTTBAS = "iot_practice"
seconds = 5
server_names = ("aws", "oracle", "azure", "thingworx", "cisco", "watson", "thethingsnetwork", "ibmcloud")

colorama.init()
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
            print("\033[32mDevice " + dev + " in safety!\033[0m")
            infected.pop(dev, None)
            # set to predefined state
            mqttc.publish(MQTTBAS + "/" + dev + "/lamp", "off", 1)
            mqttc.publish(MQTTBAS + "/" + dev + "/lamp/color", "#dec0de", 1)
            mqttc.publish(MQTTBAS + "/" + dev + "/lamp/mode", "rgb", 1)
            mqttc.publish(MQTTBAS + "/" + dev + "/lamp", "on", 1)

def on_message_init(mosq, obj, msg):
    global infected
    topics = msg.topic.split("/")
    dev = topics[1]
    print("\033[31mDevice " + dev + " infected!\033[0m")
    infected[dev] = servers.copy()

def on_message_i_am(mosq, obj, msg):
    global infected
    topics = msg.topic.split("/")
    dev = topics[1]
    if str(msg.payload.decode('utf-8')) == "guru":
        print("\033[31mDevice " + dev + " infected!\033[0m")
        infected[dev] = servers.copy()
    if str(msg.payload.decode('utf-8')) == "weakling" and dev in infected:
        print("\033[31mYou're a weakling! \033[32mDevice " + dev + " in safety!\033[0m")
        infected.pop(dev, None)

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
                if time_left == 0:
                    time_left = seconds
                    # destroy bad protection
                    for srv in server_names:
                        mqttc.publish(MQTTBAS + "/" + dev + "/servers/" + srv, "")
                    # set to predefined state
                    color_r = 208
                    color_g = 13
                    color_b = 173
                    state = "on"
                    mode = "rgb"

                mqttc.publish(MQTTBAS + "/" + dev + "/lamp/value", str(value))
                mqttc.publish(MQTTBAS + "/" + dev + "/lamp/color", "rgba(" + str(color_r) + "," + str(color_g) + "," + str(color_b) + ", 0)")
                mqttc.publish(MQTTBAS + "/" + dev + "/lamp/mode", mode)
                mqttc.publish(MQTTBAS + "/" + dev + "/lamp", state)
                print(dev, end=", ")
            print("\b\b ")
        time.sleep(1)

thread = Thread(target = attack, args = ())
thread.daemon = True
mqttc = mqtt.Client()
#mqttc.message_callback_add(MQTTBAS + "/+/lamp/init", on_message_init)
mqttc.message_callback_add(MQTTBAS + "/+/i_am", on_message_i_am)
mqttc.message_callback_add(MQTTBAS + "/+/servers/#", on_message_srv)
mqttc.on_connect = on_connect
mqttc.username_pw_set(MQTTUSR, MQTTPWD)
mqttc.connect(MQTTSRV, MQTTPRT, 60)
thread.start()
mqttc.subscribe(MQTTBAS + "/#", 0)
mqttc.loop_forever()
