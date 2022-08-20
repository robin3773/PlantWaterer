from machine import Pin, Timer
import network
import time
from umqtt.robust import MQTTClient
import sys
import dht

sensor = dht.DHT11(Pin(14))  # DHT11 Sensor on Pin 4 of ESP32
led = Pin(4, Pin.OUT)  # Onboard LED on Pin 2 of ESP32


def blink():
    for i in [1, 2, 3, 4, 5]:
        led.value(1)
        time.sleep(0.2)
        led.value(0)
        time.sleep(0.2)


mqtt_client_id = bytes('client_' + '12321', 'utf-8')  # Just a random client ID

ADAFRUIT_IO_URL = 'io.adafruit.com'
ADAFRUIT_IO_USERNAME = "MHR377"
ADAFRUIT_IO_KEY = "aio_fPwW72I3cetpeD2muqDJdT7cK29u"

PUMP_FEED_ID = 'pump'
TEMP_FEED_ID = 'temp'
HUM_FEED_ID = 'hum'
MOISTURE_FEED_ID = 'soil-moisture'
IMAGE_FEED_ID = 'tree-photo'
OUTPUT_FEED_ID = 'serial'
LED_FEED_ID = 'led'

client = MQTTClient(client_id=mqtt_client_id,
                    server=ADAFRUIT_IO_URL,
                    user=ADAFRUIT_IO_USERNAME,
                    password=ADAFRUIT_IO_KEY,
                    ssl=False)
try:
    client.connect()
except Exception as e:
    print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
    sys.exit()

blink()


def cb(topic, msg):  # Callback function
    print('Received Data:  Topic = {}, Msg = {}'.format(topic, msg))
    recieved_data = str(msg, 'utf-8')  # Recieving Data
    if recieved_data == "0":
        led.value(0)
    if recieved_data == "1":
        led.value(1)


temp_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_IO_USERNAME, TEMP_FEED_ID),
                  'utf-8')  # format - techiesms/feeds/temp
hum_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_IO_USERNAME, HUM_FEED_ID),
                 'utf-8')  # format - techiesms/feeds/hum
pump_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_IO_USERNAME, PUMP_FEED_ID),
                  'utf-8')  # format - techiesms/feeds/led1
moisture_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_IO_USERNAME, MOISTURE_FEED_ID), 'utf-8')
image_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_IO_USERNAME, IMAGE_FEED_ID), 'utf-8')
# led_feed = bytes('{:s}/feeds/{:s}'.format(ADAFRUIT_IO_USERNAME, LED_FEED_ID), 'utf-8') # format - techiesms/feeds/led1

client.set_callback(cb)  # Callback function
client.subscribe(pump_feed)  # Subscribing to particular topic


def sens_data(data):
    sensor.measure()  # Measuring
    time.sleep(5)
    temp = sensor.temperature()  # getting Temp
    hum = sensor.humidity()
    client.publish(temp_feed,
                   bytes(str(temp), 'utf-8'),  # Publishing Temprature to adafruit.io
                   qos=0)

    client.publish(hum_feed,
                   bytes(str(hum), 'utf-8'),  # Publishing Temprature to adafruit.io
                   qos=0)

    client.publish(moisture_feed, bytes(str(hum), 'utf-8'),
                   qos=0)

    current_time = time.localtime()
    (year, month, day, hour, minute, second, *rest) = current_time

    print('Message Sent at {}/{}/{} {}:{}:{}'.format(year, month, day, hour, minute, second))
    print("Temperature - {:s} Humidity - {:s}".format(str(temp), str(hum)))
    print()


timer = Timer(0)
timer.init(period=60 * 1000, mode=Timer.PERIODIC, callback=sens_data)

while True:
    try:
        client.check_msg()  # non blocking function
    except Exception as e:
        print(e)
        client.disconnect()
        sys.exit()

