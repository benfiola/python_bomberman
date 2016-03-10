import pygame

class AbstractController(object):
    def __init__(self, view, model, previous_controller=None):
        self.view = view
        self.model = model
        self.next_controller = None
        self.previous_controller = previous_controller
        self.should_exit = False

    def process_event(self, event):
        if event.type == pygame.QUIT:
            self.should_exit = True

    def process_events(self, pygame_events):
        for event in pygame_events:
            self.process_event(event)
        self.view.update()

    def handle_forward_controller_transition(self):
        self.view.initialize_surface(self.model)
        self.view.slide_left()

    def handle_backward_controller_transition(self):
        self.view.slide_right()
