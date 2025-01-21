import pygame
import random
import string

from Server.SudokuBoard import SudokuBoard
from ClientInterface import Client
import utils


class Lobby:
    def __init__(self, owner: Client, code: str):
        """
        The lobby data structure to store all the data and do some actions on it.
        """
        self.board = SudokuBoard(3)

        self.code = code

        self.MAX_PLAYERS = 6

        self.players = [owner]
        self.spectators = []
        self.started = False
        self.owner = owner
        self.owner.set_data("lobby", self)

    def register_client(self, client: Client):
        """
        Add a client to the lobby. (Implementation of join lobby or create lobby)
        :param client: client to add
        """
        if len(self.players) < self.MAX_PLAYERS:
            self.players.append(client)
        else:
            self.spectators.append(client)

    def remove_client(self, client: Client) -> bool:
        """
        Remove a client from the lobby. (Implementation of leave lobby)
        :param client: Client to remove.
        :return: True if the client was removed, False otherwise.
        """
        if client != self.owner:
            if client in self.players:
                self.players.remove(client)
                client.set_data("lobby", None)
                return True
            if client in self.spectators:
                self.spectators.remove(client)
                client.set_data("lobby", None)
                return True

        return False

    def get_client(self, username) -> Client or None:
        for client in self.players:
            if client.get_data("username") == username:
                return client

        for client in self.spectators:
            if client.get_data("username") == username:
                return client

        return None

    def delete_lobby(self) -> bool:
        """
        Delete the lobby. (Implementation of delete lobby)
        :return: True if the lobby was deleted, False otherwise.
        """
        pass

    def __repr__(self):
        return {
            "max_players": self.MAX_PLAYERS,
            "players": [x.get_data("username") for x in self.players],
            "spectators": [x.get_data("username") for x in self.spectators],
            "started": self.started,
            "owner": self.owner.get_data("username"),
            "code": self.code
        }


class LobbyManager:
    def __init__(self):
        """
        Manage all the lobbies
        """
        self.all_lobbies = {}

    def create_lobby(self, owner: Client) -> Lobby:
        """
        Create a new lobby.
        :param owner: The owner of the lobby.
        :return: The created lobby object.
        """
        utils.server_print("Lobby Manager", "Creating new lobby")
        new_lobby = Lobby(owner, self.generate_code())

        # add the new lobby to all the lobbies for auths.
        self.all_lobbies[new_lobby.code] = new_lobby

        return new_lobby

    def generate_code(self) -> str:
        """
        Generate a random code for a lobby.
        :return: 6 digit random code.
        """
        code = "".join([random.choice(string.digits) for _ in range(6)])

        while code in self.all_lobbies:
            code = "".join([random.choice(string.digits) for _ in range(6)])

        return code
