from controller.AbstractController import AbstractController
import pygame
from views.options.OptionsView import OptionsView


class OptionsController(AbstractController):
    def __init__(self, previous_controller=None):
        super(OptionsController, self).__init__(OptionsView(), None, previous_controller)
        pass

    def process_event(self, event):
        super(OptionsController, self).process_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_controller = self.previous_controller