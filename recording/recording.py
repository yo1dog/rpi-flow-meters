class Recording:
  def __init__(self, start_time_s, duation_s, flow_meter_recordings):
    self.start_time_s          = start_time_s          # the unix timestamp in seconds of the time of this recording was recorded
    self.duation_s             = duation_s             # the duration in seconds of this recording
    self.flow_meter_recordings = flow_meter_recordings # the recordings of each of the flow meters
    

class FlowMeterRecording:
  def __init__(self, flow_meter, volume_ml):
    self.flow_meter = flow_meter # the flow meter
    self.volume_ml  = volume_ml  # volume in milliliters
