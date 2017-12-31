import Adafruit_CharLCD
from ui.lcd import LCD
from ui.cistern_ui import CisternUI
from recording.recorder_manager import RecorderManager
from logger import Logger

logger = Logger("Cistern: ")

class Cistern():
  def __init__(self, flow_meters):
    self.ui               = None
    self.lcd              = None
    self.recorder_manager = None
    self.flow_meters      = flow_meters
  
  def init(self):
    # initialize the LCD plate
    try:
      lcd_plate = Adafruit_CharLCD.Adafruit_CharLCDPlate()
    except IOError:
      logger.error("Error configuring LCD plate. Make sure it is connected.")
      raise
    
    self.lcd = LCD(lcd_plate)
    
    # initialize the ui
    self.ui = CisternUI(self.lcd, self.flow_meters);
    
    # initalize the recorder manager
    self.recorder_manager = RecorderManager(self.flow_meters)
  
  
  def start(self):
    logger.info("starting")
    
    # start the flow meters
    logger.info("starting flow meters")
    for flow_meter in self.flow_meters:
      flow_meter.start()
    
    # start the UI
    logger.info("starting UI")
    self.ui.start()
    
    # start the recorder manager
    self.recorder_manager.start()
    
    logger.info("started")
  
  def stop(self):
    logger.info("stopping")
    
    # stop the flow meters
    logger.info("stopping flow meters")
    for flow_meter in self.flow_meters:
      flow_meter.stop()
      flow_meter.join()
    
    # stop the UI
    logger.info("stopping UI")
    if self.ui != None:
      self.ui.stop()
      self.ui.join()
    
    # stop the recorder manager
    if self.recorder_manager != None:
      self.recorder_manager.stop()
      self.recorder_manager.join()
    
    logger.info("stopped")
  
  def is_alive(self):
    if not self.ui.isAlive():
      return False
    
    if not self.recorder_manager.isAlive():
      return False
    
    for flow_meter in self.flow_meters:
      if not flow_meter.isAlive():
        return False
    
    return True