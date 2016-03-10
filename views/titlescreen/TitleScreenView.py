from views.AbstractView import AbstractView
from views.Colors import Colors
from views.widgets.LabelWidget import LabelWidget


class TitleScreenView(AbstractView):
    def __init__(self):
        super(TitleScreenView, self).__init__(bg_color=Colors.RED)
        self.title = None
        self.subtext = None

    def initialize_surface(self, model):
        super(TitleScreenView, self).initialize_surface(model)
        self.title = LabelWidget("Bombenman", 72, Colors.WHITE)
        self.subtext = LabelWidget("Press enter", 36, Colors.WHITE)

        surface_center = self.surface.get_rect().center
        title_center = self.title.rect.center
        subtext_center = self.subtext.rect.center

        title_position = (surface_center[0]-title_center[0],0)
        subtext_position = (surface_center[0]-subtext_center[0], surface_center[1] + (surface_center[1]/2))

        title_layer_group = self.title.to_layer_group(title_position)
        subtext_layer_group = self.subtext.to_layer_group(subtext_position)
        self.layer_groups.extend([title_layer_group, subtext_layer_group])



