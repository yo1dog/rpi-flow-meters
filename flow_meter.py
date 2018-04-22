import threading
import time
import math
import re
import RPi.GPIO as GPIO
import config
from stopable_thread import StopableThread
from stepped_sleep import stepped_sleep
from logger import Logger

class FlowMeter(StopableThread):
  def __init__(self, id, gpio_pin, volume_per_interrupt_ml):
    # ID must contain only letters, numbers, and spaces
    #if not re.match(r"^[a-zA-Z0-9 ]+$", id):
    #   raise ValueError("Flow meter ID must contain only letters, numbers, and spaces.")
    
    StopableThread.__init__(self, "Flow Meter - " + id)
    
    self.id                                   = id                      # identifier for this flow meter
    self.gpio_pin                             = gpio_pin                # the GPIO pin to read interrupts from
    self.volume_per_interrupt_ml              = volume_per_interrupt_ml # volume per interrupt in milliliters
    self.flow_rate_mlps                       = 0.0                     # last calculated flow rate in milliliters per second
    self.num_interrupts                       = 0                       # number of interrupts recorded
    self.last_recalc_flow_rate_time_s         = time.time()             # the unix timestamp in seconds of the last time we recalculated the flow rate
    self.last_recalc_flow_rate_num_interrupts = 0                       # number of interrupts recorded the last time we recalculated the flow rate
    self.lock                                 = threading.Lock()        # lock used to prevent multithread concurency issues
    
    # setup the GPIO pin for input and interrupt whenever the singal rises
    GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(self.gpio_pin, GPIO.RISING, callback=self.on_rising, bouncetime=1)
    
    # setup the average flow rate
    self.average_flow_rate_mlps = -1.0 # negative means not enough data to calculate average
    self.flow_rates_to_average = []
    self.num_flow_rates_to_average = math.ceil(config.flow_meter_flow_rate_average_duration_s / config.flow_meter_recalc_flow_rate_freq_s)
    
    self.logger = Logger("FlowMeter [" + self.id + "]: ")
  
  
  # called whenever the signal from the given GPIO pin goes from a low to high state
  def on_rising(self, channel):
    with self.lock:
      self.num_interrupts += 1
  
  
  # recalculates the average flow rate since the last recalculation
  def recalc_flow_rate(self):
    with self.lock:
      cur_time_s = time.time()
      
      # get the amount of time that has passed since the last recalculation
      delta_time_s = cur_time_s - self.last_recalc_flow_rate_time_s
      if delta_time_s == 0:
        return
      
      # get the number of interrupts that have occured since the last recalculation
      delta_num_interupts = self.num_interrupts - self.last_recalc_flow_rate_num_interrupts
      
      # calculate the new flow rate
      volume_ml = delta_num_interupts * self.volume_per_interrupt_ml
      self.flow_rate_mlps = volume_ml/delta_time_s
      
      # set the recalculation time and number of interrupts
      self.last_recalc_flow_rate_time_s         = cur_time_s
      self.last_recalc_flow_rate_num_interrupts = self.num_interrupts
      
      # calculate the average flow rate
      if len(self.flow_rates_to_average) == self.num_flow_rates_to_average:
        self.flow_rates_to_average.pop(0)
      
      self.flow_rates_to_average.append(self.flow_rate_mlps)
      
      if len(self.flow_rates_to_average) < self.num_flow_rates_to_average:
        self.average_flow_rate_mlps = -1.0
      else:
        self.average_flow_rate_mlps = sum(self.flow_rates_to_average) / len(self.flow_rates_to_average)
  
  
  def should_run(self):
    return not self.should_stop
  
  def run(self):
    self.logger.info("started")
    
    try:
      # loop forever until we are told to stop
      while self.should_run():
        # recalculate the flow rate then wait the configured interval
        self.recalc_flow_rate()
        stepped_sleep(config.flow_meter_recalc_flow_rate_freq_s, config.global_sleep_step_s, self.should_run)
    except:
      self.logger.last_exception()
      self.logger.error("exception raised")
    
    self.logger.info("stopping")
    self.logger.info("ended")
  
  def on_stop(self):
    self.logger.info("stop requested")
