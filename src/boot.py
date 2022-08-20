import network
import sys
import time

ssid = 'SSID'
password = 'wireless'


def connect_wifi():
    timeout = 0
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.disconnect()
    wifi.connect(ssid, password)
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
