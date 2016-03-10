from controller.AbstractController import AbstractController
from controller.mainmenu.MainMenuController import MainMenuController
from views.titlescreen.TitleScreenView import TitleScreenView
import pygame, sys

class TitleScreenController(AbstractController):
    def __init__(self, previous_controller=None):
        super(TitleScreenController, self).__init__(TitleScreenView(), None, previous_controller)

    def process_event(self, event):
        super(TitleScreenController, self).process_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.should_exit = True
            if event.key == pygame.K_RETURN:
                self.next_controller = MainMenuController(self)