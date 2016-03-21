import pygame

import models
import views


class AbstractController(object):
    def __init__(self, view_class, model_class, previous_controller=None):
        self.model = model_class()
        self.view = view_class(self.model)
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
        self.view.initialize_surface()
        self.view.slide_left()

    def handle_backward_controller_transition(self):
        self.view.slide_right()


class MainMenuController(AbstractController):
    def __init__(self, previous_controller=None):
        super(MainMenuController, self).__init__(views.MainMenuView, models.MainMenuModel, previous_controller)

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
                self.view.option_change()
            elif event.key == pygame.K_DOWN:
                self.model.next_option()
                self.view.option_change()


class MultiplayerController(AbstractController):
    def __init__(self, previous_controller=None):
        super(MultiplayerController, self).__init__(views.MultiplayerView, models.MultiplayerModel, previous_controller)
        pass

    def process_event(self, event):
        super(MultiplayerController, self).process_event(event)
        pass


class MultiplayerOptionsController(AbstractController):
    def __init__(self, previous_controller=None):
        super(MultiplayerOptionsController, self).__init__(views.MultiplayerOptionsView, models.MultiplayerOptionsModel,
                                                           previous_controller)
        pass

    def process_event(self, event):
        super(MultiplayerOptionsController, self).process_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_controller = self.previous_controller


class OptionsController(AbstractController):
    def __init__(self, previous_controller=None):
        super(OptionsController, self).__init__(views.OptionsView, models.OptionsModel, previous_controller)
        pass

    def process_event(self, event):
        super(OptionsController, self).process_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if not self.model.selection.is_active:
                    self.next_controller = self.previous_controller
                else:
                    self.model.set_selection_active()
            if event.key == pygame.K_RETURN:
                pass


class SinglePlayerController(AbstractController):
    def __init__(self, previous_controller=None):
        super(SinglePlayerController, self).__init__(views.SinglePlayerView, models.SinglePlayerModel, previous_controller)
        pass

    def process_event(self, event):
        super(SinglePlayerController, self).process_event(event)
        pass


class SinglePlayerOptionsController(AbstractController):
    def __init__(self, previous_controller=None):
        super(SinglePlayerOptionsController, self).__init__(views.SinglePlayerOptionsView, models.SinglePlayerOptionsModel,
                                                            previous_controller)

    def process_event(self, event):
        super(SinglePlayerOptionsController, self).process_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.next_controller = self.previous_controller


class TitleScreenController(AbstractController):
    def __init__(self, previous_controller=None):
        super(TitleScreenController, self).__init__(views.TitleScreenView, models.TitleScreenModel, previous_controller)

    def process_event(self, event):
        super(TitleScreenController, self).process_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.should_exit = True
            if event.key == pygame.K_RETURN:
                self.next_controller = MainMenuController(self)
