import time
import network
from umqttsimple import MQTTClient
from hx711 import HX711
from utime import sleep_us

# 定义HX711类及函数
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

# ESP32连接无线网
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        # WIFI名字和密码
        wlan.connect('IoT-Lab_WiFi6_2.4G', 'CD449C0E36')
        i = 1
        while not wlan.isconnected():
            print("connecting...{}".format(i))
            i += 1
            time.sleep(1)
    print('network config:', wlan.ifconfig())

# 回调函数，收到服务器消息后会调用这个函数
def sub_cb(topic, msg): 
    if topic.decode("utf-8") == "weight":
        if msg.decode("utf-8") == "t1":
            val = scales.stable_value()/A
            message = "{:.3f}g".format(val)
            c.publish(topic, message)
        elif msg.decode("utf-8") == "t5":
            i = 0
            sum = 0
            while i < 60:
                val = scales.stable_value()/A
                message = "{:.3f}".format(val)
                c.publish(topic, message)
                i += 1
                sum += val
            val = sum/5
            message = "{:.3f}".format(val)
            c.publish(topic, message)

    elif topic.decode("utf-8") == "etc":
        print(topic, msg)

 
# 1. 联网
do_connect()

# 2. 创建mqtt
c = MQTTClient("ESP32", "192.168.0.102")    # 建立一个名为ESP32的MQTT客户端，IP地址为服务端IP
                                            # 使用EMQX本地部署的服务器，因此使用本机ip
c.set_callback(sub_cb)  # 设置回调函数
c.connect()             # 建立连接
c.subscribe(b"weight")  # 添加订阅，监控weight这个通道，接收控制命令
c.subscribe(b"etc")

# 3. 初始化测量重量设置
scales = Scales(d_out=22, pd_sck=23)
scales.tare()
A = 1013.5
val = scales.stable_value()/A

# 4. 循环持续监控
while True:
    c.check_msg()
    time.sleep(1)