#!/bin/bash

# 日志文件路径
LOG_FILE_PATH="/var/log/cat1_module.log"

# Python 脚本路径
SCRIPT_PATH="/usr/local/bin/cat1logsmod.py"

# 延迟时间（秒）
DELAY_TIME=5

# 使用 inotifywait 监控文件变化
inotifywait -m -e modify "$LOG_FILE_PATH" | while read -r filename event; do
    # 检测到文件变化后等待一段时间，确保数据不会丢失
    sleep "$DELAY_TIME"
    
    # 执行 Python 脚本来解析日志
    python3 "$SCRIPT_PATH"
done
