import socket

import utils
from ClientInterface import Client
from ThreadPool import ThreadPool
from Database.Database import Database
import API.LatestVersion as api


class ServerSocket:
    """
    The server socket side, run the server socket and listen for incoming connections.
    """
    def __init__(self):
        # *should be in config*, for now just a static var
        self.MAX_CLIENTS = 3

        # all the clients that the server is handling.
        self.clients = []

        # the database interface
        self.database = Database(0)

        # create a socket with tpc protocol.
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # bind the server to the local ip address and port 8080.
        self.server_socket.bind(('127.0.0.1', 8080))

        # running variable for the main loop, variable is private.
        self.__running = False

        # create a thread pool of client handling.
        self.threadpool = ThreadPool(self.MAX_CLIENTS)

    def start_socket(self) -> None:
        """
        Start the server socket for incoming connections.
        """
        # start listening for incoming connection from clients.
        self.server_socket.listen()

        # set the running variable to true and start the main loop.
        self.__running = True
        self.run()

    def run(self) -> None:
        """
        Main loop of the server socket.
        """
        while self.__running:
            self.server_iteration()

    def server_iteration(self) -> None:
        """
        Each interaction of the server main loop,
        this should only be accepting and handling connections.
        """
        # accept client connection.
        client_socket, client_address = self.server_socket.accept()

        # create object for the client.
        client = Client(client_address, client_socket)

        # start to handle the client on a different thread.
        self.threadpool.submit(self.handle_client, client)

    def handle_client(self, client: Client) -> None:
        """
        handle each client individually, wait for incoming requests and serve them.
        should be running on the different thread.
        :param client: the client interface to handle
        """
        utils.server_print("Starts handling " + client.address + ".")

        while client.running:
            request = client.get_request()

            # route the command to the specific api path.
            if request["Command"].lower() == "register":
                # register data should have username and password.
                if "Username" not in request['data'] or "Password" not in request['data']:
                    client.send_response(400, "Bad Request", {"Msg": "Missing Username or Password attribute."})


            # username is unique

    # -- Server running status --

    def stop(self) -> None:
        self.__running = False
        self.server_socket.close()

    def toggle_status(self) -> None:
        if self.__running:
            self.stop()
        else:
            self.start_socket()

    def get_status(self) -> bool:
        return self.__running

    def __repr__(self):
        pass

    def __str__(self):
        pass
