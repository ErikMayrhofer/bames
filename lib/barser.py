from multiprocessing import Process, Pipe, connection
from typing import Optional
from lib.bicturetaker import Bicturetaker
import time

class WorkerPayload:
    """
    The actual payload which is sent from the barser to the main Bame Thread.

    This is created inside of "barser_worker(...)"

    Fields:
        image: Undistorted image
        raw_image: Raw image from the camera
        barsed_info (dict): Result which was generated from the Barsers - containing information about the game field.
    """
    def __init__(self, raw_image, image, barsed_info):
        self.raw_image = raw_image
        self.image = image
        self.barsed_info = barsed_info

def barser_worker(pipe_connection: connection.Connection):
    """
    Worker method which runs in a seperate process. This creates the `WorkerBayload` and sends it to the `Barser`

    Workflow:
        Bicturetaker takes and processes image 
          |
          V
        Barsers are run and create the game field which will be stored in barsed_info
          |
          V
        WorkerBayload is constructed and sent over the pipe
    """
    running = True

    taker = Bicturetaker()

    while running:
        if pipe_connection.poll(0):
            res = pipe_connection.recv()
            if res:
                running = False

        if running:
            d = taker.take_bicture()
            pipe_connection.send(WorkerPayload(raw_image=d["raw"], image=d["img"]))

    print("Barser Worker shut down.")



class WorkerHandle:
    """
    Unified access to the worker process.
    """
    def __init__(self, pipe_connection: connection.Connection, process: Process):
        self.pipe_connection = pipe_connection
        self.process = process

    def stop(self):
        print("Stopping worker")
        self.pipe_connection.send(True)
        self.process.join(3)
        if self.process.is_alive():
            print("Needing to terminate the process??")
            self.process.terminate()
        self.process.close()


class Barser:
    """
    Utility class to spawn a seperate process which then runs the bicture-taking and barsing
    """

    handle: Optional[WorkerHandle]
    last_barsed: Optional[WorkerPayload]
    last_barsed_time: Optional[float]
    def __init__(self):
        self.handle = None
        self.last_barsed = None
        self.last_barsed_time = None
        pass

    def launch(self):
        """
        Actually launches the thread. Do not forget to call stop() at the end.
        """
        pipe_connection, child_pipe = Pipe()
        process = Process(target=barser_worker, args=(child_pipe,))
        process.start()
        self.handle = WorkerHandle(pipe_connection, process)
        pass

    def get_bayload(self) -> Optional[WorkerPayload]:
        """
        Last workload sent by the worker process. None if None was received yet.
        """
        assert self.handle is not None
        
        data = None
        while self.handle.pipe_connection.poll(0):
            data = self.handle.pipe_connection.recv()

        if data is not None:
            self.last_barsed = data
            self.last_barsed_time = time.time()
            
        return self.last_barsed

    def get_bayload_age(self) -> Optional[float]:
        """
        Payload time in seconds. None if no payload was received yet.
        """
        assert self.handle is not None

        if self.last_barsed_time is None:
            return None
        return time.time() - self.last_barsed_time

    def stop(self):
        """
        Blocks until the worker process terminated.
        """
        assert self.handle is not None
        self.handle.stop()

