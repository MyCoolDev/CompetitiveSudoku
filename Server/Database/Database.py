import json
import os
import threading
from queue import Queue

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
        self.task_queue = []
        self.shutdown_event = threading.Event()

        # create the thread
        thread = threading.Thread(target=self.worker)

        # ensures threads exit when the main program exits
        thread.daemon = True

        # start running the thread on the worker function
        thread.start()

        utils.server_print("Database", "Database worker is running")

    def worker(self):
        """
        The worker function that will handle all the db jobs
        :return:
        """
        while not self.shutdown_event.is_set():
            try:
                # get a task from the queue
                obj = self.task_queue.pop(0)

                try:
                    # execute the task and store the result
                    result = obj[0](*obj[2])

                    if obj[1]:
                        # push the result to the result queue
                        obj[1].put(result)

                except Exception as e:
                    utils.server_print("Database", f"Error processing db task: {e}")
            finally:
                continue

    def submit_read(self, collection: str) -> str or None:
        """
        Submit a read command to the worker queue.
        :param collection: the collection to work on.
        :return: the data from the collection.
        """
        result_queue = Queue()

        self.task_queue.append((self.read, result_queue, [self.profile, collection]))

        while result_queue.empty():
            continue

        return result_queue.get()

    @staticmethod
    def read(profile, collection: str) -> str or None:
        try:
            with open(os.getcwd() + f"\\Database\\{profile}\\{collection}.json", "r") as f:
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

        self.task_queue.append((self.update, result_queue, [self.profile, collection, data]))

        while result_queue.empty():
            continue

        return result_queue.get()

    @staticmethod
    def update(profile: str, collection: str, data: dict) -> bool:
        """
        Update the collection with the new data.
        :param profile: The profile of the database.
        :param collection: The collection to work on.
        :param data: The new data to be writen the collection.
        :return: The success of the update command.
        """
        try:
            with open(os.getcwd() + f"\\Database\\{profile}\\{collection}.json", "w") as f:
                f.write(json.dumps(data, indent=4))

            return True
        except Exception as e:
            utils.server_print("Database", f"Error updating db collection: {e}")
            return False
