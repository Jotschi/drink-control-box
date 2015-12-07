#!/usr/bin/python

import os

def readBarcode():
  f = open("/dev/tty0")
  while True:
    r = f.read(1)
    #f.seek(-1,1)
    print("R:" + r)
  f.close()
  return code

while True:
  code = readBarcode()
  print("Code:" + code)

