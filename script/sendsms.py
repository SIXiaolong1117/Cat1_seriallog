import serial
import time
import sys
import os

# 串口设置
SERIAL_PORT = '/dev/ttyS5'
BAUDRATE = 115200
TIMEOUT = 1  # 单位秒

# 日志文件路径
LOG_FILE_PATH = '/var/log/cat1_module.log'

# 发送 AT 命令并检查日志中的返回
def send_at_OK_check(ser, command, retries=10):
    for _ in range(retries):
        # 发送命令
        ser.write((command + '\r\n').encode())  
        print(f"Send: {command.strip()}")
        
        time.sleep(2)

        log_line = get_latest_log_line()  
        print(f"{log_line.strip()}")
        if "OK" in log_line:
            return True
    return False

def send_at(ser, command, retries=10):
    ser.write((command + '\r\n').encode())
    print(f"Send: {command.strip()}")

    time.sleep(2)

    log_line = get_latest_log_line()
    print(f"{log_line.strip()}")
    return log_line

def send_sms(ser, command):
    # 转换为 UTF-16 BE 编码的字节
    for byte in command.encode('utf-16-be'):  
        ser.write(bytes([byte]))  # 逐个字节发送    
    ser.write(bytes([0x1A]))
    
    time.sleep(2)

    log_line = get_latest_log_line()
    print(f"{log_line.strip()}")

# 从日志中读取最后一行
def get_latest_log_line():
    try:
        with open(LOG_FILE_PATH, 'r') as log_file:
            lines = log_file.readlines()
            return lines[-1] if lines else ""
    except Exception as e:
        print(f"Unable to read log file: {e}")
        return ""

# 从日志中读取倒数第二行
def get_second_last_log_line():
    try:
        with open(LOG_FILE_PATH, 'r') as log_file:
            lines = log_file.readlines()
            return lines[-2] if len(lines) > 1 else ""  # 如果存在的话
    except Exception as e:
        print(f"Unable to read log file: {e}")
        return ""

# 解析短信发送结果
def parse_sms_response():
    log_line = get_latest_log_line()
    if "ERROR" in log_line:
        return False, "SMS sending failed."
    elif "OK" in log_line:
        return True, "SMS sent successfully."
    return False, "Unknown response"

# 发送短信
def send_sms_process(ser, phone_number, message):
    # 步骤 1: 发送 AT\r 确认开机
    if not send_at_OK_check(ser, "AT", retries=10):
        print("AT command failed, device failed to power on or failed to connect.")
        return

    # 步骤 2: 发送 AT+ICCID\r 获取 SIM 卡 ICCID
    if not send_at_OK_check(ser, "AT+ICCID", retries=10):
        print("Unable to obtain SIM card ICCID, the SIM card may be unavailable.")
        return

    # 步骤 3: 发送 AT+CGATT?\r 查询附着状态
    attached = False
    for _ in range(40):
        ser.write(("AT+CGATT?" + '\r\n').encode())
        print(f"Send: AT+CGATT?")
        time.sleep(2)
        log_line = get_second_last_log_line()   
        print(f"{log_line.strip()}")
        if "1" in log_line:  # 检查基站是否附着
            attached = True
            break
        time.sleep(2)
    if not attached:
        print("The base station connection failed and the attachment status could not be obtained.")
        return

    # 步骤 4: 设置短信服务
    if not send_at_OK_check(ser, "AT+CSMS=1"):
        print("Unable to set up SMS service.")
        return

    # 步骤 5: 设置短信格式为 TEXT 模式
    if not send_at_OK_check(ser, "AT+CMGF=1"):
        print("Unable to set SMS format to TEXT mode.")
        return

    # 步骤 6: 设置短信模式为中文
    if not send_at_OK_check(ser, "AT+CSMP=17,167,0,8"):
        print("Unable to set SMS mode to Chinese.")
        return

    # 步骤 7: 发送短信
    # 发送 AT+CMGS="<phone_number>"
    send_command = f'AT+CMGS="{phone_number}"'    # 这里的引号不能瞎写，AT 指令要求双引号
    if ">" not in send_at(ser, send_command):
        return False

    send_sms(ser, message)

def main():
    # 获取命令行参数
    if len(sys.argv) != 3:
        print("Usage: python sendsms.py <Phone Number> <SMS>")
        sys.exit(1)

    phone_number = sys.argv[1]  # 从命令行获取电话号码
    message = sys.argv[2]  # 从命令行获取短信内容

    try:
        # 打开串口连接
        with serial.Serial(SERIAL_PORT, baudrate=BAUDRATE, timeout=TIMEOUT) as ser:
            send_sms_process(ser, phone_number, message)
    except serial.SerialException as e:
        print(f"Serial port connection failed: {e}")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
