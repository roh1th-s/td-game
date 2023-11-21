import os

import pygame
import pygame_gui
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_label import UILabel

from states.base_game_state import BaseGameState
from states.game_state_manager import GameStateManager


class MainMenu(BaseGameState):
  def __init__(self, state_manager: GameStateManager, ui_manager: pygame_gui.UIManager) -> None:
    super().__init__('main_menu', 'select_level', state_manager)
    print("Main menu")

    self.ui_manager = ui_manager
    self.bg_image = None
    self.title_label = None
    self.play_btn = None

  def start(self):
    self.bg_image = pygame.transform.scale(pygame.image.load(
        os.path.join("data", "images", "bg.jpg")).convert(), self.ui_manager.window_resolution)
    self.title_label = UILabel(pygame.Rect((0, -150), (850, 180)), text="TDM GAME",
                               manager=self.ui_manager, object_id="#game_title", anchors={"center": "center"})
    self.play_game_button = UIButton(pygame.Rect((0, 70), (200, 70)),
                                     text="Start Game", manager=self.ui_manager, object_id="@start_button",
                                     tool_tip_text="<b>Click to Start.</b>", anchors={"center": "center"})

  def end(self):
    # remove main menu ui
    self.title_label.kill()
    self.play_game_button.kill()

  def run(self, screen, dt):
    for event in pygame.event.get():
      self.ui_manager.process_events(event)

      if event.type == pygame_gui.UI_BUTTON_PRESSED:
        if event.ui_element == self.play_game_button:
          self.set_target_state_name('select_level')
          self.trigger_transition()

    self.ui_manager.update(dt/1000)

    screen.blit(self.bg_image, (0, 0))

    self.ui_manager.draw_ui(screen)
