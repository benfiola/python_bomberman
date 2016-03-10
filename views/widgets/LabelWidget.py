import pygame
from views.Colors import Colors
from views.widgets.MySprite import MySprite


class LabelWidget(MySprite):
    def __init__(self, text, font_size, color, padding=(0,0,0,0)):
        super(LabelWidget, self).__init__()

        font = pygame.font.Font(None, font_size)
        font_surface = font.render(text, True, color)

        padding_top = padding[0]
        padding_right = padding[1]
        padding_bottom = padding[2]
        padding_left = padding[3]

        font_sprite_size = font_surface.get_size()
        image_size = (font_sprite_size[0]+padding_left+padding_right, font_sprite_size[1]+padding_top+padding_bottom)
        self.image = pygame.Surface(image_size, pygame.SRCALPHA, 32)
        self.image.blit(font_surface, (padding_left,padding_top))

        # Fetch the rectangle object that has the dimensions of the image
        # Update the position of this object by setting the values of rect.x and rect.y
        self.rect = self.image.get_rect()