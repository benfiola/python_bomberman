from controller.AbstractController import AbstractController
import pygame
from views.singleplayer.SinglePlayerView import SinglePlayerView


class SinglePlayerController(AbstractController):
    def __init__(self, previous_controller=None):
        super(SinglePlayerController, self).__init__(SinglePlayerView(), None, previous_controller)
        pass

    def process_event(self, event):
        super(SinglePlayerController, self).process_event(event)
        pass