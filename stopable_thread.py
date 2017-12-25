import time
import threading
import Adafruit_CharLCD as LCD

class StopableThread(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.should_stop = False
  
  def stop(self):
    self.should_stop = True