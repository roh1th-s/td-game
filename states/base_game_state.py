import pygame


class BaseGameState:
    def __init__(self, name: str, target_state_name: str, state_manager):
        self.name = name
        self.target_state_name = target_state_name
        self.outgoing_transition_data = {}
        self.incoming_transition_data = {}
        self.state_manager = state_manager
        self.time_to_transition = False
        self.time_to_quit_app = False

    def set_target_state_name(self, target_name: str):
        self.target_state_name = target_name

    def trigger_transition(self):
        self.time_to_transition = True

    def start(self):
        pass

    def end(self):
        pass

    def run(self, surface: pygame.Surface, dt: float):
        pass
