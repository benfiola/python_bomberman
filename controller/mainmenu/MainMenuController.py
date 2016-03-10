from controller.AbstractController import AbstractController
from models.mainmenu.MainMenuModel import MainMenuModel
from views.mainmenu.MainMenuView import MainMenuView
import pygame, sys

class MainMenuController(AbstractController):
    def __init__(self, previous_controller=None):
        super(MainMenuController, self).__init__(MainMenuView(), MainMenuModel(), previous_controller)

    def process_event(self, event):
        super(MainMenuController, self).process_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_controller = self.previous_controller
            elif event.key == pygame.K_RETURN:
                selection = self.model.get_selection()
                if selection.exit_selection:
                    self.should_exit = True
                elif selection.next_controller_class is not None:
                    self.next_controller = selection.next_controller_class(self)
            elif event.key == pygame.K_UP:
                self.model.previous_option()
                self.view.option_change(self.model)
            elif event.key == pygame.K_DOWN:
                self.model.next_option()
                self.view.option_change(self.model)