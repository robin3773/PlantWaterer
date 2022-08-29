from machine import Pin
from umqtt.robust import MQTTClient
import time
import sys

led = Pin(4, Pin.OUT)


def blink_led(n):
    for i in range(n):
        led.value(not led.value())
        time.sleep(0.1)
    led.value(0)


class AdaFruitMQTT:
    def __init__(self, pump):
        self.mqtt_client_id = bytes('client_' + '12321', 'utf-8')  # Just a random client ID

        self.ADAFRUIT_IO_URL = 'io.adafruit.com'
        self.ADAFRUIT_IO_USERNAME = "MHR377"
        self.ADAFRUIT_IO_KEY = "aio_zhOp36uDtp91qLvz9jygZ4xFhCcZ"

        self.PUMP_FEED_ID = 'pump'
        self.TEMP_FEED_ID = 'temp'
        self.HUM_FEED_ID = 'hum'
        self.MOISTURE_FEED_ID = 'soil-moisture'
        self.IMAGE_FEED_ID = 'tree-photo'
        self.OUTPUT_FEED_ID = 'serial'
        self.STATUS_FEED_ID = 'status'

        self.temp_feed = bytes('{:s}/feeds/{:s}'.format(self.ADAFRUIT_IO_USERNAME, self.TEMP_FEED_ID), 'utf-8')
        self.hum_feed = bytes('{:s}/feeds/{:s}'.format(self.ADAFRUIT_IO_USERNAME, self.HUM_FEED_ID), 'utf-8')
        self.pump_feed = bytes('{:s}/feeds/{:s}'.format(self.ADAFRUIT_IO_USERNAME, self.PUMP_FEED_ID), 'utf-8')
        self.moisture_feed = bytes('{:s}/feeds/{:s}'.format(self.ADAFRUIT_IO_USERNAME, self.MOISTURE_FEED_ID), 'utf-8')
        self.image_feed = bytes('{:s}/feeds/{:s}'.format(self.ADAFRUIT_IO_USERNAME, self.IMAGE_FEED_ID), 'utf-8')
        self.status_feed = bytes('{:s}/feeds/{:s}'.format(self.ADAFRUIT_IO_USERNAME, self.STATUS_FEED_ID), 'utf-8')

        self.client = MQTTClient(client_id=self.mqtt_client_id,
                                 server=self.ADAFRUIT_IO_URL,
                                 user=self.ADAFRUIT_IO_USERNAME,
                                 password=self.ADAFRUIT_IO_KEY,
                                 ssl=False)

        self.pump = pump
        self.count = 0

    def connect(self):
        try:
            self.client.connect()
            blink_led(5)
            print('Connected to Adafruit IO! Listening for /click changes........')
            self.subscribe(self.pump_feed)
        except Exception as e:
            print('could not connect to MQTT server {}{}'.format(type(e).__name__, e))
            if self.count < 5:
                print('{:s} . Retrying..........'.format(str(self.count)))
                self.disconnect()
            else:
                sys.exit()

    def receive_and_perform(self, topic, msg):  # Callback function
        current_time = time.localtime(time.time() + 6 * 3600)
        (year, month, day, hour, minute, second, *rest) = current_time
        print('Received Data at {}/{}/{} {}:{}:{}:  Topic = {}, Msg = {}'.format(year, month, day, hour, minute, second,
                                                                                 topic, str(msg, 'utf-8')))
        data = str(msg, 'utf-8')
        if data == "0":
            self.pump.value(0)
        if data == "1":
            self.pump.value(1)
        self.publish_status(data)

    def subscribe(self, feed):
        self.client.set_callback(self.receive_and_perform)
        self.client.subscribe(feed)

    def publish(self, data, image=None):
        self.client.publish(self.temp_feed, bytes(str(data[0]), 'utf-8'), qos=0)
        self.client.publish(self.hum_feed, bytes(str(data[1]), 'utf-8'), qos=0)
        self.client.publish(self.moisture_feed, bytes(str(data[2]), 'utf-8'), qos=0)

        current_time = time.localtime(time.time() + 6 * 3600)
        (year, month, day, hour, minute, second, *rest) = current_time

        print('Message Sent at {}/{}/{} {}:{}:{}'.format(year, month, day, hour, minute, second))
        print(
            "Temperature - {:s} Humidity - {:s} Soil Moisture - {:s}".format(str(data[0]), str(data[1]), str(data[2])))
        print()

    def publish_status(self, data):
        self.client.publish(self.status_feed, bytes(str(data), 'utf-8'), qos=0)

    def check_msg(self):
        self.client.check_msg()
        # print('Checking message')

    def disconnect(self):
        self.client.disconnect()
        print('Disconnected From Adafruit IO!')
        time.sleep(1)
        self.count += 1
        self.connect()
