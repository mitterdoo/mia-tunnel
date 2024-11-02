'''
miniMIA
By Connor Ashcroft
& Justin O'Reilly

To be run on Raspberry Pi 4B running Arch Linux
'''

from time import sleep, time
from RPi import GPIO
from subprocess import run
import lcd
import re
import signal

VERSION = "MINIMIA 1.2.0" # max 16 chars

f = open("/usr/bin/mia-tunnel/mia_ip.txt",'r')
TAILSCALE_IP = f.read().strip()
f.close()

class GracefulExit():
	kill = False
	def __init__(self):
		signal.signal(signal.SIGINT, self.exit)
		signal.signal(signal.SIGTERM, self.exit)

	def exit(self, signum, frame):
		self.kill = True

IP_SAFE_PATTERN = re.compile(r"^[\dA-Za-z\.-]+$")

def isIPSafe(ip: str):
	if not IP_SAFE_PATTERN.search(ip):
		return False
	return True

def checkConnectionTo(ip: str):
	'''
	Returns whether the device can connect to a given IP/domain.
	'''
	ip = ip.strip()

	if not isIPSafe(ip):
		raise ValueError(f'IP or domain contains illegal characters ("{str(ip)}")')

	result = run(f'ping -W 3 -i 0.25 -c 4 {ip}', shell=True, capture_output=True, text=True)
	return result.returncode == 0

IP_PATTERN = re.compile(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}")
def verifyConnection():
	'''
	Checks if this device has a connection to the Tailscale device
	'''

	# check if connected to ethernet, first
	result = run("ifconfig end0| grep 'inet' -m 1 | awk '{print $2}'", shell=True, capture_output=True, text=True)
	out = result.stdout.strip()
	err = result.stderr.strip()

	if len(err) > 0:
		return False, err, None
	elif not IP_PATTERN.search(out):
		return False, "END0 DISCONNECT", None

	localip = out
	# local ip is good, check gateway connection
	# end0 connection SHOULD imply there's a gateway, but it wouldn't hurt to check..
	# first, obtain gateway
	
	result = run("ip r|grep ^def|awk '{print $3}'", shell=True, capture_output=True, text=True)
	out = result.stdout.strip()

	if len(out) == 0:
		return False, "NO GATEWAY", localip
	elif not isIPSafe(out): # this shouldn't spit out a weird ip... hoping this never happens
		return False, "@" + str(out), localip
	elif not checkConnectionTo(out):
		return False, "GATEWAY TIMEOUT", localip

	# gateway good, check internet
	if not checkConnectionTo('8.8.8.8'):
		return False, "INTERNET TIMEOUT", localip

	# internet good, now check Tailscale machine
	if not checkConnectionTo(TAILSCALE_IP):
		return False, "MIA TIMEOUT", localip

	return True, localip, None
if __name__ == '__main__':
	x = lcd.LCD(*lcd.DEFAULT_LCD)
	print('Minimia start')
	x.backlight(1)
	x.set(VERSION, 'BY CONNOR A 2024')
	sleep(2.5)
	x.set(VERSION, '& JUSTIN O. 2024')
	sleep(2.5)
	
	exiter = GracefulExit()
	times = 0
	nextCheck = time() - 1
	print('Check connection loop START')
	x.set('CHECKING','CONNECTION...')
	while not exiter.kill:
		try:
			t = time()
			if t >= nextCheck:
				nextCheck = t + 12
				#x.clear()
				#x.home()
				ok, ip, errIp = verifyConnection()
				if not ok:
					print(f'Connection FAILURE: {str(ip)}')
					x.set("ERROR", ip)
					x.backlight(1) # turn display on if we found an error
					if errIp != None:
						sleep(5)
						x.set(ip, errIp)
					times = 0
				else:
					print(f'Connection SUCCESS (ip: {str(ip)})')
					if times == 2: # turn off display after 30 seconds (when we're connected)
						x.backlight(0)
					x.set("OK", ip)
					if times == 0:
						for i in range(5):
							x.backlight(1)
							sleep(0.05)
							x.backlight(0)
							sleep(0.05)
							x.backlight(1)
					times += 1
					
			sleep(0.1)
		except KeyboardInterrupt:
			break

	print("\nEXITING...")
	x.clear()
	x.home()
	x.backlight(1)
	x.print("GOODBYE")
	sleep(2)
	x.clear()
	x.backlight(0)
	GPIO.cleanup()

