import math


class FlowMetersPage:
  def __init__(self):
    self.flow_meters = []
  
  def draw(self, lcd):
    row_strs = []
    
    for flow_meter in self.flow_meters:
      row_strs.append(self.create_flow_meter_row_str(lcd, flow_meter))
    
    lcd.set_text(row_strs)
  
  def create_flow_meter_row_str(self, lcd, flow_meter):
    prefix_str = flow_meter.id + ":"
    flow_rate_str = self.format_flow_rate(flow_meter.average_flow_rate_mlps)
    
    return prefix_str + flow_rate_str.rjust(lcd.num_cols - len(prefix_str))
  
  def format_flow_rate(self, flow_rate_mlps):
    if flow_rate_mlps < 0:
      return "---"
    
    # round the flow rate
    return str(math.floor(flow_rate_mlps * 10) / 10) + "ml/s"