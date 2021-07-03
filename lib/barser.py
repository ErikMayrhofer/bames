from multiprocessing import Process, Pipe, connection
from typing import Optional
import time

class WorkerPayload:
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
    handle: Optional[WorkerHandle]
    last_barsed: Optional[WorkerPayload]
    last_barsed_age: Optional[float]
    def __init__(self):
        self.handle = None
        self.last_barsed = None
        self.last_barsed_age = None
        pass

    def launch(self):
        pipe_connection, child_pipe = Pipe()
        process = Process(target=barser_worker, args=(child_pipe,))
        process.start()
        self.handle = WorkerHandle(pipe_connection, process)
        pass

    def get_barsed_field(self) -> Optional[WorkerPayload]:
        assert self.handle is not None
        
        data = None
        while self.handle.pipe_connection.poll(0):
            print("Receiv.")
            data = self.handle.pipe_connection.recv()

        if data is not None:
            self.last_barsed = data
            self.last_barsed_age = time.time()
            
        return self.last_barsed

    def get_barsed_age(self) -> Optional[float]:
        assert self.handle is not None

        if self.last_barsed_age is None:
            return None
        return time.time() - self.last_barsed_age

    def stop(self):
        assert self.handle is not None
        self.handle.stop()

