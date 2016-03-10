from views.AbstractView import AbstractView
from views.Colors import Colors
from views.widgets.LabelWidget import LabelWidget
import pygame
from pygame.sprite import LayeredUpdates
from views.widgets.MenuContainer import MenuContainer
from views.widgets.MyLayeredUpdates import MyLayeredUpdates
from views.widgets.SelectionWidget import SelectionWidget


class MainMenuView(AbstractView):

    def __init__(self):
        super(MainMenuView, self).__init__(bg_color=Colors.BLUE)
        self.title = None
        self.container = None
        self.selection = None

    def initialize_surface(self, model):
        super(MainMenuView, self).initialize_surface(model)

        # prepare the title
        self.title = LabelWidget("Main Menu", 36, Colors.WHITE)
        surface_center = self.surface.get_rect().center
        title_center = self.title.rect.center
        title_position = (surface_center[0]-title_center[0], 0)

        # prepare the menu options container
        font_size = 24
        option_widgets = []
        for option in model.options:
            curr_widget = LabelWidget(option.text, font_size, Colors.WHITE, padding=(12,12,12,12))
            option_widgets.append(curr_widget)

        self.container = MenuContainer(option_widgets, Colors.BLACK)
        container_center = self.container.rect.center
        container_position = (surface_center[0]-container_center[0], surface_center[1])

        title_layer_group = self.title.to_layer_group()
        container_layer_group = self.container.to_layer_group()
        title_layer_group.position(title_position)
        container_layer_group.position(container_position)
        title_layer_group.draw(self.surface)
        container_layer_group.draw(self.surface)

        self.layer_groups.append(self.title.to_layer_group())
        self.layer_groups.append(self.container.to_layer_group())

    def option_change(self, model):
        self.container.option_change(model.selection)











