import math
from typing import Tuple
from pygame import Surface
from game.turrets.normal_turret import NormalTurret


class HeavyTurret(NormalTurret):
  cooldown_time = 30
  per_bullet_damage = 100
  rotate_speed = 2
  fire_rate = 2

  def __init__(self, mouse_pos: Tuple[int, int], img: Surface, bullet_img: Surface):
    super().__init__(mouse_pos, img, bullet_img)
