from hx711 import HX711
from utime import sleep_us
import network
import time
from umqttsimple import MQTTClient

# ESP32连接无线网
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('name', 'password')  # WIFI名字和密码
        i = 1
        while not wlan.isconnected():
            print("connecting...{}".format(i))
            i += 1
            time.sleep(1)
    print('Connection successful, network config:', wlan.ifconfig())


class Scales(HX711):
    def __init__(self, d_out, pd_sck):
        super(Scales, self).__init__(d_out, pd_sck)
        self.offset = 0

    def reset(self):
        self.power_off()
        self.power_on()

    def tare(self):
        self.offset = self.read()	

    def raw_value(self):
        return self.read() - self.offset

    def stable_value(self, reads=10, delay_us=500):
        values = []
        for _ in range(reads):
            values.append(self.raw_value())
            sleep_us(delay_us)
        return self._stabilizer(values)

    @staticmethod
    def _stabilizer(values, deviation=10):
        weights = []
        for prev in values:
#            weights.append(sum([1 for current in values]))
            weights.append(sum([1 for current in values if abs(prev - current) / (prev / 100) <= deviation]))
        return sorted(zip(values, weights), key=lambda x: x[1]).pop()[0]
    


if __name__ == "__main__":
    scales = Scales(d_out=22, pd_sck=23)
    scales.tare()
    val = scales.stable_value()
    print(val)
    scales.power_off()

