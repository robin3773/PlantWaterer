import machine
import time
import sys
import network
from umqtt.robust import MQTTClient

flash = machine.Pin(4, machine.Pin.OUT)
flash.value(0)

mqtt_client_id = bytes('client_' + '377', 'utf-8')
ADAFRUIT_IO_URL = 'io.adafruit.com'
ADAFRUIT_IO_USERNAME = "MHR377"
ADAFRUIT_IO_KEY = "aio_DWDV62PQKGZPASNKuvdBPePelkGb"
TOGGLE_FEED_ID = 'led'


def connect_wifi():
    timeout = 0
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.disconnect()
    wifi.connect('SSID', 'wireless')
    if not wifi.isconnected():
        print('Connecting ..........')
        while not wifi.isconnected() and timeout < 5:
            print(5 - timeout)
            timeout = timeout - 2
            time.sleep(1)
            print('Network config:', wifi.ifconfig())

    if wifi.isconnected():
        print('Connected....')
        print('Network config:', wifi.ifconfig())
    else:
        print('not connected')
        sys.exit()


connect_wifi()

client = MQTTClient(client_id=mqtt_client_id, server=ADAFRUIT_IO_URL, user=ADAFRUIT_IO_USERNAME,
                    password=ADAFRUIT_IO_KEY, ssl=False)
try:
    client.connect()
except Exception as e:
    print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
    sys.exit()


def cb(topic, msg):
    print('Received Data:  Topic = {}, Msg = {}'.format(topic, msg))
    received_data = str(msg, 'utf-8')
    if received_data is '0':
        flash.value(0)
    elif received_data is '1':
        flash.value(1)


toggle_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_IO_USERNAME, TOGGLE_FEED_ID), 'utf-8')
client.set_callback(cb)
client.subscribe(toggle_feed)

while True:
    try:
        client.check_msg()
    except:
        client.disconnect()
        sys.exit()
