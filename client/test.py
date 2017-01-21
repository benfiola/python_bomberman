import client.platform_utils as platform_utils
platform = platform_utils.Platform.get_platform()
platform.configure_paths()
import sdl2.ext

WHITE = sdl2.ext.Color(255, 255, 255, 255)
CLEAR = sdl2.ext.Color(255, 255, 255, 0)

sdl2.ext.init()
window = sdl2.ext.Window("The Pong Game", size=(800, 600))
#  renderer = sdl2.ext.Renderer(window)
#  factory = sdl2.ext.SpriteFactory(sdl2.ext.TEXTURE, renderer=renderer)
factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE)
rsys = factory.create_sprite_render_system(window)
world = sdl2.ext.World()
world.add_system(rsys)

class Test(sdl2.ext.Entity):
    def __init__(self, world, sprite, depth, position):
        self.sprite = sprite
        self.sprite.depth = depth
        self.sprite.position = position

t = Test(world,
         factory.from_color(WHITE, size=(100, 100), masks=(0xFF000000, 0x00FF0000, 0x0000FF00, 0x000000FF)),
         0,
         (0, 0))
sdl2.ext.fill(t.sprite, CLEAR, (10, 10, 30, 30))

window.show()
running = True
while running:
    events = sdl2.ext.get_events()
    for event in events:
        if event.type == sdl2.SDL_QUIT:
            running = False
            break
    world.process()
    window.refresh()
