import network
import sys
import time
from machine import Pin

ssid = 'SSID'
password = 'wireless'

led = Pin(4, Pin.OUT)


def blink():
    for i in [1, 2, 3, 4, 5]:
        led.value(1)
        time.sleep(0.2)
        led.value(0)
        time.sleep(0.2)


def connect_wifi():
    timeout = 0
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.disconnect()
    time.sleep(5)
    wifi.connect(ssid, password)
    if not wifi.isconnected():
        print('Connecting ..........')
        while not wifi.isconnected() and timeout < 10:
            print(10 - timeout)
            timeout = timeout + 1
            time.sleep(1)

    if wifi.isconnected():
        print('Connected')
        print(wifi.ifconfig())
        blink()
    else:
        print('not connected')
        sys.exit()


connect_wifi()

