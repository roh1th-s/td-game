from typing import List
import pygame


class Animation:
  def __init__(self, frames: List[pygame.Surface], speed):
    self.frames = frames
    self.speed = speed
    self.current_frame = 0
    self.time_since_last_frame = 0
    self.started = False
    self.ended = False

  def start(self):
    self.started = True

  def update(self, dt):
    if not self.started:
      return
    
    self.time_since_last_frame += dt
    if self.time_since_last_frame > self.speed:
      if self.current_frame == len(self.frames) - 1:
        self.ended = True

      self.current_frame = (self.current_frame + 1) % len(self.frames)
      self.time_since_last_frame = 0

  def get_current_frame(self):
    return self.frames[self.current_frame]
