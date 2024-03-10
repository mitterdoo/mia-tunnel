Startup service should be located in /etc/systemd/system/mia.service

Then run
	sudo systemctl daemon-reload
	sudo systemctl enable mia
	sudo systemctl start mia

`enable` to run service automatically on boot
`start` to manually start service

`disable` to disable auto-start
`stop` to stop service

For viewing logs, use 
	sudo journalctl -u mia.service


Shell dependencies:
iptables
python3
ping
ifconfig
awk
ip

Python dependencies:
RPi

Python code expects ethernet adapter to be named "end0"