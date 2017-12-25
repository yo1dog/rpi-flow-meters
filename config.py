from flow_meter import FlowMeter

#############################
# Flow Meters

flow_meter_recalc_flow_rate_freq_s = 0.5
flow_meter_flow_rate_average_duration_s = 5;

flow_meters = [
  # pin numbers are GPIO pin numbers not PCB pin numbers
  FlowMeter(17, "Test A", 2.416),
  FlowMeter(18, "Test B", 2.416),
  FlowMeter(22, "Test C", 2.416),
  FlowMeter(24, "Test D", 2.416),
  FlowMeter(25, "Test E", 2.416),
]


#############################
# UI

ui_redraw_page_freq_s = flow_meter_recalc_flow_rate_freq_s
ui_poll_buttons_freq_s = 0.05