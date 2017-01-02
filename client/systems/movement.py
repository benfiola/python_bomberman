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
            d_x, d_y = (velocity.velocity_coords[0] * time_diff, velocity.velocity_coords[1] * time_diff)
            o_x, o_y = sprite.position
            n_x, n_y = (
                int(o_x + d_x),
                int(o_y + d_y)
            )

            if velocity.target_coords:
                t_x, t_y = velocity.target_coords
                if (o_x <= t_x and n_x >= t_x) or (o_x >= t_x and n_x <= t_x):
                    n_x = t_x
                if (o_y <= t_y and n_y >= t_y) or (o_y >= t_y and n_y <= t_y):
                    n_y = t_y

            if (n_x, n_y) == velocity.target_coords:
                velocity = None
            sprite.position = (n_x, n_y)







