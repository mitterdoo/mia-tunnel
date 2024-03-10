'''
Python 1602A LCD module

By Connor "Ranthos" Ashcroft
Mar. 1, 2024
'''

import RPi.GPIO as GPIO
from time import sleep, time
from subprocess import run
import re
import signal

class GracefulExit():
	kill = False
	def __init__(self):
		signal.signal(signal.SIGINT, self.exit)
		signal.signal(signal.SIGTERM, self.exit)

	def exit(self, signum, frame):
		self.kill = True

# Options for register select (RS pin)
REG_DATA = True
REG_INSTR = False

# Constants defined from Adruino library LiquidCrystal.h
# commands
LCD_CLEARDISPLAY = 0x01
LCD_RETURNHOME = 0x02
LCD_ENTRYMODESET = 0x04
LCD_DISPLAYCONTROL = 0x08
LCD_CURSORSHIFT = 0x10
LCD_FUNCTIONSET = 0x20
LCD_SETCGRAMADDR = 0x40
LCD_SETDDRAMADDR = 0x80

# flags for display entry mode
LCD_ENTRYRIGHT = 0x00
LCD_ENTRYLEFT = 0x02
LCD_ENTRYSHIFTINCREMENT = 0x01
LCD_ENTRYSHIFTDECREMENT = 0x00

# flags for display on/off control
LCD_DISPLAYON = 0x04
LCD_DISPLAYOFF = 0x00
LCD_CURSORON = 0x02
LCD_CURSOROFF = 0x00
LCD_BLINKON = 0x01
LCD_BLINKOFF = 0x00

# flags for display/cursor shift
LCD_DISPLAYMOVE = 0x08
LCD_CURSORMOVE = 0x00
LCD_MOVERIGHT = 0x04
LCD_MOVELEFT = 0x00

# flags for function set
LCD_8BITMODE = 0x10
LCD_4BITMODE = 0x00
LCD_2LINE = 0x08
LCD_1LINE = 0x00
LCD_5x10DOTS = 0x04
LCD_5x8DOTS = 0x00

