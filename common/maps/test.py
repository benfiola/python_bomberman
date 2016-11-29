import unittest
from . import *


class TestMap(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testOutOfBoundsSpawnAdd(self):
        map = Map(name="test", dimensions=(1, 1))
        with self.assertRaises(MapLoaderException):
            map.add_spawn(PlayerSpawn, (1, 1))

    def testLessThanTwoPlayersMap(self):
        map = Map(name="test", dimensions=(1, 1))
        map.add_spawn(PlayerSpawn(), (0, 0))
        with self.assertRaises(MapLoaderException):
            map.validate()

    def testNoNameMap(self):
        with self.assertRaises(MapLoaderException):
            Map(name=" ", dimensions=(1, 1))

    def testInvalidDimensionsMap(self):
        with self.assertRaises(MapLoaderException):
            Map(name="test", dimensions=(-1, 0))

    def testValidMap(self):
        name = "test"
        dimensions = (2, 3)
        player_one = PlayerSpawn()
        player_two = PlayerSpawn()
        map = Map(name=name, dimensions=dimensions)
        map.add_spawn(player_one, (0, 0))
        map.add_spawn(player_two, (1, 0))

        # this will do some checks that shouldn't throw an exception since this is a valid map.
        map.validate()

        # now let's confirm that everything is set correctly.
        self.assertEquals(map.name, name)
        self.assertEquals(map.dimensions, dimensions)
        self.assertEquals(len(map.grid), dimensions[1])
        self.assertEquals(len(map.grid[0]), dimensions[0])
        self.assertIsNone(map.grid[1][0])
        self.assertIsNone(map.grid[1][1])
        self.assertEquals(map.grid[0][0], player_one)
        self.assertEquals(map.grid[0][1], player_two)


class BaseMapLoaderTest(unittest.TestCase):
    def setUp(self):
        self.basic_map = Map(name="test", dimensions=(2, 3))
        self.basic_map.add_spawn(PlayerSpawn(), (0, 0))
        self.basic_map.add_spawn(IndestructableWallSpawn(), (0, 1))
        self.basic_map.add_spawn(DestructableWallSpawn(), (1, 0))
        self.basic_map.add_spawn(PlayerSpawn(), (1, 1))

    def tearDown(self):
        self.basic_map = None

    def saveAndLoad(self, map_loader_cls):
        map_str = map_loader_cls.save_to_string(self.basic_map)
        new_map = map_loader_cls.load_from_string(map_str)
        other_map_str = map_loader_cls.save_to_string(new_map)
        self.assertEquals(map_str, other_map_str)
        self.assertEquals(self.basic_map.name, new_map.name)
        self.assertEquals(self.basic_map.dimensions, new_map.dimensions)
        self.assertListEqual(self.basic_map.grid, new_map.grid)


class TestJsonMapLoader(BaseMapLoaderTest):
    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def testSaveAndLoad(self):
        super().saveAndLoad(JSONMapLoader)
