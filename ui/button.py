class Button:
  def __init__(self, on_pressed_callback=None, on_released_callback=None, on_change_callback=None):
    self.is_pressed = False
    self.on_pressed_callback  = on_pressed_callback
    self.on_released_callback = on_released_callback
    self.on_change_callback   = on_change_callback
  
  def set_is_pressed(self, is_pressed):
    state_changed = self.is_pressed != is_pressed
    self.is_pressed = is_pressed
    
    if not state_changed:
      return
    
    if self.is_pressed and self.on_pressed_callback != None:
      self.on_pressed_callback(self)
    
    if not self.is_pressed and self.on_released_callback != None:
      self.on_released_callback(self)
    
    if self.on_change_callback != None:
      self.on_change_callback(self)