class LCD:

	# Creates an LCD display class using the specified pins. This uses 4-bit mode only and is for a 16x2, because I'm lazy. sorry.
	def __init__(self, pin_RS, pin_E, pin_D4, pin_D5, pin_D6, pin_D7, pin_A):
		self.pin_RS = pin_RS
		self.pin_E = pin_E
		self.pin_D4 = pin_D4
		self.pin_D5 = pin_D5
		self.pin_D6 = pin_D6
		self.pin_D7 = pin_D7
		self.pin_A = pin_A

		self.cols = 16
		self.rows = 2

		self.dataPins = [
			pin_D4,
			pin_D5,
			pin_D6,
			pin_D7
		]

		self.rowOffsets = [0x00, 0x40]

		self.displayFunction = LCD_4BITMODE | LCD_2LINE | LCD_5x8DOTS
		self.displayMode = LCD_ENTRYLEFT | LCD_ENTRYSHIFTDECREMENT
		self.displayControl = LCD_DISPLAYON | LCD_CURSOROFF | LCD_BLINKOFF

		# GPIO.setwarnings(False)
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(pin_RS, GPIO.OUT)
		GPIO.setup(pin_E, GPIO.OUT)
		GPIO.setup(pin_D4, GPIO.OUT)
		GPIO.setup(pin_D5, GPIO.OUT)
		GPIO.setup(pin_D6, GPIO.OUT)
		GPIO.setup(pin_D7, GPIO.OUT)
		GPIO.setup(pin_A, GPIO.OUT)
		self.brightnessPWM = GPIO.PWM(pin_A, 1000)
		self.brightnessPWM.start(0)

		GPIO.output(pin_RS, False)
		GPIO.output(pin_E, False)

		# 4 bit mode

		self.write4bits(0x03)
		sleep(0.0045)
		#sleep(0.1)

		self.write4bits(0x03)
		sleep(0.0045)
		#sleep(0.1)

		self.write4bits(0x03)
		sleep(0.00015)
		#sleep(0.1)

		self.write4bits(0x02)


		self.command(LCD_FUNCTIONSET | self.displayFunction)
		self.display()
		self.clear()
		self.command(LCD_ENTRYMODESET | self.displayMode)

	def clear(self):
		self.command(LCD_CLEARDISPLAY)
		sleep(0.002)
		#sleep(0.1)

	def home(self):
		self.command(LCD_RETURNHOME)
		sleep(0.002)
		#sleep(0.1)

	def setCursor(self, col: int, row: int):
		if (row >= len(self.rowOffsets)):
			row = len(self.rowOffsets)-1

		self.command(LCD_SETDDRAMADDR | (col + self.rowOffsets[row]))

	def noDisplay(self):
		self.displayControl &= ~LCD_DISPLAYON
		self.command(LCD_DISPLAYCONTROL | self.displayControl)

	def display(self):
		self.displayControl |= LCD_DISPLAYON
		self.command(LCD_DISPLAYCONTROL | self.displayControl)

	def noCursor(self):
		self.displayControl &= ~LCD_CURSORON
		self.command(LCD_DISPLAYCONTROL | self.displayControl)

	def cursor(self):
		self.displayControl |= LCD_CURSORON
		self.command(LCD_DISPLAYCONTROL | self.displayControl)

	def noBlink(self):
		self.displayControl &= ~LCD_BLINKON
		self.command(LCD_DISPLAYCONTROL | self.displayControl)

	def blink(self):
		self.displayControl |= LCD_BLINKON
		self.command(LCD_DISPLAYCONTROL | self.displayControl)

	def scrollDisplayLeft(self):
		self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVELEFT)

	def scrollDisplayRight(self):
		self.command(LCD_CURSORSHIFT | LCD_DISPLAYMOVE | LCD_MOVERIGHT)

	def leftToRight(self):
		self.displayMode |= LCD_ENTRYLEFT
		self.command(LCD_ENTRYMODESET | self.displayMode)

	def rightToLeft(self):
		self.displayMode &= ~LCD_ENTRYLEFT
		self.command(LCD_ENTRYMODESET | self.displayMode)

	def autoscroll(self):
		self.displayMode |= LCD_ENTRYSHIFTINCREMENT
		self.command(LCD_ENTRYMODESET | self.displayMode)

	def noAutoscroll(self):
		self.displayMode &= ~LCD_ENTRYSHIFTINCREMENT
		self.command(LCD_ENTRYMODESET | self.displayMode)

	def command(self, value: int):
		self.send(value, REG_INSTR)

	def write(self, value: int):
		self.send(value, REG_DATA)

	def send(self, value: int, mode: int):
		GPIO.output(self.pin_RS, mode)
		self.write4bits(value >> 4)
		self.write4bits(value)

	def pulseEnable(self):
		GPIO.output(self.pin_E, False)
		sleep(0.001)
		#sleep(0.1)
		GPIO.output(self.pin_E, True)
		sleep(0.001)
		#sleep(0.1)
		GPIO.output(self.pin_E, False)
		sleep(0.001)
		#sleep(0.1)

	def write4bits(self, value: int):
		for i in range(4):
			GPIO.output(self.dataPins[i], (value >> i) & 0x01)
		self.pulseEnable()

	def write8bits(self, value: int):
		raise NotImplementedError

	def backlight(self, brightness: float):
		#GPIO.output(self.pin_A, enable)
		self.brightnessPWM.ChangeDutyCycle(brightness*100)

	def print(self, string: str):
		b = string.encode()
		for char in b:
			self.write(char)

	def set(self, line1: str, line2: str):
		if not line1:
			line1 = ''
		
		if not line2:
			line2 = ''
		
		self.clear()
		self.home()
		self.print(line1[:16])
		self.setCursor(0, 1)
		self.print(line2[:16])

DEFAULT_LCD = (15, 16, 21, 22, 23, 24, 12)
