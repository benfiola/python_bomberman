class Map(object):
    def __init__(self, dimensions, spawns):
        self.dimensions = dimensions
        self.spawns = spawns


class EntitySpawn(object):
    def __init__(self, mapping, position):
        self.character_mapping = mapping
        self.position = position


class PlayerSpawn(EntitySpawn):
    def __init__(self, position=None):
        super().__init__('P', position)


class IndestructibleWallSpawn(EntitySpawn):
    def __init__(self, position=None):
        super().__init__('W', position)


class DestructibleWallSpawn(EntitySpawn):
    def __init__(self, position=None):
        super().__init__('D', position)


class MapLoader(object):
    def __init__(self, filename):
        self.filename = filename
        self.spawn_map = self.generate_spawn_map()

    def generate_spawn_map(self):
        to_return = {}
        subclasses = EntitySpawn.__subclasses__()
        for subclass in subclasses:
            spawn = subclass()
            to_return[spawn.character_mapping] = subclass
        to_return['_'] = None
        return to_return

    def load(self):
        f = open(self.filename, 'r')
        file_string = f.read()
        f.close()
        lines = file_string.split("\n")
        if len(lines) == 0:
            raise Exception("Load error - map has no lines.")
        width = len(lines[0])
        height = len(lines)
        spawns = []
        for y, line in enumerate(lines):
            if len(line) != width:
                raise Exception("Load error - map has inconsistent line lengths.")
            for x, character in enumerate(line):
                if character not in self.spawn_map:
                    raise Exception("Load error - character %s unrecognized." % (character))
                spawn_class = self.spawn_map[character]
                if spawn_class:
                    spawns.append(spawn_class((x, y)))
        new_map = Map((width, height), spawns)
        return new_map



