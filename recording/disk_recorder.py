# Note: This does not maintain the size of the recordings file. You should use
# an external utility to maintain the file size (like logrotate)

import threading
import config
from stopable_thread import StopableThread
from stepped_sleep import stepped_sleep
from logger import Logger

logger = Logger("DiskRecorder: ")

class DiskRecorder(StopableThread):
  def __init__(self, recordings_filepath):
    StopableThread.__init__(self, "DiskRecorder")
    
    self.recordings_filepath = recordings_filepath # path of the file to write recordings to
    self.recordings_buffer   = []                  # recordings waiting to be written to the file
    self.buffer_lock         = threading.Lock()    # lock used to prevent multithread concurency issues
    self.write_lock          = threading.Lock()    # lock used to prevent multithread concurency issues
  
  
  # adds a recording that should be written to the file
  def record(self, recording):
    with self.buffer_lock:
      self.recordings_buffer.append(recording)
  
  # writes buffered recorings and empties the buffer
  def flush(self):
    with self.buffer_lock:
      logger.debug("flushing " + str(len(self.recordings_buffer)) + " recordings")
      self.write_to_disk(self.recordings_buffer)
      self.recordings_buffer = []
  
  # writes given recorings to the file
  def write_to_disk(self, recordings):
    if len(recordings) == 0:
      return
    
    # convert the recordings to a string
    recordings_str = self.recordings_to_str(recordings)
    
    # append the recordings to the file on the local disk
    with self.write_lock:
      with open(self.recordings_filepath, "a") as recordings_file:
        recordings_file.write(recordings_str)
    
  
  # converts recordings to a string to be written to the recordings file
  def recordings_to_str(self, recordings):
    str = ""
    for recording in recordings:
      str += self.recording_to_str(recording) + "\n"
    
    return str
  
  # format:
  #   1514492558|3000ms|"Flow Meter A":12.34ml|"Flow Meter B":56.00ml|"Flow Meter C":78.90ml|
  # 
  def recording_to_str(self, recording):
    recording_str = str(int(recording.start_time_s)) + "|" + str(int(recording.duation_s * 1000)) + "ms|"
    
    for flow_meter_recording in recording.flow_meter_recordings:
      recording_str += "\"" + flow_meter_recording.flow_meter.id + "\":" + ("%.2f" % flow_meter_recording.volume_ml) + "ml" + "|"
    
    return recording_str
  
  
  def should_run(self):
    return not self.should_stop
  
  def run(self):
    logger.info("started")
    
    try:
      # loop forever until we are told to stop
      while self.should_run():
        # flush then wait the configured interval
        try:
          self.flush()
        except:
          logger.last_exception("Error flushing:\n")
         
        stepped_sleep(config.disk_recorder_write_freq_s, config.global_sleep_step_s, self.should_run)
    except:
      logger.last_exception()
      logger.error("exception raised")
    
    logger.info("stopping")
    logger.info("ended")
  
  def on_stop(self):
    logger.info("stop requested")