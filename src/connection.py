import network


class Connection:
    def __init__(self, ssid, password):
        import network
        self.ssid = ssid
        self.password = password

    def wifi(self):
        sta_if = network.WLAN(network.STA_IF)
        if not sta_if.isconnected():
            print('connecting to network...')
            sta_if.active(True)
            sta_if.connect(self.ssid, self.password)
            while not sta_if.isconnected():
                pass
        print('network config:', sta_if.ifconfig())

    def bluetooth(self):
        # ON Development Stage
        pass
