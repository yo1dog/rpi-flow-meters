import threading
import math
import Adafruit_CharLCD as LCD
import config
from stopable_thread import StopableThread
from stepped_sleep import stepped_sleep
from flow_meters_page import FlowMetersPage
from input_manager import InputManager
from logger import Logger

logger = Logger("CisternUI: ")


class CisternUI(StopableThread):
  def __init__(self, lcd, flow_meters):
    StopableThread.__init__(self, "CisternUI")
    
    self.lcd         = lcd
    self.flow_meters = flow_meters
    
    self.ui_lock  = threading.Lock()
    self.lcd_lock = threading.Lock()
    
    # initialize the pages
    self.pages = self.create_pages(self.lcd, self.flow_meters)
    self.page_num = 0
    
    # initialize the input manager
    self.input_manager = InputManager(self.lcd)
    
    # bind inputs
    self.input_manager.up_button  .on_pressed_callback = self.on_up_pressed
    self.input_manager.down_button.on_pressed_callback = self.on_down_pressed
  
  def create_pages(self, lcd, flow_meters):
    pages = [FlowMetersPage()]
    
    for flow_meter in flow_meters:
      last_page = pages[len(pages) - 1]
      
      # start a new page if the last page is full
      if len(last_page.flow_meters) == lcd.num_rows:
        last_page = FlowMetersPage()
        pages.append(last_page)
      
      # add the flow meter to the last page
      last_page.flow_meters.append(flow_meter)
    
    return pages
  
  def turn_on_lcd(self):
    # enable, turn on the backlight, clear, and draw the first page
    with self.lcd_lock:
      self.lcd.plate.enable_display(True)
      self.lcd.plate.set_backlight(1)
      self.lcd.clear()
      self.pages[0].draw(self.lcd)
  
  def turn_off_lcd(self):
    # clear, turn off the backlight, and disable
    with self.lcd_lock:
      self.lcd.clear()
      self.lcd.plate.set_backlight(0)
      self.lcd.plate.enable_display(False)
  
  def draw_page(self, page):
    with self.lcd_lock:
      page.draw(self.lcd)
  
  def go_to_next_page(self):
    if len(self.pages) < 2:
      return
    
    with self.ui_lock:
      self.page_num += 1
      if self.page_num >= len(self.pages):
        self.page_num = 0
      
      self.draw_page(self.pages[self.page_num])
  
  def go_to_prev_page(self):
    if len(self.pages) < 2:
      return
    
    with self.ui_lock:
      self.page_num -= 1
      if self.page_num < 0:
        self.page_num = len(self.pages) - 1
      
      self.draw_page(self.pages[self.page_num])
  
  def on_up_pressed(self, button):
    self.go_to_prev_page()
  
  def on_down_pressed(self, button):
    self.go_to_next_page()
  
  
  def should_run(self):
    return (
      (not self.should_stop) and
      self.input_manager.isAlive()
    )
  
  def run(self):
    logger.info("started")
    
    # start the input manager
    logger.info("starting input manager")
    self.input_manager.start()
    
    # turn on the LCD
    logger.info("turning on LCD")
    self.turn_on_lcd()
    
    try:
      # loop forever until we are told to stop
      while self.should_run():
        # draw the current page then wait the configured interval
        self.draw_page(self.pages[self.page_num])
        stepped_sleep(config.ui_redraw_page_freq_s, config.global_sleep_step_s, self.should_run)
    except:
      logger.last_exception()
      logger.error("exception raised")
    
    logger.info("stopping")
    
    # stop the input manager
    logger.info("stopping input manager")
    self.input_manager.stop()
    self.input_manager.join()
    
    # turn off the LCD
    logger.info("turning off LCD")
    self.turn_off_lcd()
    
    logger.info("ended")
  
  def on_stop(self):
    logger.info("stop requested")
    
    
