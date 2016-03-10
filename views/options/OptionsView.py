from views.AbstractView import AbstractView
from views.Colors import Colors
from views.widgets.LabelWidget import LabelWidget


class OptionsView(AbstractView):
    def __init__(self):
        super(OptionsView, self).__init__(bg_color=Colors.GREEN)

    def initialize_surface(self, model):
        super(OptionsView, self).initialize_surface(model)
        title_widget = LabelWidget("Options", 36, Colors.BLACK)

        surface_center = self.surface.get_rect().center
        title_center = title_widget.rect.center

        self.surface.blit(title_widget.image, (surface_center[0]-title_center[0], 0))