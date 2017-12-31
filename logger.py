from datetime import datetime
import sys
import config
import traceback
import sys

class Logger:
  def __init__(self, prefix = ""):
    self.prefix = prefix
  
  def info(self, v):
    sys.stdout.write(self.format(v))
    sys.stdout.flush()
  
  def error(self, v):
    sys.stderr.write(self.format(v))
    sys.stderr.flush()
  
  def debug(self, v):
    if config.enable_debug_logging:
      self.info(v)
  
  def last_exception(self, prefix = ""):
    self.error(prefix + self.format_last_exception())
  
  
  def format(self, v):
    return "[" + datetime.now().isoformat() + "] " + self.prefix + str(v) + "\n"
  
  def format_last_exception(self):
    return traceback.format_exc(sys.exc_info()).rstrip()