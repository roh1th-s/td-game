import pygame
import math
from typing import Tuple
from game.projectile import Projectile


class GunTurret():
  def __init__(self, mouse_pos: Tuple[int, int], img: pygame.Surface, bullet_img: pygame.Surface):
    self.original_image = img  # keep this so it can be scaled/rotated later as needed
    self.display_image = img.copy()  # img that is actually blitted on screen
    self.bullet_image = bullet_img
    self.initial_pos = mouse_pos
    self.position = (float(mouse_pos[0]), float(mouse_pos[1]))
    self.rect = img.get_rect()
    self.rect.center = self.position
    self.current_target = None
    self.current_vector = [0, 0]
    self.current_angle = 0
    self.distance_to_target = 0.0

    self.placed = False
    self.show_radius = True
    self.can_fire = True
    self.radius = 100
    self.projectile_speed = 100
    self.per_bullet_damage = 30
    self.fire_rate = 2
    self.fire_rate_acc = 0.0  # accumulate dt into this to keep track of fire rate
    self.rotate_speed = 5  # in radians

  def update(self, mouse_pos, dt, enemies, projectiles):
    if self.placed:
      # show attack radius when hovered over
      if self.rect.collidepoint(mouse_pos):
        self.show_radius = True
      else:
        self.show_radius = False

      self.update_firing(dt, enemies, projectiles)

      direction_magnitude = math.sqrt(
          self.current_vector[0] ** 2 + self.current_vector[1] ** 2)
      unit_dir_vector = [0, 0]

      if direction_magnitude > 0.0:
        unit_dir_vector = [self.current_vector[0] / direction_magnitude,
                           self.current_vector[1] / direction_magnitude]

      facing_angle = math.atan2(-unit_dir_vector[0], -unit_dir_vector[1]) * 180 / math.pi

      if facing_angle != self.current_angle:
        self.current_angle = facing_angle
        turret_centre_position = self.rect.center
        self.display_image = pygame.transform.rotate(self.original_image, facing_angle)
        self.rect = self.display_image.get_rect()
        self.rect.center = turret_centre_position

    else:
      # if turret isn't placed yet, move it along with mouse
      self.set_position(mouse_pos)

  def update_firing(self, dt, enemies, projectiles):
    # time gap between shots
    if self.fire_rate_acc < self.fire_rate:
      self.fire_rate_acc += dt
    else:
      self.can_fire = True

    if self.current_target is None or self.current_target.should_die or self.target_distance > self.radius:
      self.current_target, self.target_distance = self.get_closest_enemy_in_radius(enemies)

    if self.current_target is not None:
      # aim at the enemy
      self.target_distance = self.calc_distance_to_target(self.current_target)

      results = self.calculate_aim_vector(self.current_target, self.target_distance)
      self.target_vector = results[0]
      target_pos = results[1]

      relative_angle_to_target = self.rotate_current_angle_to_target(dt)
      # fire some bullets
      if self.can_fire and abs(relative_angle_to_target) < math.pi/8:
        self.fire_rate_acc = 0.0
        self.can_fire = False

        bullet_start_pos = (self.position[0] + self.current_vector[0]
                            * 28, self.position[1] + self.current_vector[1] * 28)
        projectiles.append(Projectile(bullet_start_pos, self.current_vector, target_pos, self.per_bullet_damage,
                                      self.projectile_speed, self.bullet_image))

  def draw(self, screen: pygame.Surface):
    screen.blit(self.display_image, self.rect.topleft)

    if self.show_radius:
      s = pygame.Surface((self.radius*2, self.radius*2))

      color_key = (127, 33, 33)  # rando color
      s.fill(color_key)
      s.set_colorkey(color_key)

      pygame.draw.circle(s, pygame.Color("#B4B4B4"),
                         (self.radius, self.radius), self.radius)

      s.set_alpha(75)
      int_pos = self.get_position_int()
      screen.blit(s, (int_pos[0] - self.radius, int_pos[1] - self.radius))

  def set_position(self, position):
    self.position = position
    self.rect.center = position

  def get_position_int(self):
    return (int(self.position[0]), int(self.position[1]))

  def rotate_current_angle_to_target(self, dt):
    current_angle = math.atan2(self.current_vector[1], self.current_vector[0])
    target_angle = math.atan2(self.target_vector[1], self.target_vector[0])
    relative_angle = target_angle - current_angle

    if abs(relative_angle) < 0.05:
      self.current_vector[0] = self.target_vector[0]
      self.current_vector[1] = self.target_vector[1]
    else:
      # get value in interval (-pi, pi)
      if relative_angle > math.pi:
        relative_angle = relative_angle - (2 * math.pi)
      if relative_angle < -math.pi:
        relative_angle = relative_angle + (2 * math.pi)

      if relative_angle > 0:
        current_angle += (dt * self.rotate_speed)
      else:
        current_angle -= (dt * self.rotate_speed)

      self.current_vector[0] = math.cos(current_angle)
      self.current_vector[1] = math.sin(current_angle)

    return relative_angle

  def calc_distance_to_target(self, target):
    x_dist = self.position[0] - target.position[0]
    y_dist = self.position[1] - target.position[1]
    current_dist = math.sqrt((x_dist * x_dist) + (y_dist * y_dist))
    # re-adjust distance to our anticipated position when projectiles reach target
    time_to_reach_target = current_dist/self.projectile_speed
    guess_position = target.guess_position_at_time(time_to_reach_target)
    x_dist = guess_position[0] - self.position[0]
    y_dist = guess_position[1] - self.position[1]
    guess_dist = math.sqrt((x_dist ** 2) + (y_dist ** 2))
    return guess_dist

  def get_closest_enemy_in_radius(self, enemies):
    closest_enemy_distance = self.radius
    closest_enemy_in_radius = None
    for enemy in enemies:
      guess_dist = self.calc_distance_to_target(enemy)
      if guess_dist < self.radius:
        if guess_dist < closest_enemy_distance:
          closest_enemy_distance = guess_dist
          closest_enemy_in_radius = enemy

    return closest_enemy_in_radius, closest_enemy_distance

  def calculate_aim_vector(self, target, distance):
    time_to_reach_target = distance/self.projectile_speed
    guess_position = target.guess_position_at_time(time_to_reach_target)
    x_direction = guess_position[0] - self.position[0]
    y_direction = guess_position[1] - self.position[1]
    dist = math.sqrt((x_direction ** 2) + (y_direction ** 2))
    return [[x_direction/dist, y_direction/dist], guess_position]
