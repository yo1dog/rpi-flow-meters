import os
import sys
from flow_meter import FlowMeter

project_dir = os.path.dirname(__file__)


#############################
# Flow Meters

flow_meter_recalc_flow_rate_freq_s      = 0.5 # how often we should recalculate the flow rate for each flow meter in seconds
flow_meter_flow_rate_average_duration_s = 5   # duration we should average the flow rate over in seconds

flow_meters = [
  # pin numbers are GPIO pin numbers not PCB pin numbers
  # 
  #         ID          GPIO pin #   volume per interrupt in milliliters
  FlowMeter("Test A",   17,          2.416),
  FlowMeter("Test B",   18,          2.416),
  FlowMeter("Test C",   22,          2.416),
  FlowMeter("Test D",   24,          2.416),
  FlowMeter("Test E",   25,          2.416),
]



#############################
# Recording

record_freq_s            = 15*60 # how often we should record data from the flow meters
min_recording_duration_s = 30    # minimum duration of a recording (used to ensure we don't get many short recordings)

disk_recorder_write_freq_s = 5 # how often we should write recordings to disk
disk_recorder_filepath     = os.path.join(project_dir, 'data', 'recordings.txt') # path to the file to write recordings to

google_sheets_recorder_send_freq_s = 5*60 # how often we should send recordings to Google Sheets
google_sheets_spreadsheet_id       = "1zCe2msA7Qt2kEtVFctU8ttb2VOe7nle4h16k8zmWaBA" # the ID of the spreadsheet to write recordings to
google_sheets_sheet_name           = "Data" # the name of the sheet in the spreadshet to write recordings to
google_sheets_flow_meter_headers_start_column_index = 2 # the 0-based index of the first flow meter column in the sheet



#############################
# Google Auth

google_service_user_creds_filepath = os.path.join(project_dir, 'data', 'google_service_user_creds.json')
google_auth_scopes = ["https://www.googleapis.com/auth/spreadsheets"]



#############################
# UI

ui_redraw_page_freq_s = flow_meter_recalc_flow_rate_freq_s # how often we should refresh (redraw) pages in seconds
ui_poll_buttons_freq_s = 0.05 # how often we should poll for button state changes in seconds



#############################
# Misc

global_sleep_step_s = 1
enable_debug_logging = "--debug" in sys.argv




#############################
#############################

# ensure our min recording duration is >= 0 and <= record_freq_s - 1
min_recording_duration_s = max(min(min_recording_duration_s, record_freq_s - 1), 0)

# ensure there are no duplicate flow meter IDs
for i in range(0, len(flow_meters)):
  for j in range(i + 1, len(flow_meters)):
    if flow_meters[i].id.lower() == flow_meters[j].id.lower():
      raise ValueError("Flow meter IDs must be unique. Duplicate flow meter ID: \"" + flow_meters[i].id + "\"")