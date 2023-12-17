import math
from typing import Tuple
from pygame import Surface
from game.projectile import Projectile
from game.turrets.normal_turret import NormalTurret


class DoubleTurret(NormalTurret):
  def __init__(self, mouse_pos: Tuple[int, int], img: Surface, bullet_img: Surface):
    super().__init__(mouse_pos, img, bullet_img)

  def update_firing(self, dt, enemies, projectiles):

    if self.fire_rate_acc < self.fire_rate:
      self.fire_rate_acc += dt
    else:
      self.can_fire = True

    if self.current_target is None or self.current_target.should_die or \
            self.distance_to_target > self.radius or self.angle_to_target > math.pi/8:
      self.current_target, self.distance_to_target = self.get_closest_enemy_in_radius(
          enemies)

    if self.current_target is not None:
      # aim at the enemy
      self.distance_to_target = self.estimate_distance_to_target(
          self.current_target)

      results = self.calculate_aim_vector(
          self.current_target, self.distance_to_target)
      self.target_vector = results[0]
      target_pos = results[1]

      relative_angle_to_target = self.rotate_current_angle_to_target(dt)
      self.angle_to_target = relative_angle_to_target
      # fire some bullets
      if self.can_fire and abs(relative_angle_to_target) < math.pi/8:
        self.fire_rate_acc = 0.0
        self.can_fire = False

        cur_vec_x = self.current_vector[0]
        cur_vec_y = self.current_vector[1]

        # rotated cur_vec 90 degrees to right
        right_vec_x = cur_vec_y
        right_vec_y = -cur_vec_x

        bullet_1_start_pos = (
            self.position[0] + cur_vec_x * 28 + right_vec_x * 7,
            self.position[1] + cur_vec_y * 28 + right_vec_y * 7
        )
        projectiles.append(Projectile(bullet_1_start_pos, self.current_vector, target_pos, self.per_bullet_damage,
                                      self.projectile_speed, self.bullet_image))

        bullet_2_start_pos = (
            self.position[0] + cur_vec_x * 28 - right_vec_x * 7,
            self.position[1] + cur_vec_y * 28 - right_vec_y * 7
        )

        projectiles.append(Projectile(bullet_2_start_pos, self.current_vector, target_pos, self.per_bullet_damage,
                                      self.projectile_speed, self.bullet_image))
