import serial
import time
import logging

# 日志配置
LOG_FILE = "/var/log/cat1_module.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

# 串口配置
SERIAL_PORT = "/dev/ttyS5"
BAUD_RATE = 115200
INIT_COMMAND = "AT\r\n"  # 初始化命令 我所使用的模块不需要初始化 只需要通过AT来确认模组状态

try:
    # 打开串口
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    logging.info(f"Opened serial port {SERIAL_PORT} at {BAUD_RATE} baud.")

    # 发送初始化命令
    ser.write(INIT_COMMAND.encode())
    logging.info(f"Sent initialization command: {INIT_COMMAND.strip()}")

    # 持续读取串口数据并写入日志
    while True:
        if ser.in_waiting > 0:
            data = ser.readline().decode(errors='ignore').strip()
            if data:
                logging.info(f"Received: {data}")
        time.sleep(0.1)

except serial.SerialException as e:
    logging.error(f"Serial port error: {e}")
except Exception as e:
    logging.error(f"Unexpected error: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        logging.info("Serial port closed.")