#!/usr/bin/python
# -*- coding: utf-8 -*-

MQTTSRV = "SERVER"
MQTTPRT = 1883
MQTTUSR = "MQTT_LOGIN"
MQTTPWD = "MQTT_PASSWORD"
MQTTBAS = "iot_practice"
server_names = ("aws", "oracle", "azure", "thingworx", "cisco", "watson", "thethingsnetwork", "ibmcloud")
dev = "5404"

import hashlib
import paho.mqtt.client as mqtt

def on_connect(mqttc, obj, flags, rc):
    print("rc: " + str(rc))

def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc, obj, level, string):
    print(string)

def main():
    mqttc = mqtt.Client()
    mqttc.on_message = on_message
    mqttc.on_connect = on_connect
    mqttc.on_publish = on_publish
    mqttc.on_subscribe = on_subscribe
    mqttc.username_pw_set(MQTTUSR, MQTTPWD)
    mqttc.connect(MQTTSRV, MQTTPRT, 60)

    for srv in server_names:
        topic = MQTTBAS + "/" + dev + "/servers/" + srv
        payload = hashlib.md5((srv + ":" + dev).encode('utf-8')).hexdigest().upper()[0:6]
        print(topic + ": " + payload)
        mqttc.publish(topic, payload)

if __name__ == '__main__':
    ret = main()
