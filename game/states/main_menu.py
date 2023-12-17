import os

import pygame
import pygame_gui
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_label import UILabel

from .base_game_state import BaseGameState
from .game_state_manager import GameStateManager


class MainMenu(BaseGameState):
  def __init__(self, state_manager: GameStateManager, game) -> None:
    super().__init__('main_menu', 'select_level', state_manager)
    print("Main menu")

    self.ui_manager = game.ui_manager
    self.bg_image = None
    self.title_label = None
    self.play_btn = None

  def start(self):
    self.bg_image = pygame.transform.scale(pygame.image.load(
        os.path.join("data", "images", "bg.jpg")).convert(), self.ui_manager.window_resolution)

    # TODO: use UITextBox to wrap automatically
    self.title_label_l1 = UILabel(pygame.Rect((0, -130), (920, 100)), text="Guardians Of",
                               manager=self.ui_manager, object_id="#game_title", anchors={"center": "center"})
    self.title_label_l1.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)
    self.title_label_l2 = UILabel(pygame.Rect((0, -40), (920, 100)), text="the Realm",
                               manager=self.ui_manager, object_id="#game_title", anchors={"center": "center"})
    self.title_label_l2.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)
    self.play_game_button = UIButton(pygame.Rect((0, 90), (250, 70)),
                                     text="Start Game", manager=self.ui_manager, object_id="@primary_button",
                                     tool_tip_text="<b>Click to Start.</b>", anchors={"center": "center"})

  def end(self):
    # remove main menu ui
    self.title_label_l1.kill()
    self.title_label_l2.kill()
    self.play_game_button.kill()

  def run(self, screen: pygame.Surface, dt: float):
    for event in pygame.event.get():
      self.ui_manager.process_events(event)

      if event.type == pygame_gui.UI_BUTTON_PRESSED:
        if event.ui_element == self.play_game_button:
          self.set_target_state_name('select_level')
          self.trigger_transition()

    self.ui_manager.update(dt)

    screen.fill((0, 0, 0))
    # screen.blit(self.bg_image, (0, 0))

    self.ui_manager.draw_ui(screen)
