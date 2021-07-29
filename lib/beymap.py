from typing import Any, Dict, List, Optional, Union
import pygame
from lib.bamepad import BamePadManager, Bvent
from lib.barameters import Barameters
from pygame.event import Event

class Action:
    name: str
    default: str

class PlayerBeyMapping:
    __action_to_control: Dict[str, str]
    __control_to_action: Dict[str, str]
    def __init__(self, action_to_control: Dict[str, str]) -> None:
        self.__action_to_control = action_to_control
        self.__control_to_action = {value: key for (key, value) in action_to_control.items() }

    def action_for_control(self, control: str) -> Optional[str]:
        if control in self.__control_to_action:
            return self.__control_to_action[control]
        return None

    def control_for_action(self, action: str) -> Optional[str]:
        if action in self.__action_to_control:
            return self.__action_to_control[action]
        return None

class BeymapManager:

    map: Dict[int,PlayerBeyMapping]

    def __init__(self, map: Dict[int, Dict[str, str]], bamepad: BamePadManager, _: Barameters) -> None:
        print("BeymapManager: ", map)
        self.bamepad = bamepad
        self.map = {playernum: PlayerBeyMapping(mapping) for (playernum, mapping) in map.items()}

    def action(self, name) -> Dict[int, Any]:
        return { stick.player_num: stick.get_control(self.map[stick.player_num].control_for_action(name)) for stick in self.bamepad.joysticks.values()}

    def player_action(self, player, name) -> Any:
        stick = self.bamepad.of_player(player)
        if stick is None:
            raise Exception(f"Tried to get action for Player #{player} but no Bamepad was found for it.")
        stick.get_control(self.map[player].control_for_action(name))

    def map_event(self, event: Union[Event, Bvent]) -> Union[Event, Bvent]:
        if isinstance(event, Bvent):
            if event.player in self.map:
                action = self.map[event.player].action_for_control(event.control_name)
                event.action = action
                return event
            else:
                raise Exception(f"Got event from player {event.player} which does not have an action-map.")

        return event 

class BeymapRegistrar:
    actions: List[Action]
    player_mappings: Dict[int, Dict[str, str]]
    def __init__(self) -> None:
        self.actions = []
        self.player_mappings = {}
        pass

    def add_action(self, name, default):
        act = Action()
        act.name = name
        act.default = default

        self.actions.append(act)

    def add_player(self, player_num):
        self.player_mappings[player_num] = { a.name: a.default for a in self.actions }

    def remove_player(self, player_num):
        self.player_mappings.pop(player_num)

    def build(self, bamepad: BamePadManager, barameters: Barameters) -> BeymapManager:
        print("Player Mappings: ", self.player_mappings)
        return BeymapManager(self.player_mappings, bamepad, barameters)
