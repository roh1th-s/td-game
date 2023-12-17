import pygame
import os
import pygame_gui
from typing import List, Tuple

from pygame_gui.elements.ui_label import UILabel
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_status_bar import UIStatusBar
from pygame_gui.elements.ui_panel import UIPanel
from game.enemy import Enemy
from game.enemy_wave_manager import EnemyWaveManager
from game.turrets.double_turret import DoubleTurret
from game.turrets.normal_turret import NormalTurret
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

    # sprites/maps
    self.map_img = pygame.transform.scale(pygame.image.load(
        os.path.join("data", "images", "level1.jpeg")), (720, 720)).convert()
    self.base_img = pygame.transform.scale_by(pygame.image.load(
        os.path.join("data", "images", "base.png")), 2).convert_alpha()
    self.enemy_img = pygame.transform.scale_by(pygame.image.load(
        os.path.join("data", "images", "enemy.png")), 2).convert_alpha()
    self.projectile_img = pygame.transform.scale_by(pygame.image.load(
        os.path.join("data", "images", "projectile.png")), 0.7).convert_alpha()
    self.turret_imgs = [
        pygame.transform.scale(pygame.image.load(
            os.path.join("data", "images", "turret.png")), (50, 50)).convert_alpha(),
        pygame.transform.scale(pygame.image.load(
            os.path.join("data", "images", "turret2.png")), (50, 50)).convert_alpha()
    ]

    # self.bullet_img = pygame.Surface((30, 30))
    # self.bullet_img.fill((0, 0, 0))
    # self.bullet_img.set_colorkey((0, 0, 0))
    # circle_color = (200, 200, 200)
    # circle_center = (15, 15)
    # circle_radius = 15
    # pygame.draw.circle(self.bullet_img, circle_color,
    #                    circle_center, circle_radius)

    # settings
    self.enemy_waypoints = [(240, 207), (638, 205), (644, 90), (850, 90),
                            (834, 514), (504, 514), (501, 388), (363, 386), (363, 659), (1024, 658)]
    self.base_health_capacity: float = 100

    # ui
    self.wave_label = None
    self.health_label = None
    self.health_status_bar = None
    self.normal_turret_btn = None
    self.lose_message_label = None
    self.win_message_label = None
    self.hud_rect = None

    # game state
    self.in_progress = False
    self.player_resources = PlayerResources(self.base_health_capacity)
    self.mouse_active_turret: NormalTurret = None
    self.enemies: List[Enemy] = []
    self.enemy_wave_manager = EnemyWaveManager(
        self.enemies, self.enemy_waypoints, self.enemy_img, self.ui_manager, self)
    self.turrets: List[NormalTurret] = []
    self.hud_buttons = []
    self.projectiles: List[Projectile] = []

  def start(self):
    print("Game start")
    self.wave_label = UILabel(pygame.Rect((10, 0), (250, 50)), text="Game starting...",
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

    normal_turret_btn_rect = pygame.Rect((0, 0), (80, 80))
    normal_turret_btn_rect.bottom = 30
    normal_turret_btn_rect.right = -40
    self.normal_turret_btn = UIButton(normal_turret_btn_rect, "", object_id="#turret1_button",
                                      tool_tip_text="<font size=2><b>Normal turret</b><br><br>Fires a single projectile.</font>",
                                      anchors={"right": "right", "centery": "centery"})

    double_turret_btn_rect = normal_turret_btn_rect.copy()
    double_turret_btn_rect.bottom = 110
    self.double_turret_btn = UIButton(double_turret_btn_rect, "", object_id="#turret2_button",
                                      tool_tip_text="<font size=2><b>Double Turret</b><br><br>Shoots two projectiles.</font>",
                                      anchors={"right": "right", "centery": "centery"})

    self.end_screen_panel = UIPanel(pygame.Rect((0, 0), self.ui_manager.get_root_container().get_size()),
                                    starting_height=3, manager=self.ui_manager, object_id="#end_screen_panel")
    self.end_screen_panel.hide()
    self.end_screen_container = self.end_screen_panel.get_container()

    self.enemy_health_bar_panel = UIPanel(pygame.Rect(
        (self.screen.get_width() / 2 - self.map_img.get_width() / 2, 0),
        self.map_img.get_size()
    ), starting_height=1, manager=self.ui_manager, object_id="@transparent_panel")
    self.enemy_health_bar_container = self.enemy_health_bar_panel.get_container()

    self.win_message_label = UILabel(pygame.Rect((0, -100), (850, 180)), text="You win!",
                                     manager=self.ui_manager, container=self.end_screen_container, object_id="#win_label", anchors={"center": "center"})
    self.lose_message_label = UILabel(pygame.Rect((0, -100), (850, 180)), text="You lose :(",
                                      manager=self.ui_manager, container=self.end_screen_container, object_id="#win_label", anchors={"center": "center"})
    # self.end_screen_panel.show()
    # self.lose_message_label.hide()

    self.main_menu_button = UIButton(pygame.Rect((0, 10), (310, 70)),
                                     text="<- Back to main menu", container=self.end_screen_container, object_id="#main_menu_button",
                                     tool_tip_text="<b>Click to return to main menu.</b>", anchors={"center": "center"})

    self.quit_button = UIButton(pygame.Rect((0, 90), (310, 70)),
                                text="Quit", container=self.end_screen_container, object_id="#quit_button",
                                tool_tip_text="<b>Click to exit the game.</b>", anchors={"center": "center"})
    self.in_progress = True

  def end(self):
    self.in_progress = False

    self.wave_label.kill()
    self.health_label.kill()
    self.health_status_bar.kill()
    self.normal_turret_btn.kill()
    self.double_turret_btn.kill()
    self.enemy_health_bar_panel.kill()
    self.end_screen_panel.kill()

    for enemy in self.enemies:
      enemy.kill()

    # reset ui
    self.wave_label = None
    self.health_label = None
    self.health_status_bar = None
    self.normal_turret_btn = None
    self.lose_message_label = None
    self.win_message_label = None
    self.hud_rect = None

    # reset game state
    self.in_progress = False
    self.player_resources = PlayerResources(self.base_health_capacity)
    self.mouse_active_turret: NormalTurret or DoubleTurret = None
    self.enemies = []
    self.enemy_wave_manager = EnemyWaveManager(
        self.enemies, self.enemy_waypoints, self.enemy_img, self.ui_manager, self)
    self.turrets = []
    self.hud_buttons = []
    self.projectiles = []

  def update_entities(self, dt: float, mouse_pos: Tuple[int, int]):
    self.enemy_wave_manager.update(dt)

    for enemy in self.enemies:
      enemy.update(dt, self.player_resources)
    for turret in self.turrets:
      turret.update(mouse_pos, dt, self.enemies, self.projectiles)
    for projectile in self.projectiles:
      projectile.update(dt, self.enemies, self.projectiles)

  def update_ui(self, dt: float):
    self.wave_label.set_text(
        f"Wave {self.enemy_wave_manager.current_wave_number}/{self.enemy_wave_manager.maximum_waves}")
    self.health_status_bar.percent_full = self.player_resources.base_health / \
        self.base_health_capacity
    self.ui_manager.update(dt)

  def draw(self, screen: pygame.Surface):
    screen.fill((0, 0, 0))

    screen.blit(self.map_img, (screen.get_width() /
                2 - self.map_img.get_width() / 2, 0))

    # screen.blit(self.base_img, (950, 550))

    for enemy in self.enemies:
      enemy.draw(screen, pygame.Rect(
          (screen.get_width() / 2 - self.map_img.get_width() / 2, 0),
          self.map_img.get_size()
      ))
    for turret in self.turrets:
      turret.draw(screen)
    for projectile in self.projectiles:
      projectile.draw(screen)

    self.ui_manager.draw_ui(screen)

  def run(self, screen: pygame.Surface, dt: float):
    mouse_pos = pygame.mouse.get_pos()

    # handle events
    for event in pygame.event.get():
      self.ui_manager.process_events(event)

      if event.type == pygame_gui.UI_BUTTON_PRESSED:
        if event.ui_element == self.main_menu_button:
          self.target_state_name = "main_menu"
          self.trigger_transition()
          return
        elif event.ui_element == self.quit_button:
          self.trigger_quit()
          return

        if self.in_progress:
          if event.ui_element == self.normal_turret_btn:
            new_turret = NormalTurret(
                mouse_pos, self.turret_imgs[0], self.projectile_img)
            self.mouse_active_turret = new_turret
            self.turrets.append(new_turret)
          elif event.ui_element == self.double_turret_btn:
            new_turret = DoubleTurret(
                mouse_pos, self.turret_imgs[1], self.projectile_img)
            self.mouse_active_turret = new_turret
            self.turrets.append(new_turret)

      if event.type == pygame.MOUSEBUTTONUP:
        if event.button == 1:  # left mouse btn
          if self.in_progress:
            if self.mouse_active_turret:
              tur_rect = self.mouse_active_turret.rect

              cancelled = False
              for turr in self.turrets:
                if turr != self.mouse_active_turret and turr.rect.colliderect(tur_rect):
                  # if colliding with another turret, dont let place here
                  # cancel turret placement
                  if self.mouse_active_turret in self.turrets:
                    self.turrets.remove(self.mouse_active_turret)

                  self.mouse_active_turret = None
                  cancelled = True

              if not cancelled:
                # valid place point
                self.mouse_active_turret.set_position(mouse_pos)
                self.mouse_active_turret.placed = True
                self.mouse_active_turret = None

    if self.in_progress:
      self.update_entities(dt, mouse_pos)

    # handle game end
    if self.in_progress and self.enemy_wave_manager.waves_over:
      self.end_screen_panel.show()
      self.lose_message_label.hide()
      self.win_message_label.show()
      print("You won!")
      self.in_progress = False
      return

    if self.in_progress and self.player_resources.base_health <= 0:
      self.end_screen_panel.show()
      self.win_message_label.hide()
      self.lose_message_label.show()
      print("Game over")
      self.in_progress = False
      return

    self.update_ui(dt)

    # draw stuff
    self.draw(screen)
