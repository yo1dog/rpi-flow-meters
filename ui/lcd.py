class LCD:
  def __init__(self, lcd_plate):
    self.plate      = lcd_plate
    self.cursor_row = 0
    self.cursor_col = 0
    self.num_cols   = self.plate._cols
    self.num_rows   = self.plate._lines
    self.row_chars  = [[" " for col in range(self.num_cols)] for row in range(self.num_rows)]
  
  def clear(self):
    for row in range(self.num_rows):
      for col in range(self.num_cols):
        self.row_chars[row][col] = " "
    
    self.plate.clear()
  
  
  def set_text(self, row_strs):
    for row in range(self.num_rows):
      for col in range(self.num_cols):
        char = " "
        
        if row < len(row_strs) and col < len(row_strs[row]):
          char = row_strs[row][col]
        
        if char == self.row_chars[row][col]:
          continue
        
        self.row_chars[row][col] = char
        
        if self.cursor_row != row or self.cursor_col != col:
          self.plate.set_cursor(col, row)
          self.cursor_col = col
          self.cursor_row = row
        
        self.plate.write8(ord(char), True)
        self.cursor_col += 1