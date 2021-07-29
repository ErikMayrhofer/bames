from lib.barameters import Barameters
from lib import beymap
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import pygame
from pygame.event import Event
from pygame.joystick import Joystick
import pygame.joystick as js

BUTTON_SYMBOL_BOTTOM = "BLETTER_BOTTOM"
BUTTON_SYMBOL_TOP = "BLETTER_TOP"
BUTTON_SYMBOL_LEFT = "BLETTER_LEFT"
BUTTON_SYMBOL_RIGHT = "BLETTER_RIGHT"
BUTTON_A = BUTTON_SYMBOL_BOTTOM
BUTTON_B = BUTTON_SYMBOL_RIGHT
BUTTON_X = BUTTON_SYMBOL_LEFT
BUTTON_Y = BUTTON_SYMBOL_TOP

TRIGGER_LEFT="TRIGGER_LEFT"
TRIGGER_RIGHT="TRIGGER_RIGHT"
SHOULDER_RIGHT="SHOULDER_RIGHT"
SHOULDER_LEFT="SHOULDER_LEFT"

MENU_RIGHT="MENU_RIGHT"
MENU_LEFT="MENU_LEFT"
VENDOR_BUTTON="VENDOR_BUTTON"

LEFT_AXES_PRESS="LEFT_AXES_PRESS"
RIGHT_AXES_PRESS="RIGHT_AXES_PRESS"

BEHIND_RIGHT="BEHIND_RIGHT"
BEHIND_LEFT="BEHIND_LEFT"

TOUCH_LEFT="TOUCH_LEFT"
TOUCH_RIGHT="TOUCH_RIGHT"


AXIS_RIGHT_VERTICAL="AXIS_RIGHT_VERTICAL"
AXIS_LEFT_VERTICAL="AXIS_LEFT_VERTICAL"
AXIS_RIGHT_HORIZONTAL="AXIS_RIGHT_HORIZONTAL"
AXIS_LEFT_HORIZONTAL="AXIS_LEFT_HORIZONTAL"
AXIS_LEFT_TRIGGER="AXIS_LEFT_TRIGGER"
AXIS_RIGHT_TRIGGER="AXIS_RIGHT_TRIGGER"

LEFT_HAT="LEFT_HAT"

WEIRD_DISABLED_SHIT="WEIRD!!!"


MAPS = {
        # "Wireless Steam Controller": {
        "03000000de2800004211000011010000": {
            "BUTTONS": {
                
            0: TOUCH_LEFT,
            1: TOUCH_RIGHT,
            2: BUTTON_SYMBOL_BOTTOM,
            3: BUTTON_SYMBOL_RIGHT,
            4: BUTTON_SYMBOL_LEFT,
            5: BUTTON_SYMBOL_TOP,
            6: SHOULDER_LEFT,
            7: SHOULDER_RIGHT,
            8: TRIGGER_LEFT,
            9: TRIGGER_RIGHT,
            10: MENU_LEFT,
            11: MENU_RIGHT,
            12: VENDOR_BUTTON,
            13: LEFT_AXES_PRESS,
            14: RIGHT_AXES_PRESS,
            15: BEHIND_LEFT,
            16: BEHIND_RIGHT
                },
            "AXES": {

                0: AXIS_LEFT_HORIZONTAL,
                1: AXIS_LEFT_VERTICAL,
                2: AXIS_RIGHT_HORIZONTAL,
                3: AXIS_RIGHT_VERTICAL,
                },
            "HATS": {
                0: LEFT_HAT
                }
        },
        # "Xbox One S Controller": {
        "050000005e040000e002000003090000": {
            "BUTTONS": {

            0: BUTTON_SYMBOL_BOTTOM,
            1: BUTTON_SYMBOL_RIGHT,
            2: BUTTON_SYMBOL_LEFT,
            3: BUTTON_SYMBOL_TOP,
            4: SHOULDER_LEFT,
            5: SHOULDER_RIGHT,
            6: MENU_LEFT,
            7: MENU_RIGHT,
            8: LEFT_AXES_PRESS,
            9: RIGHT_AXES_PRESS,
            10: VENDOR_BUTTON
                },

            "AXES": {

                0: AXIS_LEFT_HORIZONTAL,
                1: AXIS_LEFT_VERTICAL,
                2: AXIS_LEFT_TRIGGER,
                3: AXIS_RIGHT_HORIZONTAL,
                4: AXIS_RIGHT_VERTICAL,
                5: AXIS_RIGHT_TRIGGER,
                },

            "HATS": {
                0: LEFT_HAT
                }
        },
        # "DragonRise Inc. Generic USB Joystick": {
        "03000000790000000600000010010000": {
            "BUTTONS": {
            0: BUTTON_SYMBOL_TOP,
            1: BUTTON_SYMBOL_RIGHT,
            2: BUTTON_SYMBOL_BOTTOM,
            3: BUTTON_SYMBOL_LEFT,
            4: TRIGGER_LEFT,
            5: TRIGGER_RIGHT,
            6: SHOULDER_LEFT,
            7: SHOULDER_RIGHT,
            8: MENU_LEFT,
            9: MENU_RIGHT,
            10: LEFT_AXES_PRESS,
            11: RIGHT_AXES_PRESS
            },
            "AXES": {
                0: AXIS_LEFT_HORIZONTAL,
                1: AXIS_LEFT_VERTICAL,
                2: WEIRD_DISABLED_SHIT,
                3: AXIS_RIGHT_HORIZONTAL,
                4: AXIS_RIGHT_VERTICAL
                },

            "HATS": {
                0: LEFT_HAT
                }
        }
    }

