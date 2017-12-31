import time

def stepped_sleep(duration_s, step_s, should_continue_fn):
  if duration_s <= step_s:
    time.sleep(duration_s)
    return
  
  end_time_s = time.time() + duration_s
  
  while True:
    time.sleep(step_s)
    
    if not should_continue_fn():
      break
    
    remaining_time_s = end_time_s - time.time()
    
    if remaining_time_s <= 0:
      break
    
    if remaining_time_s <= step_s:
      time.sleep(remaining_time_s)
      break