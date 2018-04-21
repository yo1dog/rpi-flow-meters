import threading
import re
from datetime import datetime
import apiclient as google_api_client
import config
from stopable_thread import StopableThread
from stepped_sleep import stepped_sleep
from logger import Logger

logger = Logger("GoogleSheetsRecorder: ")

class GoogleSheetsRecorder(StopableThread):
  def __init__(self,
    google_sheets_spreadsheet_id,
    google_sheets_sheet_name,
    google_creds,
    flow_meters
  ):
    StopableThread.__init__(self, "GoogleSheetsRecorder")
    
    self.google_sheets_spreadsheet_id = google_sheets_spreadsheet_id # ID of the Google Sheets spreadsheet to write data to
    self.google_sheets_sheet_name     = google_sheets_sheet_name     # name of the Google Sheets sheet to write data to
    self.google_creds                 = google_creds                 # Google API credentials
    self.flow_meters                  = flow_meters                  # flow meters that will be recorded
    self.recordings_buffer            = []                           # recordings waiting to be written to the file
    self.google_sheets_service        = None                         # service used to make API calls
    self.buffer_lock                  = threading.Lock()             # lock used to prevent multithread concurency issues
    self.write_lock                   = threading.Lock()             # lock used to prevent multithread concurency issues
    self.is_initialized               = False
    
    # map of the flow meter ID to the column index in the sheet for that flow meter
    self.flow_meter_id__sheet_column_index__map = None
    self.sheet_table_num_columns = -1
    
  
  def init(self):
    # create the Google Sheets API service    
    attempt_num = 0
    while self.google_sheets_service is None:
      attempt_num += 1
      logger.info("creating Google Sheets service (attempt #" + str(attempt_num) + ")...")
      
      try:
        self.google_sheets_service = google_api_client.discovery.build("sheets", "v4", credentials=self.google_creds)
      except Exception as err:
        logger.info("Unable to create to Google Sheets service: " + str(err))
        
        retry_delay_s = config.google_sheets_create_service_retry_freq_s
        logger.info("Retrying in " + str(retry_delay_s) + "s...")
        stepped_sleep(retry_delay_s, config.global_sleep_step_s, self.should_run)
      
      logger.info("Google Sheets service created")
    
    # inspect the sheet
    logger.info("inspecting sheet...")
    
    # get the first row of the sheet (the headers)
    result = self.google_sheets_service.spreadsheets().values().get(
      spreadsheetId=self.google_sheets_spreadsheet_id,
      range=self.google_sheets_sheet_name + "!1:1"
    ).execute()
    
    values = result.get('values', [])
    if not values:
      raise ValueError("0 rows returned from first row Google Sheets request.")
    
    headers = values[0]
    
    # create the flow meter ID -> column index map
    self.flow_meter_id__sheet_column_index__map = {}
    
    flow_meter_headers_start_column_index = config.google_sheets_flow_meter_headers_start_column_index
    
    # for each flow meter ID...
    for flow_meter in self.flow_meters:
      # find the header that matches the flow meter's ID and use its column index
      found_header_column_index = -1
      for header_column_index in range(flow_meter_headers_start_column_index, len(headers)):
        header = headers[header_column_index]
        if header.strip().lower() == flow_meter.id.lower():
          found_header_column_index = header_column_index
          break
      
      if found_header_column_index == -1:
        raise ValueError("Unable to find header for flow meter ID \"" + flow_meter.id + "\".")
      
      self.flow_meter_id__sheet_column_index__map[flow_meter.id] = found_header_column_index
    
    # set the number of columns in the table
    max_column_index = max(self.flow_meter_id__sheet_column_index__map.values())
    self.sheet_table_num_columns = max_column_index + 1
    
    logger.info("sheet inspected: " + str(self.sheet_table_num_columns) + " table columns, " + str(self.flow_meter_id__sheet_column_index__map))
    
    self.is_initialized = True
  
  
  # adds a recording that should be added to the sheet
  def record(self, recording):
    with self.buffer_lock:
      self.recordings_buffer.append(recording)
  
  
  # writes buffered recorings and empties the buffer
  def flush(self):
    if not self.is_initialized:
      logger.error("not initialized. Ignoring request to flush")
      return
    
    with self.buffer_lock:
      logger.debug("flushing " + str(len(self.recordings_buffer)) + " recordings")
      self.add_to_sheet(self.recordings_buffer)
      self.recordings_buffer = []
  
  # adds buffered recorings to the sheet and empties the buffer
  def add_to_sheet(self, recordings):
    if len(recordings) == 0:
      return
    
    # convert the recordings to sheet rows
    recording_sheet_rows = self.recordings_to_sheet_rows(recordings)
    
    # append the recordings to the sheet
    with self.write_lock:
      result = self.google_sheets_service.spreadsheets().values().append(
        spreadsheetId=self.google_sheets_spreadsheet_id,
        range=self.google_sheets_sheet_name+"!A1",
        body={"values": recording_sheet_rows},
        valueInputOption="USER_ENTERED"
      ).execute()
      
      num_rows_updated = result.get("updates", {}).get("updatedRows", 0)
      if num_rows_updated < 1:
        raise ValueError("0 rows updated.")
  
  
  # converts recordings to sheet rows to be added to the sheet
  def recordings_to_sheet_rows(self, recordings):
    sheet_rows = []
    for recording in recordings:
      sheet_rows.append(self.recording_to_sheet_row(recording))
    
    return sheet_rows
  
  def recording_to_sheet_row(self, recording):
    if self.flow_meter_id__sheet_column_index__map is None:
      raise ValueError("Must initialize flow meter ID -> sheet column index map before recordings can be converted to rows.")
    
    sheet_row = [""] * self.sheet_table_num_columns
    
    sheet_row[0] = datetime.fromtimestamp(recording.start_time_s).isoformat(" ")
    sheet_row[1] = recording.duation_s
    
    # add values for each flow meter recording
    for flow_meter_recording in recording.flow_meter_recordings:
      flow_meter = flow_meter_recording.flow_meter
      
      # get the column index to insert the value at
      if not flow_meter.id in self.flow_meter_id__sheet_column_index__map:
        raise ValueError("Unrecognized flow meter ID \"" + flow_meter.id + "\".")
      
      column_index = self.flow_meter_id__sheet_column_index__map[flow_meter.id]
      sheet_row[column_index] = flow_meter_recording.volume_ml
    
    return sheet_row
  
  
  def should_run(self):
    return not self.should_stop
  
  def run(self):
    logger.info("started")
    
    logger.debug("initializing...")
    self.init()
    logger.debug("initialized")
    
    try:
      # loop forever until we are told to stop
      while self.should_run():
        # flush then wait the configured interval
        try:
          self.flush()
        except:
          logger.last_exception("Error flushing:\n")
        
        stepped_sleep(config.google_sheets_recorder_send_freq_s, config.global_sleep_step_s, self.should_run)
    except:
      logger.last_exception()
      logger.error("exception raised")
    
    logger.info("stopping")
    logger.info("ended")
  
  def on_stop(self):
    logger.info("stop requested")
