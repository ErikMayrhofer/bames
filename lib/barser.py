from multiprocessing import Process, Pipe, connection
from typing import Optional
import time

class WorkerPayload:
    """
    The actual 
    """
    def __init__(self, message: str):
        self.message = message

def barser_worker(pipe_connection: connection.Connection):
    running = True

    while running:
        if pipe_connection.poll(0):
            res = pipe_connection.recv()
            if res:
                running = False

        time.sleep(0.8) 
        pipe_connection.send(WorkerPayload(message="Helo"))

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
        self.process.join(2)
        if self.process.is_alive():
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
            print("Receiv.")
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

