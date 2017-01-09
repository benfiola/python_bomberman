import sdl2.ext


class Colors(object):
    BLUE = sdl2.ext.Color(0, 0, 255)
    RED = sdl2.ext.Color(255, 0, 0)
    GREEN = sdl2.ext.Color(0, 255, 0)
    WHITE = sdl2.ext.Color(255, 255, 255)
    BLACK = sdl2.ext.Color(0, 0, 0)
    YELLOW = sdl2.ext.Color(255, 255, 0)
    PURPLE = sdl2.ext.Color(255, 0, 255)
    LIGHT_BLUE = sdl2.ext.Color(0, 255, 255)
    GRAY = sdl2.ext.Color(128, 128, 128)
    ORANGE = sdl2.ext.Color(255, 165, 0)
    BROWN = sdl2.ext.Color(165, 42, 42)

    @classmethod
    def find_color(cls, color_string):
        to_return = getattr(cls, color_string.upper(), None)
        return to_return
