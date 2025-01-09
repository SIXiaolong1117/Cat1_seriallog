import sys
import serial
import time

# 串口设置
SERIAL_PORT = '/dev/ttyS5'
BAUDRATE = 115200
TIMEOUT = 1  # 单位秒

# 日志文件路径
LOG_FILE_PATH = '/var/log/cat1_module.log'

# 从日志中读取最新一行
def get_latest_log_line():
    try:
        with open(LOG_FILE_PATH, 'r') as log_file:
            lines = log_file.readlines()
            return lines[-1] if lines else ""
    except Exception as e:
        print(f"Unable to read log file: {e}")
        return ""

# 发送 AT 命令并检查日志中的返回
def send_at_command(port, command, retries=10):
    try:
        # 打开串口
        ser = serial.Serial(port, baudrate=BAUDRATE, timeout=TIMEOUT)
    except serial.SerialException as e:
        print(f"Unable to open serial port: {e}")
        return False

    ser.write((command + '\r\n').encode())
    print(f"Send: {command.strip()}")

    time.sleep(2)

    log_line = get_latest_log_line()
    print(f"{log_line.strip()}")
    return log_line

if __name__ == "__main__":
    # 获取命令行参数
    if len(sys.argv) != 2:
        print("Usage: python sendat.py <AT>")
        sys.exit(1)

    command = sys.argv[1]

    send_at_command(SERIAL_PORT, command)