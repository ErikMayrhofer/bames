from typing import Dict, List
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

MAPS = {
        # "Wireless Steam Controller": {
        "03000000de2800004211000011010000": {
            0: TOUCH_LEFT,
            1: TOUCH_RIGHT,
            2: BUTTON_SYMBOL_BOTTOM,
            3: BUTTON_SYMBOL_LEFT,
            4: BUTTON_SYMBOL_RIGHT,
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
        # "Xbox One S Controller": {
        "050000005e040000e002000003090000": {
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
        # "DragonRise Inc. Generic USB Joystick": {
        "03000000790000000600000010010000": {
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
        }
    }

class JoystickMetadata:
    def __init__(self, joystick: Joystick) -> None:
        self.joystick = joystick
        pass

    def map_button(self, raw_button: int):
        # print("MAP BUTTON ", self.joystick.get_name(), raw_button)

        name = self.joystick.get_guid()
        
        if name in MAPS:
            map = MAPS[name]
            if raw_button in map:
                return map[raw_button]
            else:
                # raise Exception(f"Gamepad '{name}' pressed button <{raw_button}> which is not yet present in the MAPS in bamepad.py")
                print(f"Gamepad '{name}' pressed button <{raw_button}> which is not yet present in the MAPS in bamepad.py")
        else:
            # raise Exception(f"Unknown Gamepad '{name}' is not yet present in the MAPS in bamepad.py")
            print(f"Unknown Gamepad '{name}' is not yet present in the MAPS in bamepad.py")

    def map_axes(self, raw_axes: int):
        name = self.joystick.get_guid()
        if name in MAPS:
            map = MAPS[name]
            if raw_axes in map:
                return map[raw_axes]
            else:
                # raise Exception(f"Gamepad '{name}' pressed button <{raw_button}> which is not yet present in the MAPS in bamepad.py")
                print(f"Gamepad '{name}' pressed button <{raw_axes}> which is not yet present in the MAPS in bamepad.py")
        else:
            # raise Exception(f"Unknown Gamepad '{name}' is not yet present in the MAPS in bamepad.py")
            print(f"Unknown Gamepad '{name}' is not yet present in the MAPS in bamepad.py")


class BamePadManager:
    joysticks: List[JoystickMetadata]
    def __init__(self, joysticks: List[JoystickMetadata]) -> None:
        self.joysticks = joysticks
        pass


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
    def __init__(self) -> None:
        self.joysticks = {}
        for x in range (js.get_count()):
            joystick = JoystickFactoryParcel(x)
            self.joysticks[joystick.metadata.joystick.get_instance_id()] = joystick


    def build(self) -> BamePadManager:
        return BamePadManager([x.build() for x in self.joysticks.values() if x.should_be_built()])

    def handle_press(self, joystick_instance_id, button_index):
        joystick = self.joysticks[joystick_instance_id]

        mapped_button = joystick.metadata.map_button(button_index)

        print("PRess: ", mapped_button)

        if mapped_button == BUTTON_SYMBOL_BOTTOM:
            if joystick.active:
                joystick.ready = True
            joystick.active = True
        if mapped_button == BUTTON_SYMBOL_RIGHT:
            joystick.active = False
            joystick.ready = False

    def get_active_controllers(self) -> List[JoystickFactoryParcel]:
        return [x for x in self.joysticks.values() if x.active]


