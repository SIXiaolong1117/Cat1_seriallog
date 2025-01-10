import os
import re
from datetime import datetime

'''
该脚本主要用于解析日志中的短信内容，短信编码为 UnicodeBE 的 16 进制格式，我们将其解码成对应字符。
使用 init_cat1.py 生成的日志应该如下所示：
2025-01-09 13:12:33,622 - Opened serial port /dev/ttyS5 at 115200 baud.
2025-01-09 13:12:33,622 - Sent initialization command: AT
2025-01-09 13:12:33,723 - Received: AT (Invalid hex data)
2025-01-09 13:12:33,924 - Received: OK
2025-01-09 13:13:50,394 - Received: +CMT: "+86***********",,"25/01/09,13:13:48 +32"
2025-01-09 13:13:50,500 - Received: 4E2D56FD52369020FF0C60E053CA516874033002
                                    ----------------------------------------  <- 我们要解码的内容
'''

# 日志文件路径
LOG_FILE_PATH = '/var/log/cat1_module.log'

def parse_unicode_be(log_path):
    # 确保输出文件夹存在
    output_dir = os.path.join(os.getcwd(), 'cat1logs')
    os.makedirs(output_dir, exist_ok=True)
    # 生成带时间戳的文件名
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file_path = os.path.join(output_dir, f'{timestamp}.log')

    try:
        with open(log_path, 'r', encoding='utf-8') as log_file, open(output_file_path, 'w', encoding='utf-8') as output_file:
            for line in log_file:
                # 匹配 "Received: " 后的 16 进制数据，并确保只包含合法字符
                match = re.search(r'Received:\s([0-9A-F]+)', line)
                if match:
                    hex_data = match.group(1)
                    try:
                        # 确保16进制数据没有多余的空格或非法字符
                        hex_data_cleaned = ''.join(c for c in hex_data if c in '0123456789ABCDEF')

                        # 按照 UnicodeBE 解码 16 进制数据
                        decoded_text = bytes.fromhex(hex_data_cleaned).decode('utf-16-be')
                        line = line.replace(hex_data, f'{hex_data} ({decoded_text})')
                    except UnicodeDecodeError:
                        # 如果解码失败
                        line = line.strip() + " (Decoding failed)\n"
                    except ValueError:
                        # 如果转换失败
                        line = line.strip() + " (Invalid hex data)\n"
                
                # 输出到终端
                print(line, end='')
                # 写入到输出文件
                output_file.write(line)

        print(f"\nProcessed log saved to: {output_file_path}")

    except FileNotFoundError:
        print(f"Log file not found: {log_path}")
    except Exception as e:
        print(f"ERROR: {e}")

parse_unicode_be(LOG_FILE_PATH)