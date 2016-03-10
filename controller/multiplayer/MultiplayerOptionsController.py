from controller.AbstractController import AbstractController
import pygame
from views.multiplayer.MultiplayerOptionsView import MultiplayerOptionsView


class MultiplayerOptionsController(AbstractController):
    def __init__(self, previous_controller=None):
        super(MultiplayerOptionsController, self).__init__(MultiplayerOptionsView(), None, previous_controller)
        pass

    def process_event(self, event):
        super(MultiplayerOptionsController, self).process_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_controller = self.previous_controller