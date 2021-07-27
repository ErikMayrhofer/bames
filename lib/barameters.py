import argparse
import toml

def d(a, b):
    return a if a is not None else b

class Barameters:
    fullscreen: bool
    tag_size: int
    quick_start: bool
    camera_index: int

    def __init__(self):
        file_settings = toml.load("bame.toml")
        parser = argparse.ArgumentParser(description='BAME! (von den Machern von Bame)') 
        parser.add_argument('--fullscreen', dest="fullscreen", action='store_true')
        parser.add_argument('--no-splash', dest="no_splash", action='store_true')
        parser.add_argument('--tag-size', dest="tag_size")
        parser.add_argument('--camera', dest="camera_index")

        arg_settings = parser.parse_args()

        merged_settings = {**file_settings, **vars(arg_settings)}
        print("Merged Settings: ", merged_settings)

        self.fullscreen = d(merged_settings["fullscreen"], False)
        self.quick_start = d(merged_settings["no_splash"], False)
        self.tag_size = int(d(merged_settings["tag_size"], 192))
        self.camera_index = int(d(merged_settings["camera_index"], 0))

if __name__ == "__main__":
    barameters = Barameters()
