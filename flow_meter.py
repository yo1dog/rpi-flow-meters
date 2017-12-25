import threading
import time
import math
import RPi.GPIO as GPIO
import config
from stopable_thread import StopableThread

class FlowMeter(StopableThread):
  def __init__(self, gpio_pin, name, ml_per_interrupt):
    StopableThread.__init__(self)
    
    self.gpio_pin                     = gpio_pin         # the GPIO pin to read interrupts from
    self.name                         = name             # label for display purposes
    self.ml_per_interrupt             = ml_per_interrupt # volumne in milliliters per interrupt
    self.flow_rate_mlps               = 0.0              # last calculated flow rate
    self.num_interrupts               = 0                # number of interrupts since the last time the flow rate was calculated
    self.last_recalc_flow_rate_time_s = time.time()      # the unix timestamp in seconds of the last time we recalculated the flow rate
    self.lock                         = threading.Lock() # lock used to prevent multithread concurency issues
    
    # setup the GPIO pin for input and interrupt whenever the singal rises
    GPIO.setup(self.gpio_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(self.gpio_pin, GPIO.RISING, callback=self.on_rising, bouncetime=1)
    
    # setup the average flow rate
    self.average_flow_rate_mlps = -1.0 # negative means not enough data to calculate average
    self.flow_rates_to_average = []
    self.num_flow_rates_to_average = math.ceil(config.flow_meter_flow_rate_average_duration_s / config.flow_meter_recalc_flow_rate_freq_s)
  
  
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
      
      # calculate the new flow rate
      ml = self.num_interrupts * self.ml_per_interrupt
      self.flow_rate_mlps = ml/delta_time_s
    
      # reset the number of interrupts and set the recalculation time
      self.num_interrupts = 0
      self.last_recalc_flow_rate_time_s = cur_time_s
      
      # calculate the average flow rate
      if len(self.flow_rates_to_average) == self.num_flow_rates_to_average:
        self.flow_rates_to_average.pop(0)
      
      self.flow_rates_to_average.append(self.flow_rate_mlps)
      
      if len(self.flow_rates_to_average) < self.num_flow_rates_to_average:
        self.average_flow_rate_mlps = -1
      else:
        self.average_flow_rate_mlps = sum(self.flow_rates_to_average) / len(self.flow_rates_to_average)
  
  
  # start this flow meter's thread
  def run(self):
    print "Starting flow meter \"" + self.name + "\" thread"
    
    # loop forever until we are told to stop
    while not self.should_stop:
      # recalculate the flow rate then wait the configured interval
      self.recalc_flow_rate()
      time.sleep(config.flow_meter_recalc_flow_rate_freq_s)
    
    print "Flow meter \"" + self.name + "\" thread end"
  
  # stop this flow meter's thread
  def stop(self):
    print "Stopping flow meter \"" + self.name + "\" thread"
    StopableThread.stop(self)