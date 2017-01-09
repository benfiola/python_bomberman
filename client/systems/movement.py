import sdl2.ext
import client.entities as entities
import time


class MenuMovementSystem(sdl2.ext.Applicator):
    def __init__(self):
        super().__init__()
        self.componenttypes = entities.Velocity, sdl2.ext.Sprite

    def process(self, world, components):
        for velocity, sprite in components:
            curr_time = time.time()
            time_diff = curr_time - velocity.last_update
            vel = (velocity.velocity_coords[0] * time_diff, velocity.velocity_coords[1] * time_diff)
            old = sprite.position
            new = (
                int(old[0] + vel[0]),
                int(old[1] + vel[1])
            )

            if velocity.target_coords:
                target = velocity.target_coords
                new_list = list(new)
                for index in [0, 1]:
                    if old[index] <= target[index] and new[index] >= target[index]:
                        new_list[index] = target[index]
                    if old[index] >= target[index] and new[index] <= target[index]:
                        new_list[index] = target[index]
                new = tuple(new_list)

            sprite.position = new
            if new == velocity.target_coords:
                entities = world.get_entities(velocity)
                for entity in entities:
                    delattr(entity, "velocity")







