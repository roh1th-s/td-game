import pygame
import pygame_gui

from states.base_game_state import BaseGameState
from states.game_state_manager import GameStateManager


class GameState(BaseGameState):
  def __init__(self, state_manager: GameStateManager, ui_manager: pygame_gui.UIManager) -> None:
    super().__init__('game', 'main_menu', state_manager)
    self.ui_manager = ui_manager

  def start(self):
    print("In game")
    print(self.incoming_transition_data)

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

    self.ui_manager.draw_ui(screen)
