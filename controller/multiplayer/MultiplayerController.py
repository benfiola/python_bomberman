from controller.AbstractController import AbstractController
from views.multiplayer.MultiplayerView import MultiplayerView
import pygame

class MultiplayerController(AbstractController):
    def __init__(self, previous_controller=None):
        super(MultiplayerController, self).__init__(MultiplayerView(), None, previous_controller)
        pass

    def process_event(self, event):
        super(MultiplayerController, self).process_event(event)
        pass