import time
from stopable_thread import StopableThread

class FlowMetersManager(StopableThread):
  def __init__(self, flow_meters, recalc_flow_rate_interval_s):
    StopableThread.__init__(self)
    self.flow_meters                 = flow_meters                 # flow meters to manage
    self.recalc_flow_rate_interval_s = recalc_flow_rate_interval_s # how often the flow meters' flow rate should be recalculated
  
  def run(self):
    print "Starting flow meters manager thread"
    
    while True:
      if self.should_stop:
        print "Breaking flow meters manager thread loop"
        break
      
      for flow_meter in self.flow_meters:
        flow_meter.recalc_flow_rate()
      
      time.sleep(recalc_flow_rate_interval_s)
    
    print "Flow meters manager thread end"
  
  def stop(self):
    print "Stopping flow meters manager thread"
    StopableThread.stop(self)