#!/usr/bin/python


import pygame
from threading import Thread
from sys import stdin
import RPi.GPIO as GPIO
import time
import sys
from evdev import InputDevice, categorize, ecodes
dev = InputDevice('/dev/input/event0')

# Provided as an example taken from my own keyboard attached to a Centos 6 box:
scancodes = {
    # Scancode: ASCIICode
    0: None, 1: u'ESC', 2: u'1', 3: u'2', 4: u'3', 5: u'4', 6: u'5', 7: u'6', 8: u'7', 9: u'8',
    10: u'9', 11: u'0', 12: u'-', 13: u'=', 14: u'BKSP', 15: u'TAB', 16: u'Q', 17: u'W', 18: u'E', 19: u'R',
    20: u'T', 21: u'Y', 22: u'U', 23: u'I', 24: u'O', 25: u'P', 26: u'[', 27: u']', 28: u'CRLF', 29: u'LCTRL',
    30: u'A', 31: u'S', 32: u'D', 33: u'F', 34: u'G', 35: u'H', 36: u'J', 37: u'K', 38: u'L', 39: u';',
    40: u'"', 41: u'`', 42: u'LSHFT', 43: u'\\', 44: u'Z', 45: u'X', 46: u'C', 47: u'V', 48: u'B', 49: u'N',
    50: u'M', 51: u',', 52: u'.', 53: u'/', 54: u'RSHFT', 56: u'LALT', 100: u'RALT'
}

pygame.mixer.init()

LCD_RS = 25
LCD_E  = 24
LCD_D4 = 23
LCD_D5 = 14
LCD_D6 = 31
LCD_D7 = 30
LED_TOGGLE = 22
B1 = 18 
B2 = 15
B3 = 27
B4 = 29

L1 = 8
L2 = 17
L3 = 28

REED = 4
BAR = 2
 
# Define some device constants
LCD_WIDTH = 16    # Maximum characters per line
LCD_CHR = True
LCD_CMD = False
 
LCD_LINE_1 = 0x80 # LCD RAM address for the 1st line
LCD_LINE_2 = 0xC0 # LCD RAM address for the 2nd line
 
# Timing constants
E_PULSE = 0.0005
E_DELAY = 0.0005

