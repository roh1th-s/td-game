import copy
import pygame
import typing

from states.base_game_state import BaseGameState


class GameStateManager:
  def __init__(self, game_states: typing.Dict[str, typing.Type[BaseGameState]], initial_state: str, game):
    self.states: typing.Dict[str, typing.Type[BaseGameState]] = {}
    self.active_state: BaseGameState = None

    for state_name in game_states:
      # create an object of game_state class
      state = game_states[state_name](self, game)
      self.states[state_name] = state

      if state_name == initial_state:
        self.active_state = state
        # start the initial state
        self.active_state.start()

  def run(self, screen: pygame.Surface, dt: float):
    quit_event = pygame.event.get(pygame.QUIT)
    if quit_event:
      return False
    
    if self.active_state is not None:
      self.active_state.run(screen, dt)

      if self.active_state.time_to_transition:
        self.active_state.time_to_transition = False
        new_state_name = self.active_state.target_state_name
        self.active_state.end()
        outgoing_data_copy = copy.deepcopy(self.active_state.outgoing_transition_data)
        self.active_state = self.states[new_state_name]
        self.active_state.incoming_transition_data = outgoing_data_copy
        self.active_state.start()

      if self.active_state.time_to_quit_app:
        return False

    return True

  def set_initial_state(self, name):
    if name in self.states:
      self.active_state = self.states[name]
      self.active_state.start()
