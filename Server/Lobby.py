import pygame
from Server.SudokuBoard import SudokuBoard


class Lobby:
    def __init__(self, name, description):
        """
        The lobby data structure to store all the data and do some actions on it.
        """
        self.name = name
        self.description = description
        self.board = SudokuBoard(3)

        self.players = []
        self.spectators = []
        self.started = False
