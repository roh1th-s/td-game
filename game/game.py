import os
import pygame
from enum import Enum

from pygame_gui import UIManager

from .states.game_state_manager import GameStateManager
from .states.main_menu import MainMenu
from .states.game_state import GameState
from .states.select_level import SelectLevel


class Game:
  def __init__(self, screen: pygame.Surface):
    self.running = True
    self.ui_manager = UIManager(screen.get_size(), theme_path=os.path.join("data", "ui_theme.json"))
    self.ui_manager.preload_fonts([{'name': 'fira_code', 'point_size': 10, 'style': 'bold'},
                                   {'name': 'fira_code', 'point_size': 10, 'style': 'regular'},
                                   {'name': 'fira_code', 'point_size': 14, 'style': 'bold'}])

    assert screen != None
    self.screen = screen

    self.state_manager = GameStateManager(
        {
            "main_menu": MainMenu,
            "select_level": SelectLevel,
            "game": GameState
        },
        "main_menu",
        self
    )

  def run(self):
    clock = pygame.time.Clock()
    dt = 0

    while self.running:
      dt = clock.tick(60)

      self.running = self.state_manager.run(self.screen, dt)

      pygame.display.update()
