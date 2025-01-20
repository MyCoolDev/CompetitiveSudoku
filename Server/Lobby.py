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
        if len(self.players) < self.MAX_PLAYERS:
            self.players.append(client)
        else:
            self.spectators.append(client)

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
        utils.server_print("Lobby Manager", "Creating new lobby")
        return Lobby(owner, self.generate_code())

    def generate_code(self):
        code = "".join([random.choice(string.digits) for _ in range(6)])

        while code in self.all_lobbies:
            code = "".join([random.choice(string.digits) for _ in range(6)])

        return code
