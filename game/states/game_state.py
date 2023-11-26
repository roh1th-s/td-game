import pygame
import os
import pygame_gui
from typing import List

from pygame_gui.elements.ui_label import UILabel
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_status_bar import UIStatusBar
from game.enemy import Enemy
from game.enemy_wave_manager import EnemyWaveManager
from game.gun_turret import GunTurret
from game.projectile import Projectile
from .base_game_state import BaseGameState
from .game_state_manager import GameStateManager


class PlayerResources():
  def __init__(self, base_health_capacity=100, ):
    self.base_health = base_health_capacity
    # TODO: Rest


class GameState(BaseGameState):
  def __init__(self, state_manager: GameStateManager, game) -> None:
    super().__init__('game', 'main_menu', state_manager)
    self.ui_manager: pygame_gui.UIManager = game.ui_manager
    self.screen = game.screen
    self.in_progress = False

    # sprites/maps
    self.map_img = pygame.transform.scale(pygame.image.load(
        os.path.join("data", "images", "level1.jpeg")), (720, 720)).convert()
    self.turret_img = pygame.transform.scale(pygame.image.load(
        os.path.join("data", "images", "turret.png")), (80, 80)).convert_alpha()
    self.base_img = pygame.transform.scale_by(pygame.image.load(
        os.path.join("data", "images", "base.png")), 2).convert_alpha()
    self.enemy_img = pygame.transform.scale_by(pygame.image.load(
        os.path.join("data", "images", "enemy.png")), 2).convert_alpha()
    
    self.bullet_img = pygame.Surface((30, 30))
    self.bullet_img.fill((0, 0, 0))
    self.bullet_img.set_colorkey((0, 0, 0))
    circle_color = (200, 200, 200)
    circle_center = (15, 15)
    circle_radius = 15
    pygame.draw.circle(self.bullet_img, circle_color, circle_center, circle_radius)

    self.enemy_spawn_loc = (317, 207)
    self.enemy_waypoints = [(317, 207), (638, 205), (644, 94), (850, 94),
                            (834, 514), (504, 514), (501, 388), (368, 386), (369, 659), (980, 658)]

    # ui
    self.wave_label = None
    self.health_label = None
    self.health_status_bar = None
    self.turret_button = None
    self.lose_message_label = None
    self.win_message_label = None
    self.hud_rect = None

    # game state
    self.base_health_capacity: float = 100
    self.player_resources = PlayerResources(self.base_health_capacity)
    self.mouse_active_turret: GunTurret = None
    self.enemies: List[Enemy] = []
    self.enemy_wave_manager = EnemyWaveManager(
        self.enemies, self.enemy_spawn_loc, self.enemy_waypoints, self.enemy_img, self.ui_manager)
    self.turrets: List[GunTurret] = []
    self.hud_buttons = []
    self.projectiles: List[Projectile] = []

  def start(self):
    print("In game")
    self.wave_label = UILabel(pygame.Rect((10, 0), (200, 50)), text="Wave 1/5",
                              manager=self.ui_manager, object_id="#wave_number")

    health_label_rect = pygame.Rect((0, 0), (200, 100))
    health_label_rect.bottomright = (-30, -30)
    self.health_label = UILabel(health_label_rect, text="Health:",
                                manager=self.ui_manager, object_id="#health_label", anchors={"right": "right", "bottom": "bottom"})

    health_status_rect = pygame.Rect((0, 0), (200, 50))
    health_status_rect.bottomright = (-30, -10)
    self.health_status_bar = UIStatusBar(health_status_rect, object_id="#health_status",
                                         anchors={"right": "right", "bottom": "bottom"})
    self.health_status_bar.percent_full = 100

    turret_btn_rect = pygame.Rect((0, 0), (80, 80))
    turret_btn_rect.bottom = 30
    turret_btn_rect.right = -40
    self.turret_button = UIButton(turret_btn_rect, "", object_id="#turret_button",
                                  tool_tip_text="<font size=2><b>Defense Turret</b><br><br>"
                                  "Place this on the map to defend against enemies.</font>", anchors={"right": "right", "centery": "centery"})

    self.in_progress = True

  def end(self):
    self.in_progress = False

    self.wave_label.kill()
    self.health_label.kill()
    self.health_status_bar.kill()
    self.turret_button.kill()

    for enemy in self.enemies:
      enemy.kill()

  def run(self, screen: pygame.Surface, dt: float):
    mouse_pos = pygame.mouse.get_pos()

    # print(mouse_pos)
    for event in pygame.event.get():
      self.ui_manager.process_events(event)

      if event.type == pygame_gui.UI_BUTTON_PRESSED:
        if "#turret_button" in event.ui_object_id:
          new_turret = GunTurret(mouse_pos, self.turret_img, self.bullet_img)
          self.mouse_active_turret = new_turret
          self.turrets.append(new_turret)

      if event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:  # left mouse btn
          if self.mouse_active_turret:
            tur_rect = self.mouse_active_turret.rect

            cancelled = False
            for turr in self.turrets:
              if turr != self.mouse_active_turret and turr.rect.colliderect(tur_rect):
                # if colliding with another turret, dont let place here
                # cancel turret placement
                self.turrets.remove(self.mouse_active_turret)
                self.mouse_active_turret = None
                cancelled = True

            if not cancelled:
              # valid place point
              self.mouse_active_turret.set_position(mouse_pos)
              self.mouse_active_turret.placed = True
              self.mouse_active_turret = None

    self.enemy_wave_manager.update(dt)

    for enemy in self.enemies:
      enemy.update(dt, self.player_resources)
    for turret in self.turrets:
      turret.update(mouse_pos, dt, self.enemies, self.projectiles)
    for projectile in self.projectiles:
      projectile.update(dt, self.enemies, self.projectiles)

    if self.player_resources.base_health <= 0:
      self.trigger_quit()
      return

    self.health_status_bar.percent_full = self.player_resources.base_health / self.base_health_capacity
    self.ui_manager.update(dt)

    screen.fill((0, 0, 0))

    screen.blit(self.map_img, (screen.get_width() /
                2 - self.map_img.get_width() / 2, 0))
    screen.blit(self.base_img, (950, 550))

    for enemy in self.enemies:
      enemy.draw(screen)
    for turret in self.turrets:
      turret.draw(screen)
    for projectile in self.projectiles:
      projectile.draw(screen)

    self.ui_manager.draw_ui(screen)
