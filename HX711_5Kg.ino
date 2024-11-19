#include "HX711.h"
float Weight = 0;
int rebootNum;
void setup() {
  Init_HX711();  //初始化HX711模块连接的IO设置

  Serial.begin(9600);
  Serial.print("Welcome to use!\n");

  delay(3000);
  Get_Maopi();  //获取毛皮

}

void loop() {
  Weight = Get_Weight();                  //计算放在传感器上的重物重量
  Serial.print(float(Weight / 1000), 3);  //串口显示重量
  Serial.print(" kg\n");                  //显示单位
  Serial.print("\n");                     //显示单位
  delay(2000);                            //延时1s
  
}
