import time


class Animation(object):
    def __init__(self, velocity_coords, target_coords, clipping_container):
        super().__init__()
        self.velocity_coords = velocity_coords
        self.target_coords = target_coords
        self.last_update = time.time()
        self.clipping_container = clipping_container


class BoardPosition(object):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
