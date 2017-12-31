import time
import config
from oauth2client.service_account import ServiceAccountCredentials
from stopable_thread import StopableThread
from stepped_sleep import stepped_sleep
from recording import Recording, FlowMeterRecording
from disk_recorder import DiskRecorder
from google_sheets_recorder import GoogleSheetsRecorder
from logger import Logger

logger = Logger("RecorderManager: ")

class RecorderManager(StopableThread):
  def __init__(self, flow_meters):
    StopableThread.__init__(self, "RecorderManager")
    
    self.flow_meters                            = flow_meters # flow meters to record
    self.last_record_time_s                     = -1          # the unix timestamp in seconds of the last time we recorded
    self.last_record_flow_meters_num_interrupts = {}          # the flow meters' total number of interrupts the last time we recorded
    
    self.recorders = []
    
    # create the disk recorder
    self.recorders.append(DiskRecorder(
      config.disk_recorder_filepath
    ))
    
    # create the Google Sheets recorder
    google_creds = ServiceAccountCredentials.from_json_keyfile_name(
      config.google_service_user_creds_filepath,
      config.google_auth_scopes
    )
    self.recorders.append(GoogleSheetsRecorder(
      config.google_sheets_spreadsheet_id,
      config.google_sheets_sheet_name,
      google_creds,
      flow_meters
    ))
  
  
  def record(self):
    logger.debug("recording")
    cur_time_s = time.time()
    
    # check if this is the first time we will be recording
    if self.last_record_time_s < 0:
      self.set_last_record_state(cur_time_s)
      return
    
    # get the amount of time that has passed since the last recording
    delta_time_s = cur_time_s - self.last_record_time_s
    if delta_time_s < config.min_recording_duration_s:
      return
    
    # create a recording for each of the flow meters
    flow_meter_recordings = []
    for flow_meter in self.flow_meters:
      # get the change in the total number of interrupts for the flow meter
      last_record_flow_meter_num_interrupts = self.last_record_flow_meters_num_interrupts[flow_meter.id]
      delta_flow_meter_num_interrupts = flow_meter.num_interrupts - last_record_flow_meter_num_interrupts
      
      # calculate the volume
      volume_ml = delta_flow_meter_num_interrupts * flow_meter.volume_per_interrupt_ml
      
      flow_meter_recordings.append(FlowMeterRecording(flow_meter, volume_ml))
    
    # create a recording
    recording = Recording(cur_time_s, delta_time_s, flow_meter_recordings)
    
    # set the last record state
    self.set_last_record_state(cur_time_s)
    
    # record to recorders
    for recorder in self.recorders:
      recorder.record(recording)
  
  # sets the record time and number of interrupts for each flow meter
  def set_last_record_state(self, cur_time_s):
    self.last_record_time_s = cur_time_s
    for flow_meter in self.flow_meters:
      self.last_record_flow_meters_num_interrupts[flow_meter.id] = flow_meter.num_interrupts
  
  def should_run(self):
    if self.should_stop:
      return False
    
    for recorder in self.recorders:
      if not recorder.isAlive():
        return False
    
    return True
  
  def run(self):
    logger.info("started")
    
    # start the recorders
    logger.info("starting recorders")
    for recorder in self.recorders:
      recorder.start()
    
    try:
      # loop forever until we are told to stop
      while self.should_run():
        # record then wait the configured interval
        self.record()
        stepped_sleep(config.record_freq_s, config.global_sleep_step_s, self.should_run)
    except:
      logger.last_exception()
      logger.error("exception raised")
    
    logger.info("stopping")
    
    # stop the recorders
    logger.info("stopping recorders")
    for recorder in self.recorders:
      recorder.stop()
      recorder.join()
    
    # take a final recording
    logger.info("taking final recording")
    self.record()
    
    # flush recorders
    logger.info("flushing recorders")
    for recorder in self.recorders:
      try:
        recorder.flush()
      except:
        logger.last_exception("Error flushing one of the recorders:\n")
    
    logger.info("ended")
  
  def on_stop(self):
    logger.info("stop requested")