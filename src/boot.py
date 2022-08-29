import network
import sys
import time
from machine import Pin
import ntptime

ssid = 'Robin'
password = '12345678'

led = Pin(2, Pin.OUT)


def blink():
    for i in [1, 2, 3, 4, 5]:
        led.value(not led.value())
    led.value(1)


def connect_wifi():
    timeout = 0
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    print('Disconnecting WiFi...............................................................')
    wifi.disconnect()
    time.sleep(2)
    print('WiFi disconnected!')
    wifi.connect(ssid, password)
    if not wifi.isconnected():
        print('Connecting .................................................................')
        while not wifi.isconnected() and timeout < 20:
            print(20 - timeout)
            timeout = timeout + 1
            time.sleep(1)

    if wifi.isconnected():
        print('Connected!')
        print(wifi.ifconfig())
        blink()
    else:
        print('not connected')
        sys.exit()


connect_wifi()
try:
    ntptime.settime()
except Exception as e:
    print('Could not Set Time {}{}'.format(type(e).__name__, e))
