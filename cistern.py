#!/usr/bin/python

# use GPIO pin numbering instead of PCB pin numbering
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

import time
import config
import Adafruit_CharLCD
from ui.lcd import LCD
from ui.cistern_ui import CisternUI

class Cistern():
  def __init__(self, flow_meters):
    self.ui          = None
    self.lcd         = None
    self.flow_meters = flow_meters
  
  def init(self):
    # initialize the LCD plate
    try:
      lcd_plate = Adafruit_CharLCD.Adafruit_CharLCDPlate()
    except IOError:
      print "Error configuring LCD plate. Make sure it is connected."
      raise
    
    self.lcd = LCD(lcd_plate)
    
    # initialize the ui
    self.ui = CisternUI(self.lcd, self.flow_meters);
  
  
  def start(self): 
    # start the flow meters
    for flow_meter in self.flow_meters:
      flow_meter.start()
    
    # start the UI
    self.ui.start()
    
  def stop(self):
    # stop all child threads
    for flow_meter in self.flow_meters:
      flow_meter.stop()
    
    if self.ui != None:
      self.ui.stop()


# entry point
cistern = Cistern(config.flow_meters)

try:
  cistern.init()
  cistern.start()
  
  # keep the main thread alive to listen for keyboard interrupts (^C)
  while True:
    time.sleep(1)
  
except KeyboardInterrupt:
  print "Interrupted"
  cistern.stop()
except:
  cistern.stop()
  raise