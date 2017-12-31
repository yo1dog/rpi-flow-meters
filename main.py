#!/usr/bin/python

# use GPIO pin numbering instead of PCB pin numbering
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)

import time
import config
from cistern import Cistern
from logger import Logger

logger = Logger("Main: ")

logger.debug("Debugging Enabled")

cistern = Cistern(config.flow_meters)
cistern.init()

try:
  logger.info("started")
  
  logger.info("starting cistern")
  cistern.start()
  
  # keep the main thread alive to listen for keyboard interrupts (^C)
  while cistern.is_alive():
    time.sleep(config.global_sleep_step_s)
except KeyboardInterrupt:
  logger.info("keyboard interrupt")
except:
  logger.last_exception()
  logger.info("exception raised")

logger.info("stopping cistern")
cistern.stop()

logger.info("ended")