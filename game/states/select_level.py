import os
import pygame
import pygame_gui
from pygame_gui.elements.ui_button import UIButton
from .base_game_state import BaseGameState
from .game_state_manager import GameStateManager


class SelectLevel(BaseGameState):
  def __init__(self, state_manager: GameStateManager, game) -> None:
    super().__init__('select_level', 'game', state_manager)

    self.ui_manager = game.ui_manager
    self.bg_image = pygame.transform.scale(pygame.image.load(
        os.path.join("data", "images", "bg.jpg")).convert(), game.screen.get_size())
    self.level1_btn = None

  def start(self):
    print("select level")

    # temporarily hardcoded
    self.level1_btn = UIButton(pygame.Rect((0, 0), (200, 200)),
                               text="Level 1", manager=self.ui_manager, object_id="@primary_button",
                               tool_tip_text="<b>Play Level 1</b>", anchors={"center": "center"})

  def end(self):
    # remove select ui
    self.level1_btn.kill()

  def run(self, screen: pygame.Surface, dt):
    for event in pygame.event.get():
      self.ui_manager.process_events(event)

      if event.type == pygame_gui.UI_BUTTON_PRESSED:
        if event.ui_element == self.level1_btn:
          self.set_target_state_name('game')
          self.outgoing_transition_data = {"level": 1}
          self.trigger_transition()

    self.ui_manager.update(dt)

    screen.fill((0, 0, 0))
    # screen.blit(self.bg_image, (0, 0))

    self.ui_manager.draw_ui(screen)
