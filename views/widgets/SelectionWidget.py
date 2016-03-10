import pygame
import math
from views.widgets.MySprite import MySprite


class SelectionWidget(MySprite):
    def __init__(self, size, color):
        super(SelectionWidget, self).__init__()
        self.image = pygame.Surface(size)
        self.image.fill(color)

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()