class JoystickMetadata:
    def __init__(self, joystick: Joystick) -> None:
        self.joystick = joystick
        self.player_num = 0
        pass

    def map_button(self, raw_button: int):
        return self.__map("BUTTONS", raw_button)

    def map_axes(self, raw_axes: int):
        return self.__map("AXES", raw_axes)

    def map_hat(self, raw_hat: int):
        return self.__map("HATS", raw_hat)

    def __map(self, type, raw) -> str:
        name = self.joystick.get_guid()
        if name in MAPS:
            map = MAPS[name][type]
            if raw in map:
                return map[raw]
            else:
                # raise Exception(f"Gamepad '{name}' pressed button <{raw_button}> which is not yet present in the MAPS in bamepad.py")
                print(f"Gamepad '{name}' moved {type} <{raw}> which is not yet present in the MAPS in bamepad.py")
        else:
            # raise Exception(f"Unknown Gamepad '{name}' is not yet present in the MAPS in bamepad.py")
            print(f"Unknown Gamepad '{name}' is not yet present in the MAPS in bamepad.py")
        return WEIRD_DISABLED_SHIT

    def __reverse_map(self, type, control) -> Optional[Tuple[str, int]]:
        name = self.joystick.get_guid()
        if name in MAPS:
            for type, map in MAPS[name].items():
                for raw, name in map.items():
                    if name == control:
                        return (type, raw)
        else:
            # raise Exception(f"Unknown Gamepad '{name}' is not yet present in the MAPS in bamepad.py")
            print(f"Unknown Gamepad '{name}' is not yet present in the MAPS in bamepad.py")
        return None

    def __f_reverse_map(self, type, control) -> Tuple[str, int]:
        r = self.__reverse_map(type, control)
        if r is None:
            raise Exception(f"Could not reverse map {control} for controller {self.joystick.get_name()}")
        return r

    # def get_button(self, control) -> bool:
        # return self.joystick.get_button(self.__f_reverse_map("BUTTONS", control))
# 
    # def get_axis(self, control) -> float:
        # return self.joystick.get_axis(self.__f_reverse_map("AXES", control))
# 
    # def get_hat(self, control) -> Tuple[float, float]:
        # return self.joystick.get_hat(self.__f_reverse_map("HATS", control))
 
    def get_control(self, control) -> Union[Tuple[float, float], bool, float]:
        (type, raw) = self.__f_reverse_map("HATS", control)
        if type == "HATS":
            return self.joystick.get_hat(raw)
        if type == "BUTTONS":
            return self.joystick.get_button(raw)
        if type == "AXES":
            return self.joystick.get_axis(raw)
        raise Exception(f"Unknown type returned for control reverse mapping: {control} -> {type}, {raw} on controller {self.joystick.get_name()}")

class Bvent:
    action: Optional[str]
    def __init__(self, *, type: int, control_name: str, player: int, value: Any) -> None:
        self.control_name = control_name
        self.player = player
        self.value = value
        self.type = type
        self.action = None

    def __str__(self) -> str:
        return f"<Bvent({self.type} : {self.control_name}({self.action}) player={self.player}, value={self.value})>"


