import os
import json
from .spawns import *


class SpawnConverter(object):
    """
    A spawn converter simply handles Spawn object serialization-deserialization in a way that's decoupled
    from the actual Spawn object's implementations or class definitions.

    Like the other classes in this file, this is probably overwrought and overengineered, but I kinda wanted to
    practice this idea here.
    """
    @classmethod
    def to_spawn(cls, character):
        raise MapLoaderException("SpawnLoader %s has unimplemented method to_spawn." % cls.__name__)

    @classmethod
    def from_spawn(cls, spawn):
        raise MapLoaderException("SpawnLoader %s has unimplemented method from_spawn." % cls.__name__)


class TextSpawnConverter(SpawnConverter):
    """
    This class defines the text <-> spawn object representation.  We just have a single map here, but we
    generically make it bidirectional directly below it.
    """
    TO = {
        'i': IndestructableWallSpawn,
        'p': PlayerSpawn,
        'd': DestructableWallSpawn,
        '_': None.__class__
    }

    FROM = {}
    for key in TO.keys():
        FROM[TO[key]] = key

    @classmethod
    def to_spawn(cls, character):
        if character not in cls.TO:
            raise MapLoaderException("Character %c is unrecognized and cannot be converted into spawn data." % character)
        return cls.TO[character]()

    @classmethod
    def from_spawn(cls, spawn):
        if spawn.__class__ not in cls.FROM:
            raise MapLoaderException("Class %s is unrecognized and cannot be converted into text data." % spawn.__class__)
        return cls.FROM[spawn.__class__]


class MapLoader(object):
    """
    Much like the ovewrought and overengineered SpawnConverter, the MapLoader is the ovewrought and overengineered
    base class for simply handling general map serialization and deserialization.
    """
    @classmethod
    def save_to_string(cls, map_obj):
        raise MapLoaderException("MapLoader class %s has unimplemented method save_to_string" % cls.__name__)

    @classmethod
    def save_to_file(cls, map_obj, file):
        to_save = cls.save_to_string(map_obj)
        with open(file, 'w') as f:
            f.write(to_save)

    @classmethod
    def load_from_string(cls, s):
        raise MapLoaderException("MapLoader class %s has unimplemented method load_from_string" % cls.__name__)

    @classmethod
    def load_from_file(cls, file):
        if not os.path.exists(file):
            raise MapLoaderException("Path %s does not exist." % file)
        if not os.path.isfile(file):
            raise MapLoaderException("%s is not a file." % file)
        with open(file, 'r') as f:
            return cls.load_from_string(f.read())


class JSONMapLoader(MapLoader, TextSpawnConverter):
    @classmethod
    def save_to_string(cls, map_obj):
        json_dict = {
            'name':map_obj.name,
            'dimensions': map_obj.dimensions,
            'grid': [[cls.from_spawn(space) for space in row] for row in map_obj.grid]
        }
        return json.dumps(json_dict)

    @classmethod
    def load_from_string(cls, s):
        s = s.strip()
        if not s:
            raise MapLoaderException("Unable to load string %s." % s)

        json_dict = json.loads(s)
        name = json_dict['name']
        dimensions = tuple(json_dict['dimensions'])
        to_return = Map(name=name, dimensions=dimensions)
        rows = json_dict['grid']

        for row_index in range(0, dimensions[1]):
            for col_index in range(0, dimensions[0]):
                character = rows[row_index][col_index]
                to_return.add_spawn(cls.to_spawn(character), (col_index, row_index))

        to_return.validate()
        return to_return


class Map(object):
    def __init__(self, name, dimensions):
        name = name.strip()
        if not name:
            raise MapLoaderException("Invalid map name: %s" % name)
        if not type(dimensions) == tuple or dimensions[0] <= 0 or dimensions[1] <= 0:
            raise MapLoaderException("Invalid map dimensions: %s - expecting tuple of two positive integers" % str(dimensions))

        self.dimensions = dimensions
        self.grid = [[None for _ in range(0, self.dimensions[0])] for _ in range(self.dimensions[1])]
        self.name = name

    def validate(self):
        # count number of player spawns
        # we need at least two otherwise there won't be a game to be had.
        player_spawns = 0
        for row in self.grid:
            for space in row:
                if isinstance(space, PlayerSpawn):
                    player_spawns += 1

        if player_spawns < 2:
            raise MapLoaderException("Map needs at least two player spawns.")

    def add_spawn(self, spawn, pos):
        col_index = pos[0]
        row_index = pos[1]
        if col_index < 0 or col_index >= self.dimensions[0] or row_index < 0 or row_index >= self.dimensions[1]:
            raise MapLoaderException("Spawn location %s must be within (0, 0) and %s." % (str(pos), str(self.dimensions)))

        self.grid[row_index][col_index] = spawn


class MapLoaderException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
