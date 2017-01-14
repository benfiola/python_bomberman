from client.controllers import *
import client.graphics.views.single_player_options as view
import common.configuration.game_configuration as game_configuration
import common.maps as maps

class SinglePlayerOptionsController(Controller):
    def __init__(self, client):
        super().__init__(client, view.SinglePlayerOptionsView)

    def set_up(self):
        entities.ClientEntity(self, view_qualifier="background")
        entities.ClientEntity(self, view_qualifier="title")

    def on_key_down(self, key_code):
        if key_code == events.KeyInputEvent.ESC:
            from client.controllers.main_menu import MainMenuController
            self.client.add_event(events.ControllerTransition(MainMenuController))
        if key_code == events.KeyInputEvent.RETURN:
            local_host_data = entities.HostData(True)
            remote_host_data = entities.HostData(False, ("", 40000))
            map = maps.Map("test", (3, 3))
            map.add_spawn(maps.PlayerSpawn(), (1, 1))
            map.add_spawn(maps.DestructableWallSpawn(), (0, 0))
            map.add_spawn(maps.DestructableWallSpawn(), (2, 2))
            map.add_spawn(maps.IndestructableWallSpawn(), (0, 2))
            map.add_spawn(maps.IndestructableWallSpawn(), (2, 0))
            game_config = game_configuration.GameConfiguration(
                map, 1, 0
            )
            self.client.add_event(events.CreateHost(local_host_data))
            self.client.add_event(events.StartMessageBus(local_host_data))
            self.client.add_event(events.SendRequest(messages.CreateGame(self.client.uuid, game_config)))
            from client.controllers.single_player import SinglePlayerController
            self.client.add_event(events.ControllerTransition(SinglePlayerController))

