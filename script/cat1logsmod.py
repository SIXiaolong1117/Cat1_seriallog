import os
import re
from datetime import datetime

# 日志文件路径
LOG_FILE_PATH = '/var/log/cat1_module.log'

def output_decoded_data(output_file, phone_number, receive_time, decoded_data):
    """
    输出解码后的数据到终端和输出文件。
    """
    output_line = (
        f"Phone: {phone_number}\n"
        f"Date: {receive_time}\n"
        f"SMS content:\n{decoded_data.strip()}\n"
    )
    output_file.write(output_line)
    print(output_line)

def parse_unicode_be(log_path):
    # 确保输出文件夹存在
    output_dir = os.path.join(os.getcwd(), '/usr/local/cat1logsmod/logs/')
    os.makedirs(output_dir, exist_ok=True)
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file_path = os.path.join(output_dir, f'{timestamp}.txt')

    try:
        # 打开日志文件 (log_path) 和输出文件 (output_file_path) 并确保文件操作完成后正确关闭文件
        with open(log_path, 'r', encoding='utf-8') as log_file, open(output_file_path, 'w', encoding='utf-8') as output_file:
            previous_sms = None  # 存储上一条短信的手机号码和时间
            decoded_data = ""  # 存储解码后的内容
            for line in log_file:
                match_sms = re.search(r'Received:\s\+CMT:\s"(\+?\d+)",,.*"(\d{2}/\d{2}/\d{2},\d{2}:\d{2}:\d{2} \+\d{2})"', line)
                if match_sms:
                    phone_number = match_sms.group(1)
                    receive_time_str = match_sms.group(2)
                    receive_time = datetime.strptime(receive_time_str.split(' ')[0], '%y/%m/%d,%H:%M:%S')  # 转换为时间对象
                    
                    # 如果当前匹配到的短信手机号码与接收时间和前一条不同 说明前一条已解析完毕可以输出
                    # 此处合并了 3 秒内来自同一手机号的短信分段（短信内容最长 134 字节 超过要分段）
                    if previous_sms and (
                        previous_sms[0] != phone_number or
                        abs((receive_time - previous_sms[1]).total_seconds()) > 3
                    ):
                        output_decoded_data(output_file, previous_sms[0], previous_sms[2], decoded_data)
                        decoded_data = ""  # 清空之前的解码内容
                    
                    previous_sms = (phone_number, receive_time, receive_time)   # 存储当前匹配到的短信手机号码与接收时间
                    continue  # 跳过当前行 处理下一行（待解码数据）
                
                # 匹配解码数据行
                match_data = re.search(r'Received:\s([0-9A-F]+)', line)
                if match_data:
                    hex_data = match_data.group(1)
                    try:
                        # 清理16进制数据中的非法字符
                        hex_data_cleaned = ''.join(c for c in hex_data if c in '0123456789ABCDEF')

                        # 按照 UnicodeBE 解码 16 进制数据
                        decoded_text = bytes.fromhex(hex_data_cleaned).decode('utf-16-be')
                        decoded_data += decoded_text  # 将解码内容添加到当前的解码数据中

                    except (UnicodeDecodeError, ValueError):
                        # 解码失败时跳过该行
                        pass

                # 检测是否为纯英文短信内容
                match_plain_text = re.search(r'Received:\s(.+)', line)
                if match_plain_text:
                    plain_text = match_plain_text.group(1).strip()
                    # 如果是纯英文（不包含16进制字符），直接加入解码数据
                    if all(c.isprintable() for c in plain_text) and not re.search(r'[0-9A-F]{4,}', plain_text):
                        decoded_data += plain_text

            # 最后一条记录要单独处理
            if previous_sms and decoded_data:
                output_decoded_data(output_file, previous_sms[0], previous_sms[1], decoded_data)

        print(f"\nProcessed log saved to: {output_file_path}")

    except FileNotFoundError:
        print(f"Log file not found: {log_path}")
    except Exception as e:
        print(f"ERROR: {e}")

parse_unicode_be(LOG_FILE_PATH)
