import math
from typing import Tuple, List
import pygame

from game.enemy import Enemy


class Projectile():
  def __init__(self, start_pos: Tuple[int, int], heading_vec: List[float], target_pos: Tuple[int, int],
               damage: int, speed: float, sprite: pygame.Surface):
    self.original_image = sprite
    self.display_image = sprite.copy()
    self.speed = speed
    self.damage = damage

    self.current_vector = heading_vec.copy()
    self.position = [float(start_pos[0]), float(start_pos[1])]
    facing_angle = math.atan2(-self.current_vector[0], -self.current_vector[1]) * 180 / math.pi
    self.display_image = pygame.transform.rotate(self.original_image, facing_angle)
    self.rect = self.display_image.get_rect()
    self.rect.center = start_pos

    self.should_die = False
    self.target_position = target_pos
    x_diff = self.target_position[0] - self.position[0]
    y_diff = self.target_position[1] - self.position[1]
    total_target_dist = math.sqrt(x_diff * x_diff + y_diff * y_diff)
    self.shot_range = total_target_dist + 16.0

  def update(self, dt, enemies: List[Enemy], all_projectiles: List["Projectile"]):
    self.shot_range -= dt * self.speed
    self.position[0] += (self.current_vector[0] * dt * self.speed)
    self.position[1] += (self.current_vector[1] * dt * self.speed)
    self.rect.center = (int(self.position[0]), int(self.position[1]))

    for enemy in enemies:
      enemy_hitbox = enemy.rect.scale_by(0.6)
      if enemy_hitbox.colliderect(self.rect):
        enemy.take_damage(self.damage)
        self.should_die = True

    if self.shot_range <= 0.0:
      self.should_die = True

    if self.should_die:
      all_projectiles.remove(self)

  def draw(self, screen):
    screen.blit(self.display_image, self.rect.topleft)
