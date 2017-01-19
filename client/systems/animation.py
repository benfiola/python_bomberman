import sdl2.ext
import client.entities as entities
import time


class AnimationSystem(sdl2.ext.Applicator):
    def __init__(self):
        super().__init__()
        self.componenttypes = entities.Animation, sdl2.ext.Sprite

    def process(self, world, components):
        for animation, sprite in components:
            entity = world.get_entities(animation)[0]

            curr_time = time.time()
            time_diff = curr_time - animation.last_update
            vel = (animation.velocity_coords[0] * time_diff, animation.velocity_coords[1] * time_diff)
            old = sprite.position
            new = (
                int(old[0] + vel[0]),
                int(old[1] + vel[1])
            )

            target = animation.target_coords
            new_list = list(new)
            for index in [0, 1]:
                if (old[index] - target[index]) ^ (new[index] - target[index]) < 0:
                    new_list[index] = target[index]
            sprite.position = tuple(new_list)
            if new == animation.target_coords:
                delattr(entity, "animation")







