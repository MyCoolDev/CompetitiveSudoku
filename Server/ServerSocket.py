import socket
import datetime as dt
import random
import string
import codecs

import utils
from ClientInterface import Client
from ThreadPool import ThreadPool
from Database.Database import Database
import API.LatestVersion as api
import Hashing
from Lobby import Lobby, LobbyManager


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

            self.lobby_manager = LobbyManager()

            # all the tokens that have been generated.
            self.tokens = []

            # request counter - used for request identification
            self.requests = 0

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
            utils.server_print("Connection", "Client " + str(client_address) + " connection request accepted.")

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
        utils.server_print("Handler", "Starting to handle " + str(client.address) + ".")

        while client.running:
            request = client.get_request()
            request_id = self.requests
            self.requests += 1

            utils.server_print("Handler", f"Request ({request_id}) received from " + str(client.address) + ".")

            # route the command to the specific api path.
            if request["Command"].lower() == "register":
                utils.server_print("Handler", f"Request ({request_id}) identified as Register from " + str(client.address) + ".")
                # register data should have username and password.
                if "Username" not in request['Data'] or "Password" not in request['Data']:
                    utils.server_print("Handler Error", f"Request ({request_id}), no username or password provided.")
                    client.send_response(400, "Bad Request", {"Msg": "Missing Username or Password attribute."})
                    continue

                # username should be unique
                if request["Data"]["Username"] in self.database.submit_read("Users"):
                    utils.server_print("Handler Error", f"Request ({request_id}), Username already registered.")
                    client.send_response(409, "Conflict", {"Msg": "Username must be unique."})
                    continue

                utils.server_print("Handler", f"Request ({request_id}), passed all checks.")

                # generate auth token
                token = self.generate_auth_token()

                # add the token to the used token list
                self.tokens.append(token)

                # update the token and username to client object
                client.token = token
                client.username = request["Data"]["Username"]

                client.send_response(201, "Created", {"Msg": "User registered.", "Token": token})
                utils.server_print("Server", f"Request ({request_id}), User " + request["Data"]["Username"] + " registered.")

            elif request["Command"].lower() == "login":
                utils.server_print("Handler", f"Request ({request_id}), identified as Login from " + str(client.address) + ".")
                # login data should have username and password.
                if "Username" not in request['Data'] or "Password" not in request['Data']:
                    utils.server_print("Handler Error", f"Request ({request_id}), No username or password provided.")
                    client.send_response(400, "Bad Request", {"Msg": "Missing Username or Password attribute."})
                    continue

                information = api.account.get(request["Data"]["Username"], self.database)

                if information is None or not Hashing.check_password(bytes.fromhex(information["password"]),
                                                                     request["Data"]["Password"]):
                    utils.server_print("Handler Error", f"Request ({request_id}), Invalid credentials.")
                    client.send_response(404, "Not Found", {"Msg": "Invalid Credentials."})
                    continue

                utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

                # generate auth token
                token = self.generate_auth_token()

                # add the token to the used token list
                self.tokens.append(token)

                # update the token and username to client object
                client.set_data("token", token)
                client.set_data("username", request["Data"]["Username"])

                client.send_response(200, "OK", {"Msg": "Logged in successfully.", "Token": token})
                utils.server_print("Server", f"Request ({request_id}), User " + request["Data"]["Username"] + " logged in successfully.")

            elif request["Command"].lower() == "create_lobby":
                utils.server_print("Handler", "Request identified as Create Lobby from " + str(client.address) + ".")

                print(request)

                # check if the token exists
                if "Token" not in request or request["Token"] != client.get_data("token"):
                    utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
                    client.send_response(400, "Bad Request", {"Msg": "No Token provided."})
                    continue

                if client.get_data("lobby") is not None:
                    utils.server_print("Handler Error", "User already in lobby.")
                    client.send_response(409, "Conflict", {"Msg": "User already in lobby."})
                    continue

                # create and use the lobby
                lobby = self.lobby_manager.create_lobby(client)
                client.send_response(201, "Created", {"Msg": "Lobby created successfully.", "Lobby_Info": lobby.__repr__()})
                utils.server_print("Server", f"Request ({request_id}), Lobby created successfully.")

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
        """
        generate an auth token to the user.
        """

        token = "".join([random.choice(string.hexdigits) for _ in range(32)])

        while token in self.tokens:
            token = "".join([random.choice(string.hexdigits) for _ in range(32)])

        return token

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
