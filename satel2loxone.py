from satel_integra.satel_integra import AsyncSatel
from paho.mqtt import client as mqtt_client

import asyncio
import logging
import random
import time

_LOGGER = logging.getLogger(__name__)

#Satel configuration, like ETHM-1 Plus
satel = "192.168.1.99"
satel_port = 7094

#MQTT configuration
broker = 'loxberry'
broker_port = 1883
topic = "satel"
client_id = f'python-mqtt-{random.randint(0, 1000)}'
username = 'loxberry'
password = ''

#Inputs to monitor
zones = [1, 2, 3, 4, 5, 6, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35]

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(client_id)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(broker, broker_port)
    return client


if __name__ == '__main__':
    client = connect_mqtt()
    client.loop_start()

    logging.basicConfig(level=logging.WARNING)

    zonesDict = dict.fromkeys(zones, 0)

    def alarm_status_update_callback():
        _LOGGER.debug("Sending request to update panel state")

    def zones_update_callback(status):
        _LOGGER.debug("Zones callback, status: %s", status)
        for zone, value in status['zones'].items():
            if value != zonesDict[zone]:
                zonesDict[zone] = value
                client.publish(f'{topic}/pir/{zone}', value)


    def outputs_update_callback(status):
        _LOGGER.debug("Outputs updated callback , status: %s", status)

    loop = asyncio.get_event_loop()
    stl = AsyncSatel(satel,
                     satel_port,
                     loop,
                     zones,
                     [1, 2, 3]
                     )

    loop.run_until_complete(stl.connect())
    loop.create_task(stl.keep_alive())
    loop.create_task(
        stl.monitor_status(
            alarm_status_update_callback, zones_update_callback, outputs_update_callback
        ))

    loop.run_forever()
    loop.close()

