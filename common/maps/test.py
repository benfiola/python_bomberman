import unittest
from . import *

class TestMap(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testOutOfBoundsSpawnAdd(self):
        map = Map((0, 0))
        map.add_spawn(PlayerSpawn)