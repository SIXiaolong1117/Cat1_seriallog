import wiringpi
import time  # 用于延时操作

# 初始化
wiringpi.wiringPiSetup()

# 设置 GPIO6 为输出模式
wiringpi.pinMode(6, 1)

# 输出电平
wiringpi.digitalWrite(6, 1)
time.sleep(0.1)
wiringpi.digitalWrite(6, 0)

print("重启 AT 模块完成（GPIO6）")
