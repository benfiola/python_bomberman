from common.logging import get_logger
from common.maps.spawns import *
from common.entities import *

class Game(object):
    def __init__(self, configuration):
        self.logger = get_logger(self)
        self.logger.info("Creating game")
        self.configuration = configuration
        self.map = self.configuration.map
        self.unassigned_player_entities = []
        self.player_entities = {}
        self.board = [[self.spawn_to_entity(self.map.spawns[x][y]) for y in range(self.map.dimensions[1])] for x in range(self.map.dimensions[0])]

    def spawn_to_entity(self, spawn):
        if isinstance(spawn, PlayerSpawn):
            player = PlayerEntity(spawn.position)
            self.unassigned_player_entities.append(player)
            return player
        if isinstance(spawn, IndestructibleWallSpawn):
            return IndestructibleWallEntity(spawn.position)
        if isinstance(spawn, DestructibleWallSpawn):
            return DestructibleWallEntity(spawn.position)

    def assign_player_to_client(self, client_id):
        player_entity = self.unassigned_player_entities.pop()
        self.logger.debug("Assigning client %s to player entity %s" % (str(client_id), str(player_entity.id)))
        self.player_entities[client_id] = player_entity

