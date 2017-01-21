import time


class Animation(object):
    def __init__(self, velocity_coords, target_coords, chain=None):
        super().__init__()
        self.velocity_coords = velocity_coords
        self.target_coords = target_coords
        self.last_update = time.time()
        self.chain = chain


class BoardPosition(object):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