MAPPABLE_EVENTS = {
        pygame.JOYBUTTONDOWN,
        pygame.JOYBUTTONUP,
        pygame.JOYHATMOTION,
        pygame.JOYAXISMOTION
        }

class BamePadManager:
    joysticks: Dict[int, JoystickMetadata]
    def __init__(self, joysticks: List[JoystickMetadata]) -> None:
        self.joysticks = {}
        for stick in joysticks:
            self.joysticks[stick.joystick.get_instance_id()] = stick
    
        pass

    def map_event(self, event: Event) -> Optional[Union[Event, Bvent]]:
        if event.type in MAPPABLE_EVENTS:
            print("Mappable Events ", event)
            joystick = self.joysticks[event.instance_id]
            (value, control_name) = self.__extract_mapped_control_from_event(joystick, event)
            player = joystick.player_num
            if control_name is WEIRD_DISABLED_SHIT: 
                return None
            return Bvent(
                    control_name=control_name,
                    value=value,
                    player=player,
                    type=event.type)
        return event

    def of_player(self, player_num) -> Optional[JoystickMetadata]:
        for stick in self.joysticks.values():
            if stick.player_num == player_num:
                return stick
        return None


    def __extract_mapped_control_from_event(self, joystick: JoystickMetadata, event: Event) -> Tuple[Any, str]:
        if event.type == pygame.JOYBUTTONUP:
            return (False, joystick.map_button(event.button))
        if event.type == pygame.JOYBUTTONDOWN:
            return (True, joystick.map_button(event.button))
        if event.type == pygame.JOYAXISMOTION:
            return (event.value, joystick.map_axes(event.axis))
        if event.type == pygame.JOYHATMOTION:
            print("Hat: ", event)
            return (event.value, joystick.map_hat(event.hat))
        raise Exception("Unsupported event type: ", event.type)


class JoystickFactoryParcel:
    def __init__(self, joystick_index) -> None:
        self.metadata = JoystickMetadata(Joystick(joystick_index))
        self.active = False
        self.ready = False
        pass

    def build(self):
        return self.metadata

    def should_be_built(self):
        return self.active
    
class BamePadFactory:
    joysticks: Dict[int, JoystickFactoryParcel]
    player_nums: Set[int]
    def __init__(self, beymapregistrar: 'BeymapRegistrar') -> None:
        self.beymapregistrar = beymapregistrar
        self.joysticks = {}
        self.player_nums = set() 
        for x in range (js.get_count()):
            joystick = JoystickFactoryParcel(x)
            self.joysticks[joystick.metadata.joystick.get_instance_id()] = joystick


    def build(self, barameters: Barameters) -> Tuple[BamePadManager, 'BeymapManager']:
        for x in self.joysticks.values():
            if not x.active:
                x.metadata.joystick.quit()

        beymap = BamePadManager([x.build() for x in self.joysticks.values() if x.should_be_built()])
        return (
                beymap,
                self.beymapregistrar.build(beymap, barameters)
               )

    def handle_press(self, joystick_instance_id, button_index):
        joystick = self.joysticks[joystick_instance_id]

        mapped_button = joystick.metadata.map_button(button_index)

        if mapped_button == BUTTON_SYMBOL_BOTTOM:
            if joystick.active:
                joystick.ready = True
            else:
                joystick.active = True
                joystick.metadata.player_num = self.get_free_num()
                self.player_nums.add(joystick.metadata.player_num)
                self.beymapregistrar.add_player(joystick.metadata.player_num)
        if mapped_button == BUTTON_SYMBOL_RIGHT:
            joystick.active = False
            joystick.ready = False
            self.player_nums.discard(joystick.metadata.player_num)
            joystick.metadata.player_num = -1
            self.beymapregistrar.remove_player(joystick.metadata.player_num)

    def get_free_num(self) -> int:
        for x in range(1, 20): # <- cap
            if x not in self.player_nums:
                return x
        raise Exception("Too many players :(... Just raise the cap in bamepad.py")

    def get_active_controllers(self) -> List[JoystickFactoryParcel]:
        return [x for x in self.joysticks.values() if x.active]


