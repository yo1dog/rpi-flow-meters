import time
import Adafruit_CharLCD
import config
from stopable_thread import StopableThread
from button import Button


# TODO: replace polling with interrupt?
class InputManager(StopableThread):
  def __init__(self, lcd):
    StopableThread.__init__(self)
    
    self.lcd = lcd
    
    # initialize the buttons
    self.up_button     = Button()
    self.down_button   = Button()
    self.left_button   = Button()
    self.right_button  = Button()
    self.select_button = Button()
  
  def run(self):
    print "Starting input manager thread"
    
    while not self.should_stop:
      self.update_buttons()
      time.sleep(config.ui_poll_buttons_freq_s)
    
    print "Input manager thread end"
  
  def update_buttons(self):
    self.up_button    .set_is_pressed(self.lcd.plate.is_pressed(Adafruit_CharLCD.UP    ))
    self.down_button  .set_is_pressed(self.lcd.plate.is_pressed(Adafruit_CharLCD.DOWN  ))
    self.left_button  .set_is_pressed(self.lcd.plate.is_pressed(Adafruit_CharLCD.LEFT  ))
    self.right_button .set_is_pressed(self.lcd.plate.is_pressed(Adafruit_CharLCD.RIGHT ))
    self.select_button.set_is_pressed(self.lcd.plate.is_pressed(Adafruit_CharLCD.SELECT))
  
  def stop(self):
    print "Stopping input manager thread"
    StopableThread.stop(self)