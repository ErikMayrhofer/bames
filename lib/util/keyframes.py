from typing import List, Tuple

class Keyframes:
    """
    Create smooth Animation-Timelines.
    Supply the timeline in the constructor. This should be an array of absolute time-stamps and values.

    Step forwards through the animation with the advance method and then get the value using the value function.

    Example::
        

    Init Method:
        self.frames = Keyframes([(0, 0), (0.5, 255), (1, 255), (1.5, 0)])

    Tick Method:
        self.frames.advance(delta_ms/1000)
        val = self.frames.value()
    """
    
    def __init__(self, frames: List[Tuple[float, float]]):
        """
        Supply an array of keyframes.
        [(timestamp, value), (timestamp, value)]
        These have to be ordered.

        Move 
        """
        self.frames = frames
        self.time = 0
        self.index = 0
        pass

    def advance(self, time: float):
        """
        Step forward through time.

        (Negative time values are currently not supported)
        """
        self.time += time 
        for i in reversed(range(self.index, len(self.frames))):
            if self.frames[i][0] < self.time:
                self.index = i
                break

    def done(self) -> bool:
        return self.index == len(self.frames) - 1

    def value(self):
        """
        Get the current value of the Animation.

        O(N)=1
        """
        if self.done():
            return self.frames[self.index][1]

        fr = self.frames[self.index]
        to = self.frames[self.index+1]

        offset = self.time - fr[0]
        duration = to[0] - fr[0]
        ran = to[1] - fr[1]

        perc = offset / duration

        return ran*perc + fr[1]
        
