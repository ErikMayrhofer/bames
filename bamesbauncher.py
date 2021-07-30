from types import ModuleType
from lib.bame import Bame, BameMetadata
import apps

def aggregate_bames():
    pass

if __name__ == "__main__":
    print(dir(apps))
    bames = []
    for app in dir(apps):
        mod = getattr(apps, app)
        if isinstance(mod, ModuleType):
            for child in dir(mod):
                app_metadata = getattr(mod, child)
                if isinstance(app_metadata, BameMetadata):
                    bames.append(app_metadata)
    for b in bames:
        print("Found Bame: ", b)
    Bame(bames).run()
