import threading
from queue import Queue

from typing import Callable

class ThreadPool:
    def __init__(self, num_threads: int):
        """
        Create a pool of thread that will manage the thread we're using in the program.
        All the thread will be running, but they will wait for a task or run a task.
        :param num_threads: the amount of threads in the pool, all the threads will be running, but some of them may be on wait.
        """
        # the Queue.Queue is thread-safe, so multiple threads can access it concurrently.
        self.task_queue = Queue()
        self.threads = []
        self.shutdown_event = threading.Event()

        # initialize and start worker threads
        for _ in range(num_threads):

            # create the thread
            thread = threading.Thread(target=self.worker)

            # ensures threads exit when the main program exits
            thread.daemon = True

            # start running the thread on the worker function
            thread.start()

            # add the thread to the list.
            self.threads.append(thread)

    def worker(self) -> None:
        """
        The main loop of each thread, here a thread may wait for a task in the pool or execute a task.
        """
        # check the shutdown event for shutdown.
        while not self.shutdown_event.is_set():
            try:
                # get a task from the queue
                # *timeout prevents deadlock on shutdown*
                task, args, kwargs = self.task_queue.get(timeout=1)

                try:
                    # execute the task
                    task(*args, **kwargs)

                except Exception as e:
                    print(f"Error executing task: {e}")

                finally:
                    # mark the task as done
                    self.task_queue.task_done()

            # empty() - not reliable?
            except self.task_queue.empty():

                # Timeout reached, loop to check shutdown_event
                continue

    def submit(self, task: Callable, *args, **kwargs) -> None:
        """
        Submit a task to the pool.
        :param task: the function to execute
        :param args: the arguments for the function
        :param kwargs: key-value arguments for the function
        """
        self.task_queue.put((task, args, kwargs))

    def shutdown(self, wait=False) -> None:
        """
        Shut down the thread pool.
        :param wait: should the pool wait for all the threads to end. by default set to False.
        """
        # emit the threads to stop
        self.shutdown_event.set()

        if wait:
            for thread in self.threads:
                # wait for all threads to finish
                thread.join()
