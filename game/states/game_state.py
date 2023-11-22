import pygame
import os
import pygame_gui

from pygame_gui.elements.ui_label import UILabel
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_status_bar import UIStatusBar
from game.gun_turret import GunTurret
from .base_game_state import BaseGameState
from .game_state_manager import GameStateManager


class GameState(BaseGameState):
  def __init__(self, state_manager: GameStateManager, game) -> None:
    super().__init__('game', 'main_menu', state_manager)
    self.ui_manager: pygame_gui.UIManager = game.ui_manager
    self.screen = game.screen
    self.in_progress = False

    # ui
    self.map_img = pygame.transform.scale(pygame.image.load(
        os.path.join("data", "images", "level1.jpeg")), (720, 720)).convert()
    self.turret_img = pygame.transform.scale(pygame.image.load(
        os.path.join("data", "images", "turret.png")), (80, 80)).convert_alpha()
    
    self.wave_label = None
    self.health_label = None  
    self.health_status_bar = None
    self.turret_button = None
    self.lose_message_label = None
    self.win_message_label = None
    self.hud_rect = None

    # game state
    self.mouse_active_turret = None
    self.enemies = []
    self.hud_buttons = []
    self.projectiles = []

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
                                         percent_method=lambda: 0.9, anchors={"right": "right", "bottom": "bottom"})

    turret_btn_rect = pygame.Rect((0, 0), (80, 80))
    turret_btn_rect.bottom = 30
    turret_btn_rect.right = -40
    self.turret_button = UIButton(turret_btn_rect, "", object_id="#turret_button",
                                  tool_tip_text="<font size=2><b>Defense Turret</b><br><br>"
                                  "Place this on the map to defend against enemies.</font>", anchors={"right": "right", "centery": "centery"})
    self.in_progress = True

  def end(self):
    # remove game ui
    pass

  def run(self, screen: pygame.Surface, dt):
    for event in pygame.event.get():
      self.ui_manager.process_events(event)

      if event.type == pygame_gui.UI_BUTTON_PRESSED:
        if "#turret_button" in event.ui_object_id:
            new_turret = GunTurret(pygame.mouse.get_pos(), self.turret_img)
            self.mouse_active_turret = new_turret
            self.turrets.append(new_turret)

    self.ui_manager.update(dt/1000)

    screen.fill((0, 0, 0))
    screen.blit(self.map_img, (screen.get_width() /
                2 - self.map_img.get_width() / 2, 0))

    self.ui_manager.draw_ui(screen)
