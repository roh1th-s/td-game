import pygame
import os
import pygame_gui

from pygame_gui.elements.ui_label import UILabel
from states.base_game_state import BaseGameState
from states.game_state_manager import GameStateManager


class GameState(BaseGameState):
  def __init__(self, state_manager: GameStateManager, game) -> None:
    super().__init__('game', 'main_menu', state_manager)
    self.ui_manager: pygame_gui.UIManager = game.ui_manager
    self.screen = game.screen
    self.in_progress = False

    # ui
    self.map_img = pygame.transform.scale(pygame.image.load(
        os.path.join("data", "images", "level1.jpeg")), (720, 720)).convert()
    
    self.wave_label = None
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
    self.wave_label = UILabel(pygame.Rect((10, 0), (200, 100)), text="Wave 1/5",
                               manager=self.ui_manager, container=self.ui_manager.get_root_container(),object_id="#wave_number")
    # self.hud_rect = pygame.Rect(0, self.screen_data.screen_size[1] - 128,
    #                             self.screen_data.screen_size[0], 128)

  def end(self):
    # remove game ui
    pass

  def run(self, screen: pygame.Surface, dt):
    for event in pygame.event.get():
      self.ui_manager.process_events(event)

      if event.type == pygame_gui.UI_BUTTON_PRESSED:
        pass

    self.ui_manager.update(dt/1000)

    screen.fill((0, 0, 0))
    screen.blit(self.map_img, (screen.get_width() /
                2 - self.map_img.get_width() / 2, 0))

    self.ui_manager.draw_ui(screen)
