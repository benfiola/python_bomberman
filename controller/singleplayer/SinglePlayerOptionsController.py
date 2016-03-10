import pygame
from controller.AbstractController import AbstractController
from views.singleplayer.SinglePlayerOptionsView import SinglePlayerOptionsView


class SinglePlayerOptionsController(AbstractController):
    def __init__(self, previous_controller=None):
        super(SinglePlayerOptionsController, self).__init__(SinglePlayerOptionsView(), None, previous_controller)

    def process_event(self, event):
        super(SinglePlayerOptionsController, self).process_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_controller = self.previous_controller