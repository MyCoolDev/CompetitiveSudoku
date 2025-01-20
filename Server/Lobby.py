import pygame
import random
import string

from Server.SudokuBoard import SudokuBoard
from ClientInterface import Client
import utils


class Lobby:
    def __init__(self, name: str, description: str, owner: Client, code: str):
        """
        The lobby data structure to store all the data and do some actions on it.
        """
        self.name = name
        self.description = description
        self.board = SudokuBoard(3)

        self.MAX_PLAYERS = 6

        self.players = [owner]
        self.spectators = []
        self.started = False
        self.owner = owner
        self.owner.lobby = self

    def register_client(self, client: Client):
        if len(self.players) < self.MAX_PLAYERS:
            self.players.append(client)
        else:
            self.spectators.append(client)


class LobbyManager:
    def __init__(self):
        """
        Manage all the lobbies
        """
        self.all_lobbies = {}

    def create_lobby(self, name: str, description: str, owner: Client):
        utils.server_print("Lobby Manager", "Creating new lobby")
        Lobby(name, description, owner, self.generate_code())

    def generate_code(self):
        token = "".join([random.choice(string.hexdigits) for _ in range(32)])

        # while token in self.:
        #    token = "".join([random.choice(string.hexdigits) for _ in range(32)])

        return token
