from typing import List
from lib.bamepad import BamePadManager
from lib.barameters import Barameters

class Action:
    name: str

class BeymapRegistrar:
    actions: List[Action]
    def __init__(self) -> None:
        self.actions = []
        pass

    def add_action(self, name):
        act = Action()
        act.name = name

        self.actions.append(act)

class BeymapManager:
    def __init__(self, bamepad: BamePadManager, _: Barameters) -> None:
        pass

    def action(self, name):
        return False
