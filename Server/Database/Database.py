import json
from queue import Queue
import threading

from abc import ABC, abstractmethod

import Server.utils as utils


# maybe add cache system ;(

class Database:
    def __init__(self, profile: int):
        """
        Manage the database to prevent overriding and problems, also for easy use.
        Simple implementations.
        Profile is a temp solution for the config and run system.
        :param profile: database profile id, 0 - tests, 1 - official.
        """
        # set the default profile to be 0 in case of unrecognized profile.
        self.profile = "Tests" if profile not in [0, 1] else "Tests" if profile == 0 else "Official"

        # the Queue.Queue is thread-safe, so multiple threads can access it concurrently.
        self.task_queue = Queue()
        self.shutdown_event = threading.Event()

        # create the thread
        thread = threading.Thread(target=self.worker)

        # ensures threads exit when the main program exits
        thread.daemon = True

        # start running the thread on the worker function
        thread.start()

        utils.server_print("Database", "Database worker is running")

    def worker(self):
        while not self.shutdown_event.is_set():
            try:
                # get a task from the queue
                task, result_queue, args, kwargs = self.task_queue.get(timeout=1)

                try:
                    # execute the task and store the result
                    result = task(*args, **kwargs)

                    if result_queue:
                        # push the result to the result queue
                        result_queue.put(result)

                except Exception as e:
                    utils.server_print("Database", f"Error processing db task: {e}")

                finally:
                    # mark the task as done
                    self.task_queue.task_done()
            finally:
                continue

    def submit_read(self, collection: str) -> str or None:
        """
        Submit a read command to the worker queue.
        :param collection: the collection to work on.
        :return: the data from the collection.
        """
        result_queue = Queue()

        self.task_queue.put((self.read, result_queue, collection))

        while result_queue.empty():
            continue

        return result_queue.get()

    def read(self, collection: str) -> str or None:
        try:
            with open(f"/{self.profile}/{collection}.json", "r") as f:
                data = json.load(f)

                return data
        except FileNotFoundError:
            print(f"File not found: {collection}.json")
            return None
        except json.decoder.JSONDecodeError:
            print(f"Invalid JSON: {collection}.json")
            return None
        except Exception as e:
            print(f"Error processing db task: {e}")
            return None

    def submit_update(self, collection: str, data: dict) -> bool:
        """
        Submit an update command to the worker queue.
        :param collection: the collection to work on.
        :param data: the new data to be writen the collection.
        :return: The success of the update command.
        """
        result_queue = Queue()

        self.task_queue.put((self.read, result_queue, collection, data))

        while result_queue.empty():
            continue

        return result_queue.get()

    def update(self, collection: str, data: dict) -> bool:
        try:
            with open(f"/{self.profile}/{collection}.json", "w") as f:
                f.write(json.dumps(data))

            return True
        except Exception as e:
            utils.server_print("Database", f"Error updating db collection: {e}")
            return False