LEDFlag = False



 
def setupPins():
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(LCD_E, GPIO.OUT)
  GPIO.setup(LCD_RS, GPIO.OUT)
  GPIO.setup(LCD_D4, GPIO.OUT)
  GPIO.setup(LCD_D5, GPIO.OUT)
  GPIO.setup(LCD_D6, GPIO.OUT)
  GPIO.setup(LCD_D7, GPIO.OUT)
  GPIO.setup(LED_TOGGLE, GPIO.OUT)
  GPIO.setup(B1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(B2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(B3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(B4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(REED, GPIO.IN)
  GPIO.setup(BAR, GPIO.OUT)
  GPIO.setup(L1, GPIO.OUT) 
  GPIO.setup(L2, GPIO.OUT)
  GPIO.setup(L3, GPIO.OUT)
  GPIO.add_event_detect(B1, GPIO.RISING, callback=b1callback, bouncetime=300)
  GPIO.add_event_detect(B2, GPIO.RISING, callback=b2callback, bouncetime=300)
  GPIO.add_event_detect(B3, GPIO.RISING, callback=b3callback, bouncetime=300)
  GPIO.add_event_detect(B4, GPIO.RISING, callback=b4callback, bouncetime=300)
  GPIO.add_event_detect(REED, GPIO.FALLING, callback=reedCallback, bouncetime=300)
  lcd_init()

def readBarcode():
  code = ""
  for event in dev.read_loop():
    if event.type == ecodes.EV_KEY:
      data = categorize(event)
      if data.keystate == 1:  
        if data.scancode == 28:  
          return code
        else:
          code += scancodes.get(data.scancode) or u'UNKNOWN:{}'.format(data.scancode)

def handleReads():
  while True:
    code = readBarcode()
    print("Code:" + code)
    lcd_string("Code:", LCD_LINE_1)
    lcd_string(code,    LCD_LINE_2)
  
def main():
  setupPins()
  readerThread = Thread(target=handleReads)
  readerThread.start()

  for i in range(255):
    GPIO.output(LED_TOGGLE, i)
  
  while True:
    time.sleep(0.1)

  #  triggerBar()

  #while True:
  #  # Send some test
  #  lcd_string("Rasbperry Pi",LCD_LINE_1)
  #  lcd_string("16x2 LCD Test",LCD_LINE_2)
# 
#    time.sleep(3) # 3 second delay
# 
#    # Send some text
#    lcd_string("1234567890123456",LCD_LINE_1)
#    lcd_string("abcdefghijklmnop",LCD_LINE_2)
# 
#    time.sleep(3) # 3 second delay
# 
#    # Send some text
#    lcd_string("RaspberryPi-spy",LCD_LINE_1)
#    lcd_string(".co.uk",LCD_LINE_2)
# 
#    time.sleep(3)
# 
#    # Send some text
#    lcd_string("Follow me on",LCD_LINE_1)
#    lcd_string("Twitter @RPiSpy",LCD_LINE_2)
# 
#    time.sleep(3)

def triggerBar():
  GPIO.output(BAR, 255)
  time.sleep(0.525)
  GPIO.output(BAR, 0)
  time.sleep(0.525)
  
def reedCallback(channel):
  print("REED")

def b1callback(channel):
  print("CALLED 1")
  toggleLED()
  playWarning()

def b2callback(channel):
  print("CALLED 2")
  triggerBar()

def b3callback(channel):
  print("CALLED 3")
  blib()

def b4callback(channel):
  print("CALLED 4")

def buttons():
  b1in = GPIO.input(B1)
  if b1in:
    print("PRESSED")
  else:
    print("NOT PRESSED")

def playWarning():
  pygame.mixer.music.load("warning.mp3")
  pygame.mixer.music.play()
  while pygame.mixer.music.get_busy() == True:
    continue


def fadeLED(led):
  p = GPIO.PWM(led, 255)
  fid = 0.015
  fod = 0.005
  mid = 0.200
  p.start(0)
  while True:
    for i in range(0,100):
      p.ChangeDutyCycle(i)
      time.sleep(fid)
    for i in range(100, 1, -1):
      p.ChangeDutyCycle(i)
      time.sleep(fod)
    p.ChangeDutyCycle(0)
    time.sleep(mid)
  p.stop()


def blib():
  print("Blib")
  faderThread = Thread(target=fadeLED, args=(L1,))
  faderThread.start()
  faderThread = Thread(target=fadeLED, args=(L2,))
  faderThread.start()
  faderThread = Thread(target=fadeLED, args=(L3,))
  faderThread.start()
  #GPIO.output(L1, 255)
  #GPIO.output(L2, 255)     
  #GPIO.output(L3, 255)     
  #time.sleep(1)
  #GPIO.output(L1, 0) 
  #GPIO.output(L2, 0)     
  #GPIO.output(L3, 0)     

 
def lcd_init():
  # Initialise display
  lcd_byte(0x33,LCD_CMD) # 110011 Initialise
  lcd_byte(0x32,LCD_CMD) # 110010 Initialise
  lcd_byte(0x06,LCD_CMD) # 000110 Cursor move direction
  lcd_byte(0x0C,LCD_CMD) # 001100 Display On,Cursor Off, Blink Off
  lcd_byte(0x28,LCD_CMD) # 101000 Data length, number of lines, font size
  lcd_byte(0x01,LCD_CMD) # 000001 Clear display
  time.sleep(E_DELAY)
 
def lcd_byte(bits, mode):
  # Send byte to data pins
  # bits = data
  # mode = True  for character
  #        False for command
 
  GPIO.output(LCD_RS, mode) # RS
 
  # High bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x10==0x10:
    GPIO.output(LCD_D4, True)
  if bits&0x20==0x20:
    GPIO.output(LCD_D5, True)
  if bits&0x40==0x40:
    GPIO.output(LCD_D6, True)
  if bits&0x80==0x80:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
  # Low bits
  GPIO.output(LCD_D4, False)
  GPIO.output(LCD_D5, False)
  GPIO.output(LCD_D6, False)
  GPIO.output(LCD_D7, False)
  if bits&0x01==0x01:
    GPIO.output(LCD_D4, True)
  if bits&0x02==0x02:
    GPIO.output(LCD_D5, True)
  if bits&0x04==0x04:
    GPIO.output(LCD_D6, True)
  if bits&0x08==0x08:
    GPIO.output(LCD_D7, True)
 
  # Toggle 'Enable' pin
  lcd_toggle_enable()
 
def lcd_toggle_enable():
  # Toggle enable
  time.sleep(E_DELAY)
  GPIO.output(LCD_E, True)
  time.sleep(E_PULSE)
  GPIO.output(LCD_E, False)
  time.sleep(E_DELAY)
  
def toggleLED():
  global LEDFlag
  LEDFlag = not LEDFlag
  GPIO.output(LED_TOGGLE, LEDFlag)

def lcd_string(message,line):
  # Send string to display
  message = message.ljust(LCD_WIDTH," ")
 
  lcd_byte(line, LCD_CMD)
 
  for i in range(LCD_WIDTH):
    lcd_byte(ord(message[i]),LCD_CHR)
 
if __name__ == '__main__':
 
  try:
    main()
  except KeyboardInterrupt:
    pass
  finally:
    lcd_byte(0x01, LCD_CMD)
    lcd_string("Goodbye!",LCD_LINE_1)
    GPIO.cleanup()
