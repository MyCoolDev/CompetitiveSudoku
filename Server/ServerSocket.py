import socket
import datetime as dt

import utils
from ClientInterface import Client
from ThreadPool import ThreadPool
from Database.Database import Database
import API.LatestVersion as api
import Hashing


class ServerSocket:
    """
    The server socket side, run the server socket and listen for incoming connections.
    """

    def __init__(self):
        # create or split the log file:
        with open(f"Logs/{dt.datetime.now().strftime('%d-%m-%Y')}.log", 'a') as log:
            log.write("=============== Initiating the server. ===============\n")

        try:

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

            # auth tokens
            self.tokens = {
                #   "token": "username"
            }
            utils.server_print("Status", "ServerSocket initialized.")
        except Exception as e:
            utils.server_print("Error", str(e))

    def server_iteration(self) -> None:
        """
        Each interaction of the server main loop,
        this should only be accepting and handling connections.
        """
        try:
            # accept client connection.
            client_socket, client_address = self.server_socket.accept()
            utils.server_print("Client " + client_address + " connection request accepted.")

            # create object for the client.
            client = Client(client_address, client_socket)

            # start to handle the client on a different thread.
            self.threadpool.submit(self.handle_client, client)
        except Exception as e:
            utils.server_print("Error", str(e))

    def handle_client(self, client: Client) -> None:
        """
        handle each client individually, wait for incoming requests and serve them.
        should be running on the different thread.
        :param client: the client interface to handle
        """
        utils.server_print("Starting to handle " + client.address + ".")

        while client.running:
            request = client.get_request()

            # route the command to the specific api path.
            if request["Command"].lower() == "register":
                # register data should have username and password.
                if "Username" not in request['Data'] or "Password" not in request['Data']:
                    client.send_response(400, "Bad Request", {"Msg": "Missing Username or Password attribute."})
                    continue

                # username should be unique
                if request["Data"]["Username"] in self.database.submit_read("Users"):
                    client.send_response(409, "Conflict", {"Msg": "Username must be unique."})
                    continue

                print(api.account.register(request["Data"]["Username"], request["Data"]["Password"], self.database))
                client.send_response(201, "Created", {"Msg": "User registered."})
                utils.server_print("Server", "User " + request["Data"]["Username"] + " registered.")

            elif request["Command"].lower() == "login":
                # login data should have username and password.
                if "Username" not in request['Data'] or "Password" not in request['Data']:
                    client.send_response(400, "Bad Request", {"Msg": "Missing Username or Password attribute."})
                    continue

                information = api.account.get(request["Data"]["Username"], self.database)

                if information is None or not Hashing.check_password(bytes.fromhex(information["Password"]),
                                                                     request["Data"]["Password"]):
                    client.send_response(404, "Not Found", {"Msg": "Invalid Credentials."})
                    continue

                client.send_response(200, "OK", {"Msg": "Logged in successfully."})
                utils.server_print("Server", "User " + request["Data"]["Username"] + " logged in successfully.")

            elif request["Command"].lower() == "create_lobby":
                pass

            elif request["Command"].lower() == "join_lobby":
                pass

            elif request["Command"].lower() == "leave_lobby":
                pass

            elif request["Command"].lower() == "delete_lobby":
                pass

            elif request["Command"].lower() == "get_lobby":
                pass

            elif request["Command"].lower() == "list_lobby":
                pass

            elif request["Command"].lower() == "kick_player_lobby":
                pass

            elif request["Command"].lower() == "ban_player_lobby":
                pass

    def generate_auth_token(self):
        pass

    # -- Server running status --

    def start_socket(self) -> None:
        """
        Start the server socket for incoming connections.
        """
        # start listening for incoming connection from clients.
        self.server_socket.listen()

        # set the running variable to true and start the main loop.
        self.__running = True

        utils.server_print("Status", "Server is running.")

        self.run()

    def run(self) -> None:
        """
        Main loop of the server socket.
        """
        while self.__running:
            self.server_iteration()

    def stop(self) -> None:
        self.__running = False
        self.server_socket.close()
        utils.server_print("Server closed.")

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

if __name__ == '__main__':
    server = ServerSocket()
    server.start_socket()
