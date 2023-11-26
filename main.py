import pygame

if __name__ == "__main__":
  # init
  pygame.init()
  screen = pygame.display.set_mode((1280, 720))
  pygame.display.set_caption("Tower defense :)")

  # import here so display.set_mode runs before other code
  from game.game import Game
  game = Game(screen)
  game.run()

  # clean up
  pygame.quit()
