from common.logging import get_logger
from common.maps.spawns import *
from common.entities import *
from host.custom_events import *
from common.messaging import messages


class Game(object):
    def __init__(self, host, configuration):
        self.logger = get_logger(self)
        self.logger.info("Creating game")
        self.configuration = configuration
        self.host = host
        self.map = self.configuration.map
        self.game_started = False
        self.unassigned_player_entities = []
        self.player_entities = {}
        self.board = [[self.spawn_to_entity(self.map.spawns[x][y]) for y in range(self.map.dimensions[1])] for x in
                      range(self.map.dimensions[0])]

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

    def move_entity(self, client_id, direction):
        entity = self.player_entities[client_id]
        pos = entity.position
        self.logger.info("Curr position: %s" % str(pos))
        self.logger.info("Direction: %s" % str(direction))
        new_pos = (pos[0] + direction[0], pos[1] + direction[1])
        if new_pos[0] >= 0 and new_pos[0] < len(self.board) and new_pos[1] >= 0 and new_pos[1] < len(
                self.board[pos[0]]) and self.board[new_pos[0]][new_pos[1]] is None:
            entity.position = new_pos
            self.board[pos[0]][pos[1]] = None
            self.board[new_pos[0]][new_pos[1]] = entity
            self.logger.info("New position: %s" % str(new_pos))
            update_data = dict()
            update_data[pos] = self.board[pos[0]][pos[1]]
            update_data[new_pos] = self.board[new_pos[0]][new_pos[1]]
            self.host.push_custom_event(SendMessage(messages.ClientGameDataUpdate(update_data)))

    def start_game(self):
        self.game_started = True
        self.host.push_custom_event(SendMessage(messages.ClientGameDataRequest(self.board)))