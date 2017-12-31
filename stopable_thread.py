import time
import threading
import Adafruit_CharLCD as LCD

class StopableThread(threading.Thread):
  def __init__(self, name):
    threading.Thread.__init__(self, name=name)
    self.should_stop = False
  
  def stop(self):
    if self.should_stop:
      return
    
    self.should_stop = True
    self.on_stop()
  
  def on_stop(self):
    return