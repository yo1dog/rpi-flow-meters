import time
import Adafruit_CharLCD
import config
from stopable_thread import StopableThread
from button import Button
from logger import Logger

logger = Logger("InputManager: ")


# TODO: replace polling with interrupt?
class InputManager(StopableThread):
  def __init__(self, lcd):
    StopableThread.__init__(self, "InputManager")
    
    self.lcd = lcd
    
    # initialize the buttons
    self.up_button     = Button()
    self.down_button   = Button()
    self.left_button   = Button()
    self.right_button  = Button()
    self.select_button = Button()
  
  def update_buttons(self):
    self.up_button    .set_is_pressed(self.lcd.plate.is_pressed(Adafruit_CharLCD.UP    ))
    self.down_button  .set_is_pressed(self.lcd.plate.is_pressed(Adafruit_CharLCD.DOWN  ))
    self.left_button  .set_is_pressed(self.lcd.plate.is_pressed(Adafruit_CharLCD.LEFT  ))
    self.right_button .set_is_pressed(self.lcd.plate.is_pressed(Adafruit_CharLCD.RIGHT ))
    self.select_button.set_is_pressed(self.lcd.plate.is_pressed(Adafruit_CharLCD.SELECT))
  
  
  def run(self):
    logger.info("started")
    
    try:
      while not self.should_stop:
        self.update_buttons()
        time.sleep(config.ui_poll_buttons_freq_s)
    except:
      logger.last_exception()
      logger.error("exception raised")
    
    logger.info("stopping")
    logger.info("ended")
  
  def on_stop(self):
    logger.info("stop requested")