from lib.bame import Bame, BameMetadata
import apps

def aggregate_bames():
    pass

if __name__ == "__main__":
    bames = [getattr(apps, app) for app in dir(apps) if isinstance(getattr(apps, app), BameMetadata)]
    Bame(bames).run()
