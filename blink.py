import board
from ideabord import IdeaBoard
from time import sleep

ib = IdeaBoard()

BLACK = (0,0,0)
RED = (255,0,0)
GREEN = (0,255,0)
BLUE = (0,0,255)
WHITE = (255,255,255)

while True:
    ib.pixel = BLUE
    sleep(1)
    ib.pixel = BLACK
    sleep(1)
    