import socket
import datetime as dt
import random
import string

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
        Handle each client individually, wait for incoming requests and serve them.
        Should be running on the different thread.
        :param client: the client interface to handle
        """
        utils.server_print("Handler", "Starting to handle " + str(client.address) + ".")

        while client.running:
            request = client.get_request()
            request_id = self.requests
            self.requests += 1

            rid = request["Id"]

            utils.server_print("Handler", f"Request ({request_id}) received from " + str(client.address) + ".")

            # route the command to the specific api path.
            if request["Command"].lower() == "register":
                """
                Register a new account, login into the new account, return an auth token for authentication next
                """

                utils.server_print("Handler", f"Request ({request_id}) identified as Register from " + str(client.address) + ".")
                # register data should have username and password.
                if "Username" not in request['Data'] or "Password" not in request['Data']:
                    utils.server_print("Handler Error", f"Request ({request_id}), no username or password provided.")
                    client.send_response(rid, 400, "Bad Request", {"Msg": "Missing Username or Password attribute."})
                    continue

                # username should be unique
                if request["Data"]["Username"] in self.database.submit_read("Users"):
                    utils.server_print("Handler Error", f"Request ({request_id}), Username already registered.")
                    client.send_response(rid, 409, "Conflict", {"Msg": "Username must be unique."})
                    continue

                utils.server_print("Handler", f"Request ({request_id}), passed all checks.")

                # generate auth token
                token = self.generate_auth_token()

                # add the token to the used token list
                self.tokens.append(token)

                # update the token and username to client object
                client.set_data("token", token)
                client.set_data("username", request["Data"]["Username"])

                client.send_response(rid, 201, "Created", {"Msg": "User registered.", "Token": token})
                utils.server_print("Server", f"Request ({request_id}), User " + request["Data"]["Username"] + " registered.")

            elif request["Command"].lower() == "login":
                """
                Login to an account using username and password, return an auth token for authentication next.
                """

                utils.server_print("Handler", f"Request ({request_id}), identified as Login from " + str(client.address) + ".")
                # login data should have username and password.
                if "Username" not in request['Data'] or "Password" not in request['Data']:
                    utils.server_print("Handler Error", f"Request ({request_id}), No username or password provided.")
                    client.send_response(rid, 400, "Bad Request", {"Msg": "Missing Username or Password attribute."})
                    continue

                information = api.account.get(request["Data"]["Username"], self.database)

                if information is None or not Hashing.check_password(bytes.fromhex(information["password"]),
                                                                     request["Data"]["Password"]):
                    utils.server_print("Handler Error", f"Request ({request_id}), Invalid credentials.")
                    client.send_response(rid, 404, "Not Found", {"Msg": "Invalid Credentials."})
                    continue

                utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

                # generate auth token
                token = self.generate_auth_token()

                # add the token to the used token list
                self.tokens.append(token)

                # update the token and username to client object
                client.set_data("token", token)
                client.set_data("username", request["Data"]["Username"])

                client.send_response(rid, 200, "OK", {"Msg": "Logged in successfully.", "Token": token})
                utils.server_print("Server", f"Request ({request_id}), User " + request["Data"]["Username"] + " logged in successfully.")

            elif request["Command"].lower() == "create_lobby":
                """
                Create a new lobby using auth token.
                """

                utils.server_print("Handler", f"Request ({request_id}), identified as Create Lobby from " + str(client.address) + ".")

                # check if the token exists
                if "Token" not in request or request["Token"] != client.get_data("token"):
                    utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
                    client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
                    continue

                if client.get_data("lobby") is not None:
                    utils.server_print("Handler Error", f"Request ({request_id}), User {client.get_data('username')} already in lobby.")
                    client.send_response(rid, 409, "Conflict", {"Msg": "User already in lobby."})
                    continue

                utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

                # create and use the lobby
                lobby = self.lobby_manager.create_lobby(client)
                client.set_data("lobby_info", lobby)
                client.send_response(rid, 201, "Created", {"Msg": "Lobby created successfully.", "Lobby_Info": lobby.__repr__()})
                utils.server_print("Server", f"Request ({request_id}), Lobby created successfully.")

            elif request["Command"].lower() == "join_lobby":
                """
                Join lobby using auth token, code.
                """

                utils.server_print("Handler", "Request identified as Join Lobby from " + str(client.address) + ".")

                # check if the token exists
                if "Token" not in request or request["Token"] != client.get_data("token"):
                    utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
                    client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
                    continue

                if client.get_data("lobby_info") is not None:
                    utils.server_print("Handler Error", f"Request ({request_id}), User {client.get_data('username')} already in lobby.")
                    client.send_response(rid, 409, "Conflict", {"Msg": "User already in lobby."})
                    continue

                if "Code" not in request["Data"]:
                    utils.server_print("Handler Error", f"Request ({request_id}), No code provided.")
                    client.send_response(rid, 400, "Bad Request", {"Msg": "No code provided."})

                if request["Data"]["Code"] not in self.lobby_manager.all_lobbies:
                    utils.server_print("Handler Error", f"Request ({request_id}), Invalid code.")
                    client.send_response(rid, 404, "Not Found", {"Msg": "Invalid code."})
                    continue

                utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

                lobby = self.lobby_manager.all_lobbies[request["Data"]["Code"]]
                role = lobby.register_client(client)
                client.set_data("lobby_info", lobby)
                client.send_response(rid, 200, "OK", {"Msg": "Successfully joining lobby.", "Lobby_Info": lobby.__repr__(), "Role": role})

                data = {"Msg": "New user joined the lobby.", "Role": role, "Username": client.get_data("username")}

                if role != "players":
                    del data["Username"]

                for c in lobby.players + lobby.spectators:
                    if c is not client:
                        c.push_notification("User_Joined_Lobby", data)

                utils.server_print("Server", f"Request ({request_id}), Client registered to lobby.")

            elif request["Command"].lower() == "become_lobby_spectator":
                """
                Become a lobby spectator, for players. 
                """

                utils.server_print("Handler", "Request identified as Become Lobby Spectator from " + str(client.address) + ".")

                # check if the token exists
                if "Token" not in request or request["Token"] != client.get_data("token"):
                    utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
                    client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
                    continue

                lobby = client.get_data("lobby_info")

                if lobby is None:
                    utils.server_print("Handler Error", f"Request ({request_id}), User {client.get_data('username')} already in lobby.")
                    client.send_response(rid, 409, "Conflict", {"Msg": "User already in lobby."})
                    continue

                # in case the user is not a player
                if client not in lobby.players:
                    utils.server_print("Handler Error", f"Request ({request_id}), User {client.get_data('username')} not in a player.")
                    client.send_response(rid, 409, "Conflict", {"Msg": "User is already a spectator."})
                    continue

                utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

                lobby.players.remove(client)
                lobby.spectators.append(client)

                client.send_response(rid, 200, "Ok", {"Msg": "Successfully becoming a spectator."})

                for c in lobby.players + lobby.spectators:
                    pass
                    

            elif request["Command"].lower() == "leave_lobby":
                """
                Leave the lobby using auth token, return the information on the lobby.
                """

                utils.server_print("Handler", f"Request ({request_id}), identified as Leave Lobby from " + str(client.address) + ".")

                # check if the token exists
                if "Token" not in request or request["Token"] != client.get_data("token"):
                    utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
                    client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
                    continue

                if client.get_data("lobby_info") is None:
                    utils.server_print("Handler Error", f"Request ({request_id}), User {client.get_data('username')} isn't in lobby.")
                    client.send_response(rid, 409, "Conflict", {"Msg": "User isn't in lobby."})
                    continue

                utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

                lobby = client.get_data("lobby_info")
                lobby.remove_client(client)
                utils.server_print("Server", f"Request ({request_id}), Client {client.get_data('username')} leaved the lobby {lobby.code}.")
                client.send_response(rid, 200, "OK", {"Msg": "Successfully leaving lobby."})

            elif request["Command"].lower() == "delete_lobby":
                pass

            elif request["Command"].lower() == "get_lobby":
                """
                Get lobby information using code.
                """

                utils.server_print("Handler", f"Request ({request_id}), identified as Get Lobby from " + str(client.address) + ".")

                # check if the token exists
                if "Token" not in request or request["Token"] != client.get_data("token"):
                    utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
                    client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
                    continue

                if "Code" not in request["Data"]:
                    utils.server_print("Handler Error", f"Request ({request_id}), No code provided.")
                    client.send_response(rid, 400, "Bad Request", {"Msg": "No code provided."})
                    continue

                if request["Data"]["Code"] not in self.lobby_manager.all_lobbies:
                    utils.server_print("Handler Error", f"Request ({request_id}), Invalid code.")
                    client.send_response(rid, 404, "Not Found", {"Msg": "Invalid code."})
                    continue

                utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

                lobby = self.lobby_manager.all_lobbies[request["Data"]["Code"]]
                utils.server_print("Server", f"Request ({request_id}), Client {client.get_data('username')} leaved the lobby {lobby.code}.")
                client.send_response(rid, 200, "OK", {"Lobby_Info": lobby.__repr__()})

            elif request["Command"].lower() == "kick_user_lobby":
                """
                Kick a player from a lobby, owner only.
                """

                utils.server_print("Handler", f"Request ({request_id}), identified as Kick User From Lobby from " + str(client.address) + ".")

                # check if the token exists
                if "Token" not in request or request["Token"] != client.get_data("token"):
                    utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
                    client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
                    continue

                lobby: Lobby = client.get_data("lobby_info")

                if lobby is None:
                    utils.server_print("Handler Error", f"Request ({request_id}), User {client.get_data('username')} isn't in lobby.")
                    client.send_response(rid, 409, "Conflict", {"Msg": "User isn't in lobby."})
                    continue

                if client == lobby.owner:
                    utils.server_print("Handler Error", f"Request ({request_id}), User {client.get_data('username')} isn't the owner of lobby {lobby.code}.")
                    client.send_response(rid, 409, "Conflict", {"Msg": "User isn't the owner of lobby."})
                    continue

                if "Username" in request["Data"]:
                    utils.server_print("Handler Error", f"Request ({request_id}), No username provided.")
                    client.send_response(rid, 400, "Bad Request", {"Msg": "No username provided."})
                    continue

                information = api.account.get(request["Data"]["Username"], self.database)

                if information is None:
                    utils.server_print("Handler Error", f"Request ({request_id}), Invalid username.")
                    client.send_response(rid, 404, "Not Found", {"Msg": "Invalid username."})
                    continue

                lobby: Lobby = client.get_data("lobby")
                client_to_ban: Client = lobby.get_client(request["Data"]["Username"])

                if client_to_ban is None:
                    utils.server_print("Handler Error", f"Request ({request_id}), User to kick isn't in lobby.")
                    client.send_response(rid, 404, "Not Found", "User to kick isn't in lobby.")

                utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

                lobby.remove_client(client_to_ban)
                utils.server_print("Server", f"Request ({request_id}), Client {request['Data']['Username']} kicked the lobby {lobby.code}.")
                client_to_ban.push_notification("Lobby_Kick", {"Msg": "You have been kicked from the lobby."})
                client.send_response(rid, 200, "OK", {"Msg": "User kicked."})

            elif request["Command"].lower() == "ban_player_lobby":
                utils.server_print("Handler", f"Request ({request_id}), identified as Ban User From Lobby from " + str(client.address) + ".")

                # check if the token exists
                if "Token" not in request or request["Token"] != client.get_data("token"):
                    utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
                    client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
                    continue

                lobby: Lobby = client.get_data("lobby_info")

                if lobby is None:
                    utils.server_print("Handler Error",
                                       f"Request ({request_id}), User {client.get_data('username')} isn't in lobby.")
                    client.send_response(rid, 409, "Conflict", {"Msg": "User isn't in lobby."})
                    continue

                if client == lobby.owner:
                    utils.server_print("Handler Error",
                                       f"Request ({request_id}), User {client.get_data('username')} isn't the owner of lobby {lobby.code}.")
                    client.send_response(rid, 409, "Conflict", {"Msg": "User isn't the owner of lobby."})
                    continue

                if "Username" in request["Data"]:
                    utils.server_print("Handler Error", f"Request ({request_id}), No username provided.")
                    client.send_response(rid, 400, "Bad Request", {"Msg": "No username provided."})
                    continue

                information = api.account.get(request["Data"]["Username"], self.database)

                if information is None:
                    utils.server_print("Handler Error", f"Request ({request_id}), Invalid username.")
                    client.send_response(rid, 404, "Not Found", {"Msg": "Invalid username."})
                    continue

                lobby: Lobby = client.get_data("lobby")
                client_to_ban: Client = lobby.get_client(request["Data"]["Username"])

                if client_to_ban is None:
                    utils.server_print("Handler Error", f"Request ({request_id}), User to ban isn't in lobby.")
                    client.send_response(rid, 404, "Not Found", "User to ban isn't in lobby.")

                utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

                lobby.ban_client(client_to_ban)
                utils.server_print("Server", f"Request ({request_id}), Client {request['Data']['Username']} Baned the lobby {lobby.code}.")
                client_to_ban.push_notification("Lobby_Ban", {"Msg": "You have been Baned from the lobby."})
                client.send_response(rid, 200, "OK", {"Msg": "User Baned."})

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
