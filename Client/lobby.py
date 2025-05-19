import datetime

import default


class Lobby:
    def __init__(self, owner: str, code: str, started: bool, max_players: int, players: list, spectators: int, players_colors: list, lobby_role: str):
        """
        Store all the lobby data.
        :param owner: The owner of the lobby.
        :param code: The lobby code.
        :param started: The lobby started status.
        :param max_players: The maximum number of players in the lobby.
        :param players: The players in the lobby.
        :param spectators: The number of spectators in the lobby.
        :param players_colors: The colors of the players in the lobby.
        :param lobby_role: The role of this user in the lobby.
        """
        self.owner = owner
        self.code = code
        self.started = started
        self.max_players = max_players
        self.ending_date = None
        self.players = players
        self.spectators = spectators
        self.players_colors = players_colors
        self.lobby_role = lobby_role
        self.leaderboard = []
        self.lobby_board = None
        self.back_to_lobby_action = False

        # chat
        self.chat: list[Message] = []

    @staticmethod
    def from_dict(lobby: dict, user_role: str):
        """
        Create a lobby object from a dictionary.
        :param lobby: The lobby dictionary.
        :param user_role: The role of the user in the lobby.
        :return: The created lobby object.
        """
        return Lobby(lobby["owner"], lobby["code"], lobby["started"], lobby["max_players"], lobby["players"], lobby["spectators"], lobby["players_colors"], user_role)

    def set_ending_date(self, ending_date: str):
        """
        Set the ending date of the lobby.
        :param ending_date: The ending date of the lobby.
        """
        self.ending_date = datetime.datetime.strptime(ending_date, "%Y-%m-%d %H:%M:%S")

    def to_dict(self):
        """
        Convert the lobby object to a dictionary.
        """
        return {
            "code": self.code,
            "owner": self.owner,
            "started": self.started,
            "max_players": self.max_players,
            "players": self.players,
            "spectators": self.spectators,
            "players_colors": self.players_colors
        }


class Message:
    def __init__(self, username: str, message: str, time: str):
        """
        Store the message data.
        :param username: The username of the sender.
        :param message: The message content.
        """
        self.username = username
        self.message = message
        self.time = datetime.datetime.strptime(time, "%H:%M:%S")