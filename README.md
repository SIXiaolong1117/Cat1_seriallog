# Cat1 模块串口日志记录与短信内容解码

在 [`script`](/script) 目录下存在两个脚本：

- `init_cat1.py` -- 日志记录脚本，需要注册成服务在后台运行并设置开机启动；
- `cat1logs.py` -- 对日志中的短信内容进行解码（UnicodeBE）。

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