from common.logging import get_logger
from common.maps.spawns import *
from common.entities import *
from host.custom_events import *
from common.messaging import messages
import time

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
        self.board = [[[] for y in range(self.map.dimensions[1])] for x in range(self.map.dimensions[0])]
        for x in range(len(self.board)):
            for y in range(len(self.board[x])):
                entity = self.spawn_to_entity(self.map.spawns[x][y])
                if entity is not None:
                    self.board[x][y].append(entity)

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

    def drop_bomb(self, client_id):
        entity = self.player_entities[client_id]
        pos = entity.position
        bomb = BombEntity(pos)
        self.board[pos[0]][pos[1]].append(bomb)
        update_data = dict()
        update_data["entity_add"] = [bomb]
        self.host.push_custom_event(SendMessage(messages.ClientGameDataUpdate(update_data)))

    def move_entity(self, client_id, direction):
        entity = self.player_entities[client_id]
        pos = entity.position
        new_pos = (pos[0] + direction[0], pos[1] + direction[1])
        if new_pos[0] >= 0 and new_pos[0] < len(self.board) and new_pos[1] >= 0 and new_pos[1] < len(
                self.board[pos[0]]) and len(self.board[new_pos[0]][new_pos[1]]) == 0:
            entity.position = new_pos
            self.board[pos[0]][pos[1]].remove(entity)
            self.board[new_pos[0]][new_pos[1]].append(entity)
            update_data = dict()
            update_data["entity_move"] = (pos, new_pos)
            self.host.push_custom_event(SendMessage(messages.ClientGameDataUpdate(update_data)))

    def start_game(self):
        self.game_started = True
        self.host.push_custom_event(SendMessage(messages.ClientGameDataRequest(self.board)))

    def detonate_bomb(self, bomb, update_data):
        bomb_pos = bomb.position

        entity_list = self.board[bomb_pos[0]][bomb_pos[1]]
        for entity in entity_list:
            if "entity_remove" not in update_data:
                update_data["entity_remove"] = []
                update_data["entity_remove"].append(entity)
                entity_list.remove(entity)
        fire = FireEntity(bomb_pos)
        entity_list.append(fire)
        if "entity_add" not in update_data:
            update_data["entity_add"] = []
        update_data["entity_add"].append(fire)

        # left
        stop_here = False
        for x in range(bomb_pos[0] - 1, bomb_pos[0] - BombEntity.RADIUS, -1):
            pos = (x, bomb_pos[1])
            if pos[0] < 0 or pos[0] >= len(self.board) or pos[1] < 0 or pos[1] >= len(self.board[pos[0]]):
                stop_here = True
            if stop_here:
                break
            entity_list = self.board[pos[0]][pos[1]]
            need_fire = True
            for entity in list(entity_list):
                if not isinstance(entity, IndestructibleWallEntity):
                    if "entity_remove" not in update_data:
                        update_data["entity_remove"] = []
                    update_data["entity_remove"].append(entity)
                    entity_list.remove(entity)
                else:
                    need_fire = False
                if isinstance(entity, IndestructibleWallEntity) or isinstance(entity, DestructibleWallEntity):
                    stop_here = True
                    break
            if need_fire:
                fire = FireEntity(pos)
                entity_list.append(fire)
                if "entity_add" not in update_data:
                    update_data["entity_add"] = []
                update_data["entity_add"].append(fire)

        # right
        stop_here = False
        for x in range(bomb_pos[0] + 1, bomb_pos[0] + BombEntity.RADIUS, 1):
            pos = (x, bomb_pos[1])
            if pos[0] < 0 or pos[0] >= len(self.board) or pos[1] < 0 or pos[1] >= len(self.board[pos[0]]):
                stop_here = True
            if stop_here:
                break
            entity_list = self.board[pos[0]][pos[1]]
            need_fire = True
            for entity in list(entity_list):
                if not isinstance(entity, IndestructibleWallEntity):
                    if "entity_remove" not in update_data:
                        update_data["entity_remove"] = []
                    update_data["entity_remove"].append(entity)
                    entity_list.remove(entity)
                else:
                    need_fire = False
                if isinstance(entity, IndestructibleWallEntity) or isinstance(entity, DestructibleWallEntity):
                    stop_here = True
                    break
            if need_fire:
                fire = FireEntity(pos)
                entity_list.append(fire)
                if "entity_add" not in update_data:
                    update_data["entity_add"] = []
                update_data["entity_add"].append(fire)

        # up
        stop_here = False
        for y in range(bomb_pos[1] - 1, bomb_pos[1] - BombEntity.RADIUS, -1):
            pos = (bomb_pos[0], y)
            if pos[0] < 0 or pos[0] >= len(self.board) or pos[1] < 0 or pos[1] >= len(self.board[pos[0]]):
                stop_here = True
            if stop_here:
                break
            entity_list = self.board[pos[0]][pos[1]]
            need_fire = True
            for entity in list(entity_list):
                if not isinstance(entity, IndestructibleWallEntity):
                    if "entity_remove" not in update_data:
                        update_data["entity_remove"] = []
                    update_data["entity_remove"].append(entity)
                    entity_list.remove(entity)
                else:
                    need_fire = False
                if isinstance(entity, IndestructibleWallEntity) or isinstance(entity, DestructibleWallEntity):
                    stop_here = True
                    break
            if need_fire:
                fire = FireEntity(pos)
                entity_list.append(fire)
                if "entity_add" not in update_data:
                    update_data["entity_add"] = []
                update_data["entity_add"].append(fire)

        # down
        stop_here = False
        for y in range(bomb_pos[1] + 1, bomb_pos[1] + BombEntity.RADIUS, 1):
            pos = (bomb_pos[0], y)
            if pos[0] < 0 or pos[0] >= len(self.board) or pos[1] < 0 or pos[1] >= len(self.board[pos[0]]):
                stop_here = True
            if stop_here:
                break
            entity_list = self.board[pos[0]][pos[1]]
            need_fire = True
            for entity in list(entity_list):
                if not isinstance(entity, IndestructibleWallEntity):
                    if "entity_remove" not in update_data:
                        update_data["entity_remove"] = []
                    update_data["entity_remove"].append(entity)
                    entity_list.remove(entity)
                else:
                    need_fire = False
                if isinstance(entity, IndestructibleWallEntity) or isinstance(entity, DestructibleWallEntity):
                    stop_here = True
                    break
            if need_fire:
                fire = FireEntity(pos)
                entity_list.append(fire)
                if "entity_add" not in update_data:
                    update_data["entity_add"] = []
                update_data["entity_add"].append(fire)

        return update_data

    def remove_fire(self, entity, update_data):
        pos = entity.position
        entity_list = self.board[pos[0]][pos[1]]
        entity_list.remove(entity)
        if "entity_remove" not in update_data:
            update_data["entity_remove"] = []
        update_data["entity_remove"].append(entity)

    def update_game(self):
        curr_time = time.time()
        update_data = dict()
        for row in self.board:
            for entity_list in row:
                for entity in list(entity_list):
                    if isinstance(entity, FireEntity):
                        if curr_time - entity.time_placed >= entity.DURATION:
                            self.remove_fire(entity, update_data)
                    if isinstance(entity, BombEntity):
                        if curr_time - entity.time_placed >= entity.DURATION:
                            self.detonate_bomb(entity, update_data)
        if len(list(update_data.keys())) > 0:
            self.host.push_custom_event(SendMessage(messages.ClientGameDataUpdate(update_data)))


