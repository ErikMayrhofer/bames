from typing import Dict, List, Set
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

    def __map(self, type, raw):
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


class BamePadManager:
    joysticks: Dict[int, JoystickMetadata]
    def __init__(self, joysticks: List[JoystickMetadata]) -> None:
        self.joysticks = {}
        for stick in joysticks:
            self.joysticks[stick.joystick.get_instance_id()] = stick
    
        pass

    def map_event(self, event: Event):
        if event.type == pygame.JOYBUTTONUP or event.type == pygame.JOYBUTTONDOWN:
            joystick = self.joysticks[event.instance_id]
            event.button = joystick.map_button(event.button)
            event.player = joystick.player_num
            if event.button is WEIRD_DISABLED_SHIT: 
                return None
        if event.type == pygame.JOYAXISMOTION:
            joystick = self.joysticks[event.instance_id]
            event.axis = joystick.map_axes(event.axis)
            event.player = joystick.player_num
            if event.axis is WEIRD_DISABLED_SHIT: 
                return None
        if event.type == pygame.JOYHATMOTION:
            joystick = self.joysticks[event.instance_id]
            event.hat = joystick.map_hat(event.hat)
            event.player = joystick.player_num
            if event.hat is WEIRD_DISABLED_SHIT: 
                return None

        return event


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
    def __init__(self) -> None:
        self.joysticks = {}
        self.player_nums = set() 
        for x in range (js.get_count()):
            joystick = JoystickFactoryParcel(x)
            self.joysticks[joystick.metadata.joystick.get_instance_id()] = joystick


    def build(self) -> BamePadManager:
        for x in self.joysticks.values():
            if not x.active:
                x.metadata.joystick.quit()
        return BamePadManager([x.build() for x in self.joysticks.values() if x.should_be_built()])

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
        if mapped_button == BUTTON_SYMBOL_RIGHT:
            joystick.active = False
            joystick.ready = False
            self.player_nums.discard(joystick.metadata.player_num)
            joystick.metadata.player_num = -1

    def get_free_num(self) -> int:
        for x in range(1, 20): # <- cap
            if x not in self.player_nums:
                return x
        raise Exception("Too many players :(... Just raise the cap in bamepad.py")

    def get_active_controllers(self) -> List[JoystickFactoryParcel]:
        return [x for x in self.joysticks.values() if x.active]


