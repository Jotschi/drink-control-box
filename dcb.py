#!/usr/bin/python

import RPi.GPIO as GPIO
import time
 
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
#B4 = 4
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
 
def main():
  # Main program block
  GPIO.setwarnings(False)
  GPIO.setmode(GPIO.BCM)       # Use BCM GPIO numbers
  GPIO.setup(LCD_E, GPIO.OUT)  # E
  GPIO.setup(LCD_RS, GPIO.OUT) # RS
  GPIO.setup(LCD_D4, GPIO.OUT) # DB4
  GPIO.setup(LCD_D5, GPIO.OUT) # DB5
  GPIO.setup(LCD_D6, GPIO.OUT) # DB6
  GPIO.setup(LCD_D7, GPIO.OUT) # DB7
  GPIO.setup(LED_TOGGLE, GPIO.OUT)
  GPIO.setup(B1, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(B2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(B3, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#  GPIO.setup(B4, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  GPIO.setup(REED, GPIO.IN)
  GPIO.setup(BAR, GPIO.OUT)
#  GPIO.setup(B4, GPIO.IN)
  GPIO.setup(L1, GPIO.OUT) 
  GPIO.setup(L2, GPIO.OUT)
  GPIO.setup(L3, GPIO.OUT)
  GPIO.add_event_detect(B1, GPIO.RISING, callback=b1callback, bouncetime=300)
  GPIO.add_event_detect(B2, GPIO.RISING, callback=b2callback, bouncetime=300)
  GPIO.add_event_detect(B3, GPIO.RISING, callback=b3callback, bouncetime=300)
#  GPIO.add_event_detect(B4, GPIO.RISING, callback=b4callback, bouncetime=300)
  GPIO.add_event_detect(REED, GPIO.FALLING, callback=reedCallback, bouncetime=300)


  # Initialise display
  lcd_init()
 
  while True:
 
    # Send some test
    lcd_string("Rasbperry Pi",LCD_LINE_1)
    lcd_string("16x2 LCD Test",LCD_LINE_2)
 
    time.sleep(3) # 3 second delay
 
    # Send some text
    lcd_string("1234567890123456",LCD_LINE_1)
    lcd_string("abcdefghijklmnop",LCD_LINE_2)
 
    time.sleep(3) # 3 second delay
 
    # Send some text
    lcd_string("RaspberryPi-spy",LCD_LINE_1)
    lcd_string(".co.uk",LCD_LINE_2)
 
    time.sleep(3)
 
    # Send some text
    lcd_string("Follow me on",LCD_LINE_1)
    lcd_string("Twitter @RPiSpy",LCD_LINE_2)
 
    time.sleep(3)

def triggerBar():
  GPIO.output(BAR, 255)
  time.sleep(1)
  GPIO.output(BAR, 0)
  
def reedCallback(channel):
  print("REED")

def b1callback(channel):
  print("CALLED 1")
  toggleLED()

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
  

def blib():
  GPIO.output(L1, 255)
  GPIO.output(L2, 255)     
  GPIO.output(L3, 255)     
  time.sleep(1)
  GPIO.output(L1, 0) 
  GPIO.output(L2, 0)     
  GPIO.output(L3, 0)     

 
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
