## 免责声明

1. **合法用途限制**：本脚本仅供学习、研究和合法用途。用户在使用本脚本时，需遵守所在国家或地区的法律法规，不得将本脚本用于任何非法或未经授权的用途。
2. **责任风险声明**：作者不对因使用本脚本造成的任何直接或间接损失、法律责任或争议负责。使用者须自行承担使用本脚本所产生的一切风险和后果。用户承诺仅在遵守当地法律法规和道德规范的前提下使用本脚本。作者明确声明，严禁将本脚本用于任何违反法律的行为。若用户违反上述承诺，所产生的法律责任由用户自行承担，与作者无关。
3. **开源许可声明**：项目经过 [MIT License](/LICENSE) 授权，使用者应遵守协议内容。

---

# Cat1 模块日志记录与基本操作

在 [`script`](/script) 目录下存在两个脚本：

- [`cat1logs.py`](/script/cat1logs.py) -- 对日志中的短信内容进行解码（UnicodeBE）；
- [`cat1logsmod.py`](/script/cat1logs.py) -- `cat1logs.py` 的升级版，以更加直观的方式输出短信内容；
- [`init_cat1.py`](/script/init_cat1.py) -- 日志记录脚本，需要注册成服务在后台运行并设置开机启动；
- [`rst.py`](/script/rst.py) -- 重启 Cat1 模块，需要接线。
- [`sendat.py`](/script/sendat.py) -- 发送 AT 命令，用法：`python sendat.py <AT>`；
- [`sendbyhex.py`](/script/sendat.py) -- 以 16 进制发送文本内容，会自动在末尾加上 16 进制的 `Ctrl + Z`（即：`0x1A`），用法：`python sendbyhex.py <Content>`；
- [`sendsms.py`](/script/sendat.py) -- 发送短信，用法：`python sendsms.py <Phone Number> <SMS>`；

## `init_cat1.py` 的使用

将脚本妥善存储在某个位置（通常在 `/usr/local/bin/`），并给予其运行权限：

```bash
chmod +x init_cat1.py
```

创建一个 `systemd` 服务文件 `/etc/systemd/system/cat1_module.service`：

> 注意 `ExecStart=/usr/bin/python3 /path/to/init_cat1.py` 中的 `/path/to/init_cat1.py` 要为你脚本所存储的位置。

```service
[Unit]
Description=Initialize Cat1 Module and Log Serial Output
After=network.target dev-ttyS5.device

[Service]
Type=simple
ExecStart=/usr/bin/python3 /path/to/init_cat1.py
Restart=on-failure
RestartSec=5s
StartLimitInterval=30s
StartLimitBurst=3

[Install]
WantedBy=multi-user.target
```

应用并启用启动服务，查看状态：

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now cat1_module.service
sudo systemctl status cat1_module.service
```

查看日志输出：

```bash
tail -f /var/log/cat1_module.log
```

## `cat1logsmod.py` 的使用

需要一个辅助脚本 [`monitor_cat1log.sh`](/script/monitor_cat1log.sh)，该脚本借助 `inotifywait` 监控日志文件的变动，如果文件变动则执行 `cat1logsmod.py`。

配合对应的 `systemd` 服务 `/etc/systemd/system/monitor_log.service`

```service
[Unit]
Description=Monitor /var/log/cat1_module.log and execute script on change
After=network.target

[Service]
ExecStart=/path/to/monitor_cat1log.sh
Restart=always
User=root
Group=root

[Install]
WantedBy=multi-user.target
```