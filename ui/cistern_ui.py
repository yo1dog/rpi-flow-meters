import threading
import time
import math
import Adafruit_CharLCD as LCD
import config
from stopable_thread import StopableThread
from flow_meters_page import FlowMetersPage
from input_manager import InputManager


class CisternUI(StopableThread):
  def __init__(self, lcd, flow_meters):
    StopableThread.__init__(self)
    
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
    
    # turn on the LCD
    self.turn_on_lcd()
  
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
      self.pages[0].draw_init(self.lcd)
  
  def turn_off_lcd(self):
    # clear, turn off the backlight, and disable
    with self.lcd_lock:
      self.lcd.clear()
      self.lcd.plate.set_backlight(0)
      self.lcd.plate.enable_display(False)
  
  def draw_page_init(self, page):
    with self.lcd_lock:
      page.draw_init(self.lcd)
  
  def draw_page_update(self, page):
    with self.lcd_lock:
      page.draw_update(self.lcd)
  
  def go_to_next_page(self):
    if len(self.pages) < 2:
      return
    
    with self.ui_lock:
      self.page_num += 1
      if self.page_num >= len(self.pages):
        self.page_num = 0
      
      self.draw_page_init(self.pages[self.page_num])
  
  def go_to_prev_page(self):
    if len(self.pages) < 2:
      return
    
    with self.ui_lock:
      self.page_num -= 1
      if self.page_num < 0:
        self.page_num = len(self.pages) - 1
      
      self.draw_page_init(self.pages[self.page_num])
  
  def on_up_pressed(self, button):
    self.go_to_prev_page()
  
  def on_down_pressed(self, button):
    self.go_to_next_page()
  
  
  def run(self):
    print "Starting UI thread"
    
    # start the input manager
    self.input_manager.start()
    
    while not self.should_stop:
      self.draw_page_update(self.pages[self.page_num])
      time.sleep(config.ui_redraw_page_freq_s)
      
    print "UI thread end"
  
  def stop(self):
    print "Stopping UI thread"
    
    self.input_manager.stop()
    self.turn_off_lcd()
    
    StopableThread.stop(self)
