import time
import network
import _thread
from machine import UART
from machine import Pin
from umqttsimple import MQTTClient
from hx711 import HX711
from utime import sleep_us

# ETC��ǩ��ȡ
labels = "No tag detected yet"
def buf_read(uart, length):
    buf = bytes()
    buf_len = 0
    while True:
        if uart.any():
            buf += uart.read(length - buf_len)
        buf_len = len(buf)
        if buf_len == length:
            return buf
        
def read_etc():
    global labels
    uart_etc = UART(1, baudrate=115200, tx=18, rx=19)
    uart_etc.write(bytes.fromhex('43 4D 02 02 02 00 00 00 00'))
    uart_etc.flush()
    
    # read data
    try:
        while True:
            head = buf_read(uart_etc, 8)
            assert len(head) == 8
            length = head[4] + head[5] * 16 - 2
            if length > 0:
                data = buf_read(uart_etc, length + 1)
            if head[2] == 2 and length > 1: # label detected
                label_id_len = data[1]
                label_id = data[3:3+label_id_len]
                detector_id = data[3+label_id_len]
                labels = "label ID: " + label_id.hex() + " detector ID: " + str(detector_id)
                if(mode == 1):
                    val = scales.stable_value() / A
                    single = 6.1
                    count = int(round(val/single))
                    message = labels + "\nQuantity of goods in warehouse:{}".format(count)
                    c.publish("etc", message)

    except Exception as e:
        print(e, "\nloop stopped") 
        pass
    
    # terminate reading and close the uart
    uart_etc.write(bytes.fromhex('43 4D 03 02 02 00 00 00 00'))
    uart_etc.flush()
    uart_etc.deinit()
    print("uart closed")
    print("labels: ", labels)


# �����߳�
def start_thread():
    global labels
    _thread.start_new_thread(read_etc, ())


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
#         return self._stabilizer(values)
        return values[0]

    @staticmethod
    def _stabilizer(values, deviation=10):
        weights = []
        for prev in values:
            weights.append(sum([1 for current in values if abs(prev - current) / (prev / 100) <= deviation]))
        return sorted(zip(values, weights), key=lambda x: x[1]).pop()[0]


# ESP32����������
def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect('PC', '12345678')
        i = 1
        while not wlan.isconnected():
            print("connecting...{}".format(i))
            i += 1
            time.sleep(1)
    print('network config:', wlan.ifconfig())


# �ص��������յ���������Ϣ�������������
def sub_cb(topic, msg):
    global mode
    global labels
    global info_to_publish
    if topic.decode("utf-8") == "mode":
        if msg.decode("utf-8") == "0":
            mode = 0
        else:
            mode = 1
        print(topic, msg, mode)
        led_pin.value(mode)
    
    elif topic.decode("utf-8") == "weight":
        if msg.decode("utf-8") == "measure":
            val = scales.stable_value() / A
            message = "Total Wight:{:.3f}g".format(val)
            print(message)
            c.publish(topic, message)
            
    elif topic.decode("utf-8") == "etc":
        if msg.decode("utf-8") == "check":
            print(labels)
            c.publish(topic, labels)
        
    elif topic.decode("utf-8") == "led":
        if msg.decode("utf-8") == "on":
            led_pin.value(1)
        elif msg.decode("utf-8") == "off":
            led_pin.value(0)
    

### MAIN

# 1. ����
do_connect()

# 2. ��ʼ��
mode = 0  # Ĭ��ִ��ģʽΪ0��ѯ��ģʽ��1����������ģʽ
scales = Scales(d_out=22, pd_sck=23)  # HX711�������ݴ���ӿ�
scales.tare()
A = 1020
val = scales.stable_value() / A
led_pin = Pin(2, Pin.OUT)  # ͨ��GPIO��2����ESP32���LED��
control = Pin(34, Pin.IN, Pin.PULL_UP)
# 3. ����mqtt
c = MQTTClient(
        client_id="ESP32",
        server="df6faaff.ala.dedicated.aliyun.emqxcloud.cn",
        user="esp32",
        password="123456")

c.set_callback(sub_cb)  # ���ûص�����
c.connect()             # ��������
# ��Ӷ��ģ����ͨ�������տ�������
c.subscribe(b"mode") 
c.subscribe(b"weight")  
c.subscribe(b"etc")

# 4. �����߳�
start_thread()  # �����߳�

# 5. ����ѭ����أ���غͼ��mqtt��Ϣ
while True:
    c.check_msg()
    time.sleep(1)
