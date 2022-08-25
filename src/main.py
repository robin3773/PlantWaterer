from machine import Pin, Timer
import time
import ntptime
import sys
import dht
from adafruit_io import *

dht_sensor = dht.DHT11(Pin(14))  # DHT11 Sensor on Pin 14 of ESP32
pump = Pin(4, Pin.OUT)  # Onboard LED on Pin 2 of ESP32

client = AdaFruitMQTT(pump)
client.connect()


def sensor_data():
    dht_sensor.measure()  # Measuring
    print('Measuring DHT Sensor Data...............')
    time.sleep(3)
    temp = dht_sensor.temperature()  # getting Temp
    hum = dht_sensor.humidity()
    soil_moisture = hum
    return temp, hum, soil_moisture


def send_data():
    data = sensor_data()
    client.publish(data)


timer = Timer(0)
timer.init(period=60 * 1000, mode=Timer.PERIODIC, callback=send_data)

while True:
    try:
        client.check_msg()
    except Exception as error:
        print(error)
        client.disconnect()
