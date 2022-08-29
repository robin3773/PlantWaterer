from machine import Pin, Timer, ADC
import time
import ntptime
import sys
import dht
from adafruit_io import *

count = 0
loval = 0
hival = 1024
tolow = 100
tohigh = 0

dht_sensor = dht.DHT11(Pin(14))  # DHT11 Sensor on Pin 14 of ESP32
moisture_pin = ADC(0)
pump = Pin(5, Pin.OUT)


def map(val, loval, hival, tolow, tohigh):
    if loval <= val <= hival:
        return (val - loval) / (hival - loval) * (tohigh - tolow) + tolow
    else:
        raise (ValueError)


client = AdaFruitMQTT(pump)
client.connect()


def sensor_data():
    print('Measuring DHT Sensor Data...........................')
    try:
        dht_sensor.measure()  # Measuring
        temp = dht_sensor.temperature()  # getting Temp
        hum = dht_sensor.humidity()
    except Exception as e:
        print('could not measure DHT Sensor data {}{}'.format(type(e).__name__, e))

    print('Measuring Soil Moisture................................')
    moisture_value = moisture_pin.read()
    soil_moisture = map(moisture_value, loval=loval, hival=hival, tolow=tolow, tohigh=tohigh)
    return temp, hum, soil_moisture


def send_data(data):
    data = sensor_data()
    client.publish(data)


def pump_control(moisture_value):
    moisture_value = moisture_pin.read()
    soil_moisture = map(moisture_value, loval=loval, hival=hival, tolow=tolow, tohigh=tohigh)
    print('Moisture Value - {}'.format(soil_moisture))
    if soil_moisture < 50:
        print('Pump is On!')
        pump.value(1)
    else:
        print('Pump is OFF!')
        pump.value(0)
    client.publish_status(pump.value())


timer_send_data = Timer(0)
timer_pump_control = Timer(1)
timer_send_data.init(period=60 * 1000, mode=Timer.PERIODIC, callback=send_data)
timer_pump_control.init(period=29 * 1000, mode=Timer.PERIODIC, callback=pump_control)

while True:
    try:
        client.check_msg()
    except Exception as error:
        print(error)
        client.disconnect()
