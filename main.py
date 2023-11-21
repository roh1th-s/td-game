import pygame

if __name__ == "__main__":
  # init 
  pygame.init()
  screen = pygame.display.set_mode((1280, 720))
  pygame.display.set_caption("Tower defense :)")

  button_layout_rect = pygame.Rect(0, 0, 100, 20)
  button_layout_rect.bottomright = (-30, -20)
  print(button_layout_rect)
  # import here so display.set_mode runs before other code
  from game import Game
  game = Game(screen)
  game.run()

  # clean up
  pygame.quit()
