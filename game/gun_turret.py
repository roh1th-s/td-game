import pygame
import math
import typing

from game.projectile import Projectile


class GunTurret():
  def __init__(self, mouse_pos: typing.Tuple[int, int], img: pygame.Surface):
    self.original_image = img
    self.display_image = img #img that is actually blitted on screen
    self.initial_pos = mouse_pos
    self.position = (float(mouse_pos[0]), float(mouse_pos[1]))
    self.current_target = None
    self.current_vector = (0, 0)
    self.distance_to_target = 0.0

    self.placed = False
    self.show_radius = True
    self.radius = 10
    self.projectile_speed = 100
    self.fire_rate = 2
    self.fire_rate_acc = 0.0 # accumulate dt into this to keep track of fire rate
    self.rotate_speed = 10

  def update(self, mouse_pos, dt, monsters, projectiles):
     if self.placed:
      if self.rect.collidepoint(mouse_pos):
        self.show_radius = True
      else:
        self.show_radius = False

      self.update_firing(dt, monsters, projectiles)

      direction_magnitude = math.sqrt(
          self.current_vector[0] ** 2 + self.current_vector[1] ** 2)
      unit_dir_vector = [0, 0]
      if direction_magnitude > 0.0:
        unit_dir_vector = [self.current_vector[0] / direction_magnitude,
                           self.current_vector[1] / direction_magnitude]
      facing_angle = math.atan2(-unit_dir_vector[0], -
                                unit_dir_vector[1])*180/math.pi
      if facing_angle != self.current_angle:
        self.current_angle = facing_angle
        turret_centre_position = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, facing_angle)
        self.rect = self.image.get_rect()
        self.rect.center = turret_centre_position

  
  def update_firing(self, dt, monsters, projectiles):
     # time gap between shots
        if self.fire_rate_acc < self.fire_rate:
            self.fire_rate_acc += dt
        else:
            self.can_fire = True

        if self.current_target is None or self.current_target.should_die or self.target_distance > self.radius:
            self.current_target, self.target_distance = self.get_closest_monster_in_radius(monsters)

        if self.current_target is not None:
            # aim at the monster
            self.target_distance = self.calc_distance_to_target(self.current_target)
            
            results = self.calculate_aiming_vector(self.current_target, self.target_distance)
            self.target_vector = results[0]
            target_pos = results[1]

            relative_angle_to_target = self.rotate_current_angle_to_target(dt)
            # fire some bullets
            if self.can_fire and abs(relative_angle_to_target) < math.pi/8:
                self.fire_rate_acc = 0.0
                self.can_fire = False
                
                gun_pos1 = [self.position[0] + (self.current_vector[1] * 6),
                            self.position[1] - (self.current_vector[0] * 6)]
                bullet_vec1_x = target_pos[0] - gun_pos1[0]
                bullet_vec1_y = target_pos[1] - gun_pos1[1]
                bullet1_dist = math.sqrt((bullet_vec1_x ** 2) + (bullet_vec1_y ** 2))
                bullet_vec1 = [bullet_vec1_x/bullet1_dist, bullet_vec1_y/bullet1_dist]
                
                gun_pos2 = [self.position[0] - (self.current_vector[1] * 6),
                            self.position[1] + (self.current_vector[0] * 6)]
                bullet_vec2_x = target_pos[0] - gun_pos2[0]
                bullet_vec2_y = target_pos[1] - gun_pos2[1]
                bullet2_dist = math.sqrt((bullet_vec2_x ** 2) + (bullet_vec2_y ** 2))
                bullet_vec2 = [bullet_vec2_x/bullet2_dist, bullet_vec2_y/bullet2_dist]
                
                projectiles.append(Projectile(gun_pos1, bullet_vec1, target_pos, self.per_bullet_damage,
                                          self.projectile_speed, self.explosions_sprite_sheet,
                                          self.image_atlas, self.collision_grid))
                projectiles.append(Projectile(gun_pos2, bullet_vec2, target_pos, self.per_bullet_damage,
                                          self.projectile_speed, self.explosions_sprite_sheet,
                                          self.image_atlas, self.collision_grid))
   
  def draw_radius_circle(self, screen: pygame.Surface):
    if self.show_radius:
      ck = (127, 33, 33)
      int_position = [0, 0]
      int_position[0] = int(self.position[0]-self.radius)
      int_position[1] = int(self.position[1]-self.radius)
      s = pygame.Surface((self.radius*2, self.radius*2))

      s.fill(ck)
      s.set_colorkey(ck)

      pygame.draw.circle(s, pygame.Color("#B4B4B4"),
                         (self.radius, self.radius), self.radius)

      s.set_alpha(75)
      screen.blit(s, int_position)
