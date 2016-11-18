import os
from .spawns import *


class MapLoader(object):
    @classmethod
    def generate_spawn(cls, data):
        raise MapLoaderException("MapLoader class %s has unimplemented method generate_spawn" % cls.__name__)

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


class TextMapLoader(MapLoader):
    @classmethod
    def generate_spawn(cls, char):
        if char == 'i':
            return IndestructableWallSpawn()
        if char == 'p':
            return PlayerSpawn()
        if char == 'd':
            return DestructableWallSpawn()
        if char == '_':
            return None
        raise MapLoaderException("%s could not convert spawn data %s." % (cls.__name__, str(data)))

    @classmethod
    def load_from_string(cls, s):
        if not s.strip():
            raise MapLoaderException("Unable to load string %s." % s)

        rows = s.strip().split("\n")

        # make sure board is uniform
        # we build an array of columns where we only add
        # non blank characters
        cols = []
        for row in rows:
            to_append = []
            for char in row:
                if char is not ' ':
                    to_append.append(char)
            cols.append(to_append)

        # then we get the expected length of each row
        col_length = len(rows)
        row_length = len(rows[0])

        # now we go through each column and ensure that
        # the column has col_length defined characters
        for x in range(0, len(cols)):
            col = cols[x]
            if len(col) != col_length:
                raise MapLoaderException("Column %d has length %d, expected length %d." % (x+1, len(col), col_length))

        # at this point, we just need to go through and build our map
        # and fill it with spawn locations
        to_return = Map((row_length, col_length))
        for x in range(0, len(rows)):
            row = rows[x]
            for y in range(0, len(row)):
                spawn_char = row[y]
                to_return.add_spawn(cls.generate_spawn(spawn_char), (x, y))

        to_return.validate()
        return to_return


class Map(object):
    def __init__(self, dimensions):
        self.grid = [[None for _ in range(0, dimensions[0])] for _ in range(dimensions[1])]
        self.dimensions = dimensions

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
        if pos[0] < 0 or pos[0] > self.dimensions[0] or pos[1] < 0 or pos[1] > self.dimensions[1]:
            raise MapLoaderException("Spawn location %s must be within (0, 0) and %s." % (str(pos), str(self.dimensions)))

        self.grid[pos[0]][pos[1]] = spawn


class MapLoaderException(Exception):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
