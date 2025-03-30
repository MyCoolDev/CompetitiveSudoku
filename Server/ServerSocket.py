import argparse
import datetime as dt
import random
import socket
import string

import Methods.LatestVersion as api
import Hashing
import utils
from ClientInterface import Client
from Database.Database import Database
from Lobby import Lobby, LobbyManager
from ThreadPool import ThreadPool


class ServerSocket:
    """
    The server socket side, run the server socket and listen for incoming connections.
    """

    def __init__(self, address, port, db_profile):
        # create or split the log file:
        with open(f"Logs/{dt.datetime.now().strftime('%d-%m-%Y')}.log", 'a') as log:
            log.write("=============== Initiating the server. ===============\n")

        try:
            # *should be in config*, for now just a static var
            self.MAX_CLIENTS = 3

            # all the clients that the server is handling.
            self.clients = []

            # all the clients that have already logged in
            self.logged_clients = {}

            # the database interface
            self.db_profile = db_profile
            self.database = Database(db_profile)

            # create a socket with tpc protocol.
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # set up the address and port for the server.
            self.address = address
            self.port = port

            # bind the server to the local ip address and port 8080.
            self.server_socket.bind((self.address, self.port))

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

            self.clients.append(client)
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
            try:
                request = client.get_request()
                request_id = self.requests
                self.requests += 1

                rid = request["Id"]

                utils.server_print("Handler", f"Request ({request_id}) received from " + str(client.address) + ".")

                # route the command to the specific api path.
                if request["Command"].lower() == "register":
                    self.handle_register(client, request, rid, request_id)

                elif request["Command"].lower() == "login":
                    self.handle_login(client, request, rid, request_id)

                elif request["Command"].lower() == "create_lobby":
                    self.handle_create_lobby(client, request, rid, request_id)

                elif request["Command"].lower() == "join_lobby":
                    self.handle_join_lobby(client, request, rid, request_id)

                elif request["Command"].lower() == "leave_lobby":
                    self.handle_leave_lobby(client, request, rid, request_id)

                elif request["Command"].lower() == "delete_lobby":
                    pass

                elif request["Command"].lower() == "get_lobby":
                    self.handle_get_lobby(client, request, rid, request_id)

                elif request["Command"].lower() == "become_lobby_spectator":
                    self.handle_become_lobby_spectator(client, request, rid, request_id)

                elif request["Command"].lower() == "become_lobby_player":
                    self.handle_become_lobby_player(client, request, rid, request_id)

                elif request["Command"].lower() == "make_lobby_spectator":
                    self.handle_make_lobby_spectator(client, request, rid, request_id)

                elif request["Command"].lower() == "kick_user_lobby":
                    self.handle_kick_user_lobby(client, request, rid, request_id)

                elif request["Command"].lower() == "ban_user_lobby":
                    self.handle_ban_user_lobby(client, request, rid, request_id)

                elif request["Command"].lower() == "start_game":
                    self.handle_start_game(client, request, rid, request_id)

                elif request["Command"].lower() == "game_move":
                    pass

                elif request["Command"].lower() == "add_friend":
                    self.handle_add_friend(client, request, rid, request_id)

                elif request["Command"].lower() == "accept_friend":
                    self.handle_accept_friend(client, request, rid, request_id)

                elif request["Command"].lower() == "reject_friend":
                    self.handle_reject_friend(client, request, rid, request_id)

                elif request["Command"].lower() == "invite_friend":
                    pass
                elif request["Command"].lower() == "accept_friend_invitation":
                    pass
                elif request["Command"].lower() == "reject_friend_invitation":
                    pass
                elif request["Command"].lower() == "get_friend_information":
                    pass
                elif request["Command"].lower() == "message_friend":
                    pass
                elif request["Command"].lower() == "get_chat_information":
                    pass
            except Exception as e:
                utils.server_print("Error", str(e))
                self.disconnect_user(client)
                break

    # -- Server Command Handlers --

    def handle_register(self, client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Register a new account, login into the new account, return an auth token for authentication next
        """

        utils.server_print("Handler",
                           f"Request ({request_id}) identified as Register from " + str(client.address) + ".")
        # register data should have username and password.
        if "Username" not in request['Data'] or "Password" not in request['Data']:
            utils.server_print("Handler Error", f"Request ({request_id}), no username or password provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "Missing Username or Password attribute."})
            return

        # username should be unique
        if request["Data"]["Username"] in self.database.submit_read("Users"):
            utils.server_print("Handler Error", f"Request ({request_id}), Username already registered.")
            client.send_response(rid, 409, "Conflict", {"Msg": "Username must be unique."})
            return

        utils.server_print("Handler", f"Request ({request_id}), passed all checks.")

        # register the user
        if not api.account.register(client.address, request["Data"]["Username"], request["Data"]["Password"], self.database):
            utils.server_print("Handler Error", f"Request ({request_id}), Error while registering the user.")
            client.send_response(rid, 500, "Internal Server Error", {"Msg": "Error while registering the user."})
            return

        # generate auth token
        token = self.generate_auth_token()

        # add the token to the used token list
        self.tokens.append(token)

        # update the token and username to client object
        client.set_data("token", token)
        client.set_data("username", request["Data"]["Username"])

        self.logged_clients[request["Data"]["Username"]] = client

        # get user friend list
        friends = api.friend.get_friend_list(request["Data"]["Username"], self.logged_clients, self.database)

        client.send_response(rid, 201, "Created", {"Msg": "User registered.", "Token": token, "Friends": friends})
        utils.server_print("Server", f"Request ({request_id}), User " + request["Data"]["Username"] + " registered.")

    def handle_login(self, client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Login to an account using username and password, return an auth token for authentication next.
        """

        utils.server_print("Handler", f"Request ({request_id}), identified as Login from " + str(client.address) + ".")
        # login data should have username and password.
        if "Username" not in request['Data'] or "Password" not in request['Data']:
            utils.server_print("Handler Error", f"Request ({request_id}), No username or password provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "Missing Username or Password attribute."})
            return

        information = api.account.get(request["Data"]["Username"], self.database)

        if information is None or not Hashing.check_password(bytes.fromhex(information["password"]),
                                                             request["Data"]["Password"]):
            utils.server_print("Handler Error", f"Request ({request_id}), Invalid credentials.")
            client.send_response(rid, 404, "Not Found", {"Msg": "Invalid Credentials."})
            return

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        # generate auth token
        token = self.generate_auth_token()

        # add the token to the used token list
        self.tokens.append(token)

        # update the token and username to client object
        client.set_data("token", token)
        client.set_data("username", request["Data"]["Username"])

        self.logged_clients[request["Data"]["Username"]] = client

        # get user friend list
        friends = api.friend.get_friend_list(request["Data"]["Username"], self.logged_clients, self.database)

        client.send_response(rid, 200, "OK", {"Msg": "Logged in successfully.", "Token": token, "Friends": friends})
        utils.server_print("Server",
                           f"Request ({request_id}), User " + request["Data"]["Username"] + " logged in successfully.")
        api.account.update_login_data(client.address, request["Data"]["Username"], self.database)

    def handle_create_lobby(self, client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Create a new lobby using auth token.
        """

        utils.server_print("Handler",
                           f"Request ({request_id}), identified as Create Lobby from " + str(client.address) + ".")

        # check if the token exists
        if "Token" not in request or request["Token"] != client.get_data("token"):
            utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
            return

        if client.get_data("lobby") is not None:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} already in lobby.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User already in lobby."})
            return

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        # create and use the lobby
        lobby = self.lobby_manager.create_lobby(client)
        client.set_data("lobby_info", lobby)
        client.send_response(rid, 201, "Created",
                             {"Msg": "Lobby created successfully.", "Lobby_Info": lobby.__repr__()})
        utils.server_print("Server", f"Request ({request_id}), Lobby created successfully.")

    def handle_join_lobby(self, client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Join lobby using auth token, code.
        """

        utils.server_print("Handler", "Request identified as Join Lobby from " + str(client.address) + ".")

        # check if the token exists
        if "Token" not in request or request["Token"] != client.get_data("token"):
            utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
            return

        if client.get_data("lobby_info") is not None:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} already in lobby.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User already in lobby."})
            return

        if "Code" not in request["Data"]:
            utils.server_print("Handler Error", f"Request ({request_id}), No code provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No code provided."})

        if request["Data"]["Code"] not in self.lobby_manager.all_lobbies:
            utils.server_print("Handler Error", f"Request ({request_id}), Invalid code.")
            client.send_response(rid, 404, "Not Found", {"Msg": "Invalid code."})
            return

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        lobby = self.lobby_manager.all_lobbies[request["Data"]["Code"]]
        role, success = lobby.register_client(client)
        if success:
            client.set_data("lobby_info", lobby)
            client.send_response(rid, 200, "OK",
                                 {"Msg": "Successfully joining lobby.", "Lobby_Info": lobby.__repr__(), "Role": role})

            data = {"Msg": "New user joined the lobby.", "Role": role, "Username": client.get_data("username")}

            if role != "players":
                del data["Username"]

            for c in lobby.players + lobby.spectators:
                if c is not client:
                    c.push_notification("User_Joined_Lobby", data)

            utils.server_print("Server", f"Request ({request_id}), Client registered to lobby {lobby.code}.")
        else:
            client.send_response(rid, 409, "Conflict", {"Msg": "You're blocked from the lobby."})
            utils.server_print("Server", f"Request ({request_id}), Client is blocked from lobby {lobby.code}")

    @staticmethod
    def handle_leave_lobby(client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Leave the lobby using auth token, return the information on the lobby.
        """

        utils.server_print("Handler",
                           f"Request ({request_id}), identified as Leave Lobby from " + str(client.address) + ".")

        # check if the token exists
        if "Token" not in request or request["Token"] != client.get_data("token"):
            utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
            return

        if client.get_data("lobby_info") is None:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} isn't in lobby.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User isn't in lobby."})
            return

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        lobby = client.get_data("lobby_info")
        role, success = lobby.remove_client(client)

        if success:
            utils.server_print("Server",
                               f"Request ({request_id}), Client {client.get_data('username')} leaved the lobby {lobby.code}.")
            client.send_response(rid, 200, "OK", {"Msg": "Successfully leaving lobby."})

            for c in lobby.players + lobby.spectators:
                c.push_notification("User_Left_Lobby", {"Username": request["Data"]["Username"], "Role": role})

    def handle_get_lobby(self, client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Get lobby information using code.
        """

        utils.server_print("Handler",
                           f"Request ({request_id}), identified as Get Lobby from " + str(client.address) + ".")

        # check if the token exists
        if "Token" not in request or request["Token"] != client.get_data("token"):
            utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
            return

        if "Code" not in request["Data"]:
            utils.server_print("Handler Error", f"Request ({request_id}), No code provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No code provided."})
            return

        if request["Data"]["Code"] not in self.lobby_manager.all_lobbies:
            utils.server_print("Handler Error", f"Request ({request_id}), Invalid code.")
            client.send_response(rid, 404, "Not Found", {"Msg": "Invalid code."})
            return

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        lobby = self.lobby_manager.all_lobbies[request["Data"]["Code"]]
        utils.server_print("Server",
                           f"Request ({request_id}), Client {client.get_data('username')} leaved the lobby {lobby.code}.")
        client.send_response(rid, 200, "OK", {"Lobby_Info": lobby.__repr__()})

    @staticmethod
    def handle_become_lobby_spectator(client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Become a lobby spectator, for players.
        """

        utils.server_print("Handler", "Request identified as Become Lobby Spectator from " + str(client.address) + ".")

        # check if the token exists
        if "Token" not in request or request["Token"] != client.get_data("token"):
            utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
            return

        lobby = client.get_data("lobby_info")

        if lobby is None:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} isn't in lobby.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User isn't in lobby."})
            return

        # in case the user is not a player
        if client in lobby.spectators:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} is already a spectator.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User is already a spectator."})
            return

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        lobby.players.remove(client)
        lobby.spectators.append(client)

        client.send_response(rid, 200, "Ok", {"Msg": "Successfully becoming a spectator."})
        utils.server_print("Server",
                           f"Request ({request_id}), Client {client.get_data('username')} became a spectator on lobby {lobby.code}.")

        for c in lobby.players + lobby.spectators:
            if c is not client:
                c.push_notification("Become_Spectator", {"Username": client.get_data("username")})

    @staticmethod
    def handle_become_lobby_player(client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Become a lobby player, for spectators.
        """

        utils.server_print("Handler", "Request identified as Become Lobby Player from " + str(client.address) + ".")

        # check if the token exists
        if "Token" not in request or request["Token"] != client.get_data("token"):
            utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
            return

        lobby = client.get_data("lobby_info")

        if lobby is None:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} isn't in lobby.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User isn't in lobby."})
            return

        # in case the user is a player
        if client in lobby.players:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} not in a player.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User is already a players."})
            return

        if len(lobby.players) >= lobby.MAX_PLAYERS:
            utils.server_print("Handler Error", f"Request ({request_id}), The lobby {lobby.code} is full.")
            client.send_response(rid, 409, "Conflict", {"Msg": "The lobby is full."})

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        lobby.players.append(client)
        lobby.spectators.remove(client)

        client.send_response(rid, 200, "Ok", {"Msg": "Successfully becoming a player."})
        utils.server_print("Server",
                           f"Request ({request_id}), Client {client.get_data('username')} became a player on lobby {lobby.code}.")

        for c in lobby.players + lobby.spectators:
            if c is not client:
                c.push_notification("Become_Player", {"Username": client.get_data("username")})

    def handle_make_lobby_spectator(self, client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Make a lobby spectator, for players.
        """

        utils.server_print("Handler", "Request identified as Make Lobby Spectator from " + str(client.address) + ".")

        # check if the token exists
        if "Token" not in request or request["Token"] != client.get_data("token"):
            utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
            return

        lobby = client.get_data("lobby_info")

        if lobby is None:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} already in lobby.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User already in lobby."})
            return

        if client is not lobby.owner:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} isn't the owner of lobby {lobby.code}.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User isn't the owner of lobby."})
            return

        if "Username" not in request["Data"]:
            utils.server_print("Handler Error", f"Request ({request_id}), No username provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No username provided."})
            return

        information = api.account.get(request["Data"]["Username"], self.database)

        if information is None:
            utils.server_print("Handler Error", f"Request ({request_id}), Invalid username.")
            client.send_response(rid, 404, "Not Found", {"Msg": "Invalid username."})
            return

        requested_client = self.logged_clients[request["Data"]["Username"]]

        # in case the user is not a player
        if requested_client not in lobby.players:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {request['Data']['Username']} not in a player.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User is already a spectator."})
            return

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        lobby.players.remove(requested_client)
        lobby.spectators.append(requested_client)

        client.send_response(rid, 200, "Ok", {"Msg": "Successfully making a spectator."})

        for c in lobby.players + lobby.spectators:
            if c is not client:
                c.push_notification("Become_Spectator", {"Username": request["Data"]["Username"]})

    def handle_kick_user_lobby(self, client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Kick a player from a lobby, owner only.
        """

        utils.server_print("Handler", f"Request ({request_id}), identified as Kick User From Lobby from " + str(
            client.address) + ".")

        # check if the token exists
        if "Token" not in request or request["Token"] != client.get_data("token"):
            utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
            return

        lobby: Lobby = client.get_data("lobby_info")

        if lobby is None:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} isn't in lobby.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User isn't in lobby."})
            return

        if client is not lobby.owner:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} isn't the owner of lobby {lobby.code}.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User isn't the owner of lobby."})
            return

        if "Username" not in request["Data"]:
            utils.server_print("Handler Error", f"Request ({request_id}), No username provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No username provided."})
            return

        information = api.account.get(request["Data"]["Username"], self.database)

        if information is None:
            utils.server_print("Handler Error", f"Request ({request_id}), Invalid username.")
            client.send_response(rid, 404, "Not Found", {"Msg": "Invalid username."})
            return

        lobby: Lobby = client.get_data("lobby")
        client_to_kick: Client = lobby.get_client(request["Data"]["Username"])

        if client_to_kick is None:
            utils.server_print("Handler Error", f"Request ({request_id}), User to kick isn't in lobby.")
            client.send_response(rid, 404, "Not Found", "User to kick isn't in lobby.")

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        lobby.remove_client(client_to_kick)
        utils.server_print("Server",
                           f"Request ({request_id}), Client {request['Data']['Username']} kicked the lobby {lobby.code}.")
        client_to_kick.push_notification("Lobby_Kick", {"Msg": "You have been kicked from the lobby."})
        client.send_response(rid, 200, "OK", {"Msg": "User kicked."})

        for c in lobby.players + lobby.spectators:
            if c is not client:
                c.push_notification("Use_Left_Lobby",
                                    {"Username": client_to_kick.get_data("username"), "Role": "players"})

    def handle_ban_user_lobby(self, client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Ban a player from a lobby, owner only.
        """
        utils.server_print("Handler", f"Request ({request_id}), identified as Ban User From Lobby from " + str(
            client.address) + ".")

        # check if the token exists
        if "Token" not in request or request["Token"] != client.get_data("token"):
            utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
            return

        lobby: Lobby = client.get_data("lobby_info")

        if lobby is None:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} isn't in lobby.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User isn't in lobby."})
            return

        if client is not lobby.owner:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} isn't the owner of lobby {lobby.code}.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User isn't the owner of lobby."})
            return

        if "Username" not in request["Data"]:
            utils.server_print("Handler Error", f"Request ({request_id}), No username provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No username provided."})
            return

        information = api.account.get(request["Data"]["Username"], self.database)

        if information is None:
            utils.server_print("Handler Error", f"Request ({request_id}), Invalid username.")
            client.send_response(rid, 404, "Not Found", {"Msg": "Invalid username."})
            return

        lobby: Lobby = client.get_data("lobby")
        client_to_ban: Client = lobby.get_client(request["Data"]["Username"])

        if client_to_ban is None:
            utils.server_print("Handler Error", f"Request ({request_id}), User to ban isn't in lobby.")
            client.send_response(rid, 404, "Not Found", "User to ban isn't in lobby.")

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        lobby.ban_client(client_to_ban)
        utils.server_print("Server",
                           f"Request ({request_id}), Client {request['Data']['Username']} Baned the lobby {lobby.code}.")
        client_to_ban.push_notification("Lobby_Ban", {"Msg": "You have been Baned from the lobby."})
        client.send_response(rid, 200, "OK", {"Msg": "User Baned."})

        for c in lobby.players + lobby.spectators:
            if c is not client:
                c.push_notification("Use_Left_Lobby",
                                    {"Username": client_to_ban.get_data("username"), "Role": "players"})

    @staticmethod
    def handle_start_game(client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Start lobby game.
        """
        utils.server_print("Handle", f"Request ({request_id}), identified as Start Game from " + str(client.address) + ".")

        # check if the token exists
        if "Token" not in request or request["Token"] != client.get_data("token"):
            utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
            return

        lobby: Lobby = client.get_data("lobby_info")

        if lobby is None:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} isn't in lobby.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User isn't in lobby."})
            return

        if client is not lobby.owner:
            utils.server_print("Handler Error",
                               f"Request ({request_id}), User {client.get_data('username')} isn't the owner of lobby {lobby.code}.")
            client.send_response(rid, 409, "Conflict", {"Msg": "User isn't the owner of lobby."})
            return

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        client.send_response(rid, 200, "OK", {"Msg": "Lobby game started.", "Board": lobby.puzzle})

        for c in lobby.players + lobby.spectators:
            if c is not client:
                c.push_notification("Game_Started", {"board": lobby.puzzle})

        utils.server_print("Server", f"Request ({request_id}), Game started on lobby {lobby.code}.")

    def handle_add_friend(self, client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Add a friend to the user.
        """
        utils.server_print("Handler",
                           f"Request ({request_id}), identified as Add Friend from " + str(client.address) + ".")

        # check if the token exists
        if "Token" not in request or request["Token"] != client.get_data("token"):
            utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
            return

        if "Username" not in request["Data"]:
            utils.server_print("Handler Error", f"Request ({request_id}), No username provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No username provided."})
            return

        information = api.account.get(request["Data"]["Username"], self.database)

        if information is None:
            utils.server_print("Handler Error", f"Request ({request_id}), Invalid username.")
            client.send_response(rid, 404, "Not Found", {"Msg": "Invalid username."})
            return

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        api.friend.add_friend(client.get_data("username"), request["Data"]["Username"], self.database)
        client.send_response(rid, 200, "OK", {"Msg": "Friend request sent."})

        if request["Data"]["Username"] in self.logged_clients:
            self.logged_clients[request["Data"]["Username"]].push_notification("Friend_Request", {
                "Username": client.get_data("username")})

        utils.server_print("Server", f"Request ({request_id}), Friend Request Sent.")

    def handle_accept_friend(self, client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Accept a friend request.
        """
        utils.server_print("Handler",
                           f"Request ({request_id}), identified as Accept Friend Request from " + str(client.address) + ".")

        # check if the token exists
        if "Token" not in request or request["Token"] != client.get_data("token"):
            utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
            return

        if "Username" not in request["Data"]:
            utils.server_print("Handler Error", f"Request ({request_id}), No username provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No username provided."})
            return

        information = api.account.get(request["Data"]["Username"], self.database)

        if information is None:
            utils.server_print("Handler Error", f"Request ({request_id}), Invalid username.")
            client.send_response(rid, 404, "Not Found", {"Msg": "Invalid username."})
            return

        # check if the user sent a request already.
        friend_list = api.friend.get_friend_list(client.get_data("username"), self.logged_clients, self.database)[1]

        if request["Data"]["Username"] in friend_list:
            utils.server_print("Handler Error", f"Request ({request_id}), No Friend Request")
            client.send_response(rid, 404, "Not Found", {"Msg": "No friend request."})
            return

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        api.friend.accept_friend(request["Data"]["Username"], client.get_data("username"), self.database)
        client.send_response(rid, 200, "OK", {"Msg": "Friend request accepted."})

        self.logged_clients[request["Data"]["Username"]].push_notification("Friend_Request_Accepted", {"Username": client.get_data("username")})

        utils.server_print("Server", f"Request ({request_id}), Friend Request Accepted.")

    def handle_reject_friend(self, client: Client, request: dict, rid: int, request_id: int) -> None:
        """
        Reject friend request.
        """
        utils.server_print("Handler",
                           f"Request ({request_id}), identified as Reject Friend Request from " + str(
                               client.address) + ".")

        # check if the token exists
        if "Token" not in request or request["Token"] != client.get_data("token"):
            utils.server_print("Handler Error", f"Request ({request_id}), No Token provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No Token provided."})
            return

        if "Username" not in request["Data"]:
            utils.server_print("Handler Error", f"Request ({request_id}), No username provided.")
            client.send_response(rid, 400, "Bad Request", {"Msg": "No username provided."})
            return

        information = api.account.get(request["Data"]["Username"], self.database)

        if information is None:
            utils.server_print("Handler Error", f"Request ({request_id}), Invalid username.")
            client.send_response(rid, 404, "Not Found", {"Msg": "Invalid username."})
            return

        # check if the user sent a request already.
        friend_list = api.friend.get_friend_list(client.get_data("username"), self.logged_clients, self.database)[1]

        if request["Data"]["Username"] in friend_list:
            utils.server_print("Handler Error", f"Request ({request_id}), No Friend Request")
            client.send_response(rid, 404, "Not Found", {"Msg": "No friend request."})
            return

        utils.server_print("Handler", f"Request ({request_id}), Request passed all checks.")

        api.friend.reject_friend(request["Data"]["Username"], client.get_data("username"), self.database)
        client.send_response(rid, 200, "OK", {"Msg": "Friend request rejected."})

        self.logged_clients[request["Data"]["Username"]].push_notification("Friend_Request_Accepted",
                                                                           {"Username": client.get_data("username")})

        utils.server_print("Server", f"Request ({request_id}), Friend Request Rejected.")

    # -- User authentication token generator --

    def generate_auth_token(self):
        """
        generate an auth token to the user.
        """
        token = "".join([random.choice(string.hexdigits) for _ in range(32)])

        while token in self.tokens:
            token = "".join([random.choice(string.hexdigits) for _ in range(32)])

        return token

    # -- User Logout --

    def disconnect_user(self, client: Client):
        """
        Disconnect the client from the server in a safe way.
        :param client: The client to disconnect.
        """

        # remove client, client token from list
        self.clients.remove(client)
        if client.get_data("token") is not None:
            self.tokens.remove(client.get_data("token"))
            api.account.update_logout(client.get_data("username"), self.database)

        lobby = client.get_data("lobby_info")
        if lobby is not None:
            role, success = lobby.remove_client(client)

            if success:
                utils.server_print("Lobby Manager", f"Removing {client.get_data('username')} from lobby {lobby.code}.")

                for c in lobby.players + lobby.spectators:
                    c.push_notification("User_Left_Lobby", {"Username": client.get_data("username"), "Role": role})

        utils.server_print("Server", f"Client {client.get_data('username')} disconnected.")

    # -- Server running status --

    def start_socket(self) -> None:
        """
        Start the server socket for incoming connections.
        """
        # start listening for incoming connection from clients.
        self.server_socket.listen()

        # set the running variable to true and start the main loop.
        self.__running = True

        utils.server_print("Status", f"Server is running on {self.address}:{self.port} using {'Official' if self.db_profile == 1 else 'Test'} db.")

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
        utils.server_print("Server", "Server closed.")

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
    # parse the arguments from running with this format: Server\ServerSocket.py --host %HOST% --port %PORT% --database %STATUS%
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="127.0.0.1", help="The host address of the server.")
    parser.add_argument("--port", type=int, default=8080, help="The port of the server.")
    parser.add_argument("--database", type=int, default=0, help="The database status.")
    args = parser.parse_args()
    server = ServerSocket(args.host, args.port, args.database)
    server.start_socket()
