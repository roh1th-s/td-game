import threading
import time
from .enemy import Enemy


class EnemyWaveManager:

  def __init__(self, enemies, enemy_spawn_loc, enemy_waypoints, enemy_sprite, ui_manager):
    self.ui_manager = ui_manager
    self.spawn_location = enemy_spawn_loc
    self.enemies = enemies  # this is a reference to the game_state enemies array
    self.enemy_wavepoints = enemy_waypoints
    self.enemy_sprite = enemy_sprite

    # wave settings
    self.maximum_waves = 5
    self.number_of_sub_waves = 1
    self.next_wave_countdown_time = 5.0
    self.time_between_waves = 30.0
    self.time_between_enemy_spawns = 0.7
    self.sub_wave_time = 4.0
    # wave points determine how many enemies can be spawned in the wave
    self.initial_wave_points = 10
    self.point_increase_per_wave = 10
    # point cost to spawn the enemy (decremented from wave points)
    self.enemy_cost = 1

    # state
    self.current_wave_number = 0
    self.waves_over = False
    self.current_sub_wave = 0
    self.current_wave_points = self.initial_wave_points
    self.spawning_sub_waves = False
    self.should_show_wave_countdown = False
    self.sub_wave_acc = 2.0
    self.enemy_spawn_cooldown_acc = self.time_between_enemy_spawns
    self.wave_time_acc = self.time_between_waves
    self.count_down_message = ""
    self.changed_wave = False

  def update(self, dt):
    # if all enemies dead, speed up next wave arrival
    countdown_start_time = self.time_between_waves - self.next_wave_countdown_time

    if not self.spawning_sub_waves and len(self.enemies) == 0 and self.wave_time_acc < 25.0:
      self.wave_time_acc = countdown_start_time

    new_wave_countdown = str(int(self.time_between_waves - self.wave_time_acc))

    if self.wave_time_acc >= self.time_between_waves and\
            self.current_wave_number < self.maximum_waves:
      self.should_show_wave_countdown = False
      self.spawn_new_wave()
      self.wave_time_acc = 0.0
    elif self.wave_time_acc >= countdown_start_time and self.current_wave_number < self.maximum_waves:
      self.count_down_message = "New wave in " + new_wave_countdown + " seconds"
      self.should_show_wave_countdown = True
      self.wave_time_acc += dt
    elif self.current_wave_number < self.maximum_waves:
      self.wave_time_acc += dt
    elif self.current_wave_number >= self.maximum_waves and self.current_sub_wave >= self.number_of_sub_waves and not self.spawning_sub_waves:
      if len(self.enemies) == 0:
        self.waves_over = True

    if self.spawning_sub_waves:
      if self.sub_wave_acc > self.sub_wave_time:
        self.sub_wave_acc = 0.0
        self.spawn_new_sub_wave(
            int(self.current_wave_points / self.number_of_sub_waves))
      else:
        self.enemy_spawn_cooldown_acc += dt
        self.sub_wave_acc += dt

      if self.current_sub_wave >= self.number_of_sub_waves:
        self.spawning_sub_waves = False
        self.point_increase_per_wave = self.point_increase_per_wave + \
            ((self.current_wave_number + 1) * 12)
        self.current_wave_points = self.initial_wave_points + self.point_increase_per_wave

  def spawn_new_wave(self):
    self.changed_wave = True
    self.current_wave_number += 1

    self.number_of_sub_waves = self.current_wave_number
    self.current_sub_wave = 0
    self.spawning_sub_waves = True

  def spawn_new_sub_wave(self, points):
    sub_wave_points = points
    self.current_sub_wave += 1

    def spawn_enemy():
      nonlocal sub_wave_points
      while sub_wave_points >= self.enemy_cost:
        new_enemy = Enemy(self.enemies, self.enemy_wavepoints, self.enemy_sprite,
                          self.enemy_cost, self.spawn_location, self.ui_manager)
        self.enemies.append(new_enemy)
        self.current_wave_points -= self.enemy_cost
        sub_wave_points -= self.enemy_cost
        time.sleep(self.time_between_enemy_spawns)

    # launching a thread to spawn enemies with a time gap between them
    t = threading.Thread(target=spawn_enemy)
    t.start()

  def has_changed_wave(self) -> bool:
    if self.changed_wave:
      self.changed_wave = False
      return True
