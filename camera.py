import numpy as np
from math import cos, sin

from light_math import (normalize, lookAtTransposed)

DEG_TO_RAD = 0.01745329251

class Camera(object):
  
  def __init__(self, a_pos   = np.array([0.0, 0.0, 0.0], dtype = np.float32),
                     a_up    = np.array([+0.0, +1.0, +0.0], dtype = np.float32),
                     a_front = np.array([+0.0, -1.0, 0.0], dtype = np.float32),
                     a_speed = 50.0, a_mouse_sensitivity = 0.1):
    self.move_speed = a_speed
    self.pos = a_pos
    self.up = a_up
    self.world_up = a_up
    self.front = a_front
    self.right = normalize(np.cross(a_up, a_front))
    
    self.yaw = -90.0
    self.pitch = 0.0
    self.mouse_sensitivity = a_mouse_sensitivity
    
  def get_view_matrix(self):
    return lookAtTransposed(self.pos, self.pos + self.front, self.up)
  
  def process_keyboard(self, direction, delta):
    velocity = self.move_speed * delta
    if(direction == "forward"):
      self.pos += self.front * velocity
    if (direction == "backward"):
      self.pos -= self.front * velocity
    if(direction == "left"):
      self.pos -= self.right * velocity
    if(direction == "right"):
      self.pos += self.right * velocity
      
  def updateVectors(self):
    tmpFront = np.array([cos(DEG_TO_RAD * self.yaw) * cos(DEG_TO_RAD *  self.pitch),
                         sin(DEG_TO_RAD * self.pitch),
                         sin(DEG_TO_RAD * self.yaw) * cos(DEG_TO_RAD * self.pitch)], dtype = np.float32)


    self.front = normalize(tmpFront)
    self.right = normalize(np.cross(self.front, self.world_up))
    self.up    = normalize(np.cross(self.right, self.front))
      
  def process_mouse(self, delta_x, delta_y, limit_pitch):
    delta_x *= self.mouse_sensitivity
    delta_y *= self.mouse_sensitivity
    
    self.yaw += delta_x
    self.pitch += delta_y
    
    if(limit_pitch):
      if (self.pitch > 89.0):
        self.pitch = 89.0
      if (self.pitch < -89.0):
        self.pitch = -89.0
        
    self.updateVectors()
