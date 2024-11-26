import time
import network
from umqttsimple import MQTTClient
from hx711 import HX711
from utime import sleep_us

# ����HX711�༰����
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

# ESP32����������
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        # WIFI���ֺ�����
        wlan.connect('IoT-Lab_WiFi6_2.4G', 'CD449C0E36')
        i = 1
        while not wlan.isconnected():
            print("connecting...{}".format(i))
            i += 1
            time.sleep(1)
    print('network config:', wlan.ifconfig())

# �ص��������յ���������Ϣ�������������
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

 
# 1. ����
do_connect()

# 2. ����mqtt
c = MQTTClient("ESP32", "192.168.0.102")    # ����һ����ΪESP32��MQTT�ͻ��ˣ�IP��ַΪ�����IP
                                            # ʹ��EMQX���ز���ķ����������ʹ�ñ���ip
c.set_callback(sub_cb)  # ���ûص�����
c.connect()             # ��������
c.subscribe(b"weight")  # ��Ӷ��ģ����weight���ͨ�������տ�������
c.subscribe(b"etc")

# 3. ��ʼ��������������
scales = Scales(d_out=22, pd_sck=23)
scales.tare()
A = 1013.5
val = scales.stable_value()/A

# 4. ѭ���������
while True:
    c.check_msg()
    time.sleep(1)