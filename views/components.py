import pygame


class Component(pygame.sprite.Sprite):
    def __init__(self, image=None, layer=0):
        super(Component, self).__init__()
        self._layer = layer
        self.animation_data = None
        self.image = image
        self.rect = self.image.get_rect()

    def update(self):
        if self.animation_data is not None:
            self.animation_data.function(self)

    def set_topleft(self, pos):
        self.rect.topleft = pos

    def set_center(self, pos):
        self.rect.center = pos

    def set_midtop(self, pos):
        self.rect.midtop = pos

    def set_midbottom(self, pos):
        self.rect.midbottom = pos


class BackgroundComponent(Component):
    def __init__(self, size, color, layer=0):
        image = pygame.Surface(size)
        image.fill(color)

        super(BackgroundComponent, self).__init__(image=image, layer=layer)


class SelectionComponent(BackgroundComponent):
    def __init__(self, size, color, layer=0):
        super(SelectionComponent, self).__init__(size, color, layer)


class TextComponent(Component):
    def __init__(self, text, font_size, font_color, layer=0):
        font = pygame.font.Font(None, font_size)
        font_surface = font.render(text, True, font_color)

        font_sprite_size = font_surface.get_size()
        image = pygame.Surface(font_sprite_size, pygame.SRCALPHA, 32)
        image.blit(font_surface, (0, 0))

        super(TextComponent, self).__init__(image=image, layer=layer)


class ComponentGroup(pygame.sprite.LayeredUpdates):
    def __init__(self):
        super(ComponentGroup, self).__init__()

    def set_location_attribute(self, attribute, new_value):
        # i'm assuming the 0'th layer has the background of the container and
        # should be the whole size of the group
        base_sprite = self.get_sprites_from_layer(0)[0]
        base_val = getattr(base_sprite.rect, attribute)
        setattr(base_sprite.rect, attribute, new_value)

        # we position the rest of the layers relative to the 0th layer, which gets
        # an absolute transformation
        for layer_index in self.layers()[1:]:
            for sprite in self.get_sprites_from_layer(layer_index):
                curr_val = getattr(sprite.rect, attribute)
                new_val = (new_value[0] + curr_val[0] - base_val[0], new_value[1] + curr_val[1] - base_val[1])
                setattr(sprite.rect, attribute, new_val)

    def set_topleft(self, pos):
        self.set_location_attribute("topleft", pos)

    def set_center(self, pos, shift_x=False):
        self.set_location_attribute("center", pos)

    def set_midtop(self, pos, shift_x=False, shift_y=False):
        self.set_location_attribute("midtop", pos)

    def set_midbottom(self, pos, shift_x=False, shift_y=False):
        self.set_location_attribute("midbottom", pos)


class TextContainer(ComponentGroup):
    def __init__(self, text, font_size, font_color, bg_color):
        super(TextContainer, self).__init__()
        text_component = TextComponent(text, font_size, font_color, layer=1)
        background_component = BackgroundComponent(text_component.rect.size, bg_color)
        self.add(background_component)
        self.add(text_component)


class MenuContainer(ComponentGroup):
    def __init__(self, components, bg_color, selection_color, selection_model):
        super(MenuContainer, self).__init__()
        width = 0
        height = 0
        for component in components:
            component_size = component.rect.size
            component_pos = component.rect.topleft
            if width < component_size[0]:
                width = component_size[0]
            component.rect.topleft = (component_pos[0], component_pos[1] + height)
            height += component_size[1]
            component.layer = 2
            self.add(component)
        sel_comp_rect = components[selection_model.sel_index].rect
        selection = SelectionComponent(sel_comp_rect.size, selection_color, 1)
        selection.rect.topleft = sel_comp_rect.topleft
        selection_model.sprite_hash = selection.__hash__()
        self.add(selection)
        self.selection = selection
        background = BackgroundComponent((width, height), bg_color)
        self.add(background)
