import math
from random import random
from typing import List, Tuple
import pygame
from os import listdir, path
from pygame_gui.elements.ui_world_space_health_bar import UIWorldSpaceHealthBar

from game.animation import Animation

# load explosion animation frames
anim_path = path.join("data", "images", "explosion_anim")
frame_files = sorted([f for f in listdir(anim_path) if path.isfile(
    path.join(anim_path, f)) and f.endswith(".png")], key=lambda fname: int(fname.split(".")[0]))
explosion_frames = [
    pygame.transform.scale(pygame.image.load(
        path.join(anim_path, f)), (40, 40)).convert_alpha()
    for f in frame_files
]


class Enemy():
  def __init__(self, all_enemies: List["Enemy"], waypoints: List[Tuple[int, int]], sprite: pygame.Surface, point_cost: int,
               ui_manager, health_bar_container) -> None:
    self.move_speed = 100
    self.point_cost = point_cost
    self.ui_manager = ui_manager
    self.all_enemies = all_enemies
    self.original_image = sprite
    self.display_image = self.original_image.copy()
    self.death_anim = Animation(explosion_frames, 0.1)
    self.waypoints = waypoints
    self.rect = self.display_image.get_rect()
    self.collide_radius = int(self.rect[2] / 2.0)
    self.position = [0.0, 0.0]
    rand_pos_in_radius = self.get_random_point_within_radius(
        self.waypoints[0], 5)
    self.position[0] = float(rand_pos_in_radius[0])
    self.position[1] = float(rand_pos_in_radius[1])

    self.rect.centerx = self.position[0]
    self.rect.centery = self.position[1]

    self.change_direction_time = 5.0
    self.change_direction_accumulator = 0.0

    # waypoint stuff
    self.next_way_point_index = 0
    self.next_way_point = self.get_random_point_within_radius(
        self.waypoints[self.next_way_point_index], 5)

    x_dist = float(self.next_way_point[0]) - float(self.position[0])
    y_dist = float(self.next_way_point[1]) - float(self.position[1])
    self.distance_to_next_way_point = math.sqrt(
        (x_dist * x_dist) + (y_dist * y_dist))
    self.current_vector = [x_dist / self.distance_to_next_way_point,
                           y_dist / self.distance_to_next_way_point]

    # rotate sprite correctly
    # self.prev_facing_angle = math.atan2(-self.current_vector[0], -self.current_vector[1]) * 180 / math.pi
    # self.display_image = pygame.transform.rotate(self.original_image, self.prev_facing_angle)
    # old_rect = self.rect
    # self.rect = self.display_image.get_rect()
    # self.rect.center = old_rect.center

    self.should_die = False
    self.sprite_needs_update = True
    self.health_capacity = 100
    self.current_health = self.health_capacity
    self.slow_down_percentage = 1.0

    self.health_bar = UIWorldSpaceHealthBar(pygame.Rect(
        (0, 0), (self.rect.width+4, 8)), sprite_to_monitor=self, container=health_bar_container)
    health_bar_container_rect = health_bar_container.get_rect()

    # hacky method to account for the seperate container that's offset from screen
    # modifying theme parameters in code
    self.health_bar.follow_sprite_offset = (
        -health_bar_container_rect.x, -health_bar_container_rect.y)
    self.health_bar.hover_height = 5

  def kill(self):
    self.health_bar.kill()

  def update(self, dt, plr_resources):
    if self.current_health <= 0:
      self.should_die = True

    if not self.should_die:
      # move towards next waypoint
      if self.distance_to_next_way_point <= 0.0:
        if self.next_way_point_index < (len(self.waypoints) - 1):
          self.next_way_point_index += 1
          next_way_point_centre = self.waypoints[self.next_way_point_index]
          self.next_way_point = self.get_random_point_within_radius(
              next_way_point_centre, 5)

          x_dist = float(self.next_way_point[0]) - float(self.position[0])
          y_dist = float(self.next_way_point[1]) - float(self.position[1])
          self.distance_to_next_way_point = math.sqrt(
              (x_dist * x_dist) + (y_dist * y_dist))
          self.current_vector = [x_dist / self.distance_to_next_way_point,
                                 y_dist / self.distance_to_next_way_point]
        else:
          # monster has reached base
          plr_resources.base_health -= 10
          self.should_die = True

      # move
      self.position[0] += (self.current_vector[0] * dt *
                           self.move_speed * self.slow_down_percentage)
      self.position[1] += (self.current_vector[1] * dt *
                           self.move_speed * self.slow_down_percentage)
      self.distance_to_next_way_point -= dt * \
          self.move_speed * self.slow_down_percentage

      # reset any slowdown from turrets
      self.slow_down_percentage = 1.0
      # set sprite & collision shape positions
      self.rect.center = self.position

    # update animation state
    self.death_anim.update(dt)

    if self.should_die:
      if not self.death_anim.started:
        self.kill()
        self.death_anim.start()
      elif self.death_anim.ended:
        self.all_enemies.remove(self)

  def draw(self, screen: pygame.Surface, map_rect):
    sprite_to_draw = self.display_image
    sprite_rect = self.rect

    if self.should_die:
      # draw death anim
      if self.death_anim.started:
        anim_frame = self.death_anim.get_current_frame()
        anim_frame_rect = anim_frame.get_rect()
        anim_frame_rect.center = self.rect.center

        # replace sprite with anim frame
        sprite_to_draw = anim_frame
        sprite_rect = anim_frame_rect
      else:
        return

    # draw sprite
    # clip the sprite at the map edges
    clipped_rect = sprite_rect.clip(map_rect)
    coord_dx = clipped_rect.x - sprite_rect.x
    coord_dy = clipped_rect.y - sprite_rect.y

    if clipped_rect.width > 0 and clipped_rect.height > 0:
      screen.blit(sprite_to_draw, clipped_rect, area=pygame.Rect(
          coord_dx, coord_dy, clipped_rect.width, clipped_rect.height))

  @staticmethod
  def get_random_point_within_radius(point, radius):
    theta = 2 * math.pi * random()  # get random angle
    return [point[0] + radius * random() * math.cos(theta), point[1] + radius * random() * math.sin(theta)]

  def guess_position_at_time(self, time):
    guess_position = [0.0, 0.0]
    # make sure we don't overshoot monster waypoints with our guesses, or turrets
    # will aim at impossible positions for monsters inside walls.
    if (time * self.move_speed * self.slow_down_percentage) > self.distance_to_next_way_point:
      guess_position[0] = self.next_way_point[0]
      guess_position[1] = self.next_way_point[1]
    else:
      x_move = self.current_vector[0] * time * \
          self.move_speed * self.slow_down_percentage
      y_move = self.current_vector[1] * time * \
          self.move_speed * self.slow_down_percentage
      guess_position[0] = self.position[0] + x_move
      guess_position[1] = self.position[1] + y_move
    return guess_position

  def take_damage(self, damage: int):
    self.current_health -= damage
