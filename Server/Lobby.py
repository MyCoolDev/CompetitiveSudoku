import random
import datetime
import string
import threading

import utils
from ClientInterface import Client
from Server.SudokuBoard import SudokuGenerator


class Lobby:
    def __init__(self, owner: Client, code: str, max_time=60 * 15):
        """
        The lobby data structure to store all the data and do some actions on it.
        """
        self.board = SudokuGenerator()
        self.solution, self.puzzle = self.board.generate_puzzle("medium")
        self.puzzle_size = len(SudokuGenerator.get_empty_cells(self.puzzle))

        self.code = code

        self.MAX_PLAYERS = 6

        self.players = [owner]
        self.spectators = []
        self.bans = []
        self.started = False
        self.owner = owner
        self.owner.set_data("lobby", self)
        self.players_colors = [(255, 90, 90), (96, 90, 255), (255, 230, 90), (90, 255, 134), (66, 255, 211), (227, 90, 255)]
        self.__shuffle_colors()

        self.players_data = {}

        self.BASE_EXP = 10000

        # player data structure
        """
        {
            "username": {
                "color": (r, g, b),
                "score": 0,
                "current_moves": 0,
                "mistakes": 0,
                "moves": [(x, y), ...]
            },
            ...
        }
        """

        # game vars
        self.game_started = False
        self.MAX_TIME = max_time
        self.ending_time = None
        self.leaderboard = []   # (username, score)
        self.winner = None

    def register_client(self, client: Client) -> (str, bool):
        """
        Add a client to the lobby. (Implementation of join lobby or create lobby)
        :param client: client to add
        :return: the role and the success of the registration.
        """
        if client not in self.bans:
            if len(self.players) < self.MAX_PLAYERS:
                self.players.append(client)
                return "players", True
            else:
                self.spectators.append(client)
                return "spectators", True

        return "", False

    def remove_client(self, client: Client) -> (str, bool):
        """
        Remove a client from the lobby. (Implementation of leave lobby)
        :param client: Client to remove.
        :return: True if the client was removed, False otherwise. The role of the client will be returned too.
        """
        if client in self.players:
            self.players.remove(client)
            client.set_data("lobby_info", None)
            return "players", True

        if client in self.spectators:
            self.spectators.remove(client)
            client.set_data("lobby_info", None)
            return "spectators", True

    def ban_client(self, client: Client) -> bool:
        if self.remove_client(client):
            self.bans.append(client)
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

    def __shuffle_colors(self):
        """
        Shuffle the colors set of the players to randomize the colors.
        """
        self.players_colors = random.sample(self.players_colors, len(self.players_colors))

    # --- Game ---

    def run_game(self):
        """
        Run the game as long as the timelimit hasn't been reached, the players haven't finished the game and the players are still in the lobby / game (lobby exists).
        """
        while self.check_timer() > 0 and len(self.players) > 0 and self.winner is None:
            pass

    def start_game(self) -> None:
        """
        Start the game by init the game vars and run the game in a separate thread.
        """
        self.game_started = True

        # Start the timer
        self.ending_time = datetime.datetime.now() + datetime.timedelta(seconds=self.MAX_TIME)

        for index, player in enumerate(self.players):
            self.players_data[player.get_data("username")] = {
                "color": self.players_colors[index],
                "score": 0,
                "mistakes": 0,
                "moves": [],
                "game_exp": 0
            }

        # Run the game in a separate thread.
        threading.Thread(target=self.run_game).start()

    def end_game(self):
        pass

    def player_move(self, client: Client, x: int, y: int, value: int) -> bool:
        """
        Check if the move is valid and update the player data.
        """
        username = client.get_data("username")

        if self.solution[x][y] != value:
            self.players_data[username]["mistakes"] += 1
            print("test")
            return False

        # get the delta time between the starting time and the move in seconds
        move_time = (datetime.timedelta(seconds=self.MAX_TIME) - (self.ending_time - datetime.datetime.now())).seconds

        self.players_data[username]["moves"] += (x, y)
        self.players_data[username]["game_exp"] += round(self.BASE_EXP / move_time)
        self.players_data[username]["score"] = len(self.players_data[username]["moves"]) / self.puzzle_size
        self.update_leaderboard()
        return True

    # def update_score(self, client):
    #     self.players_data[username]

    def check_timer(self) -> int:
        """
        check the time left for the game.
        :return: the time left for the game in seconds.
        """
        return (self.ending_time - datetime.datetime.now()).seconds

    def update_leaderboard(self) -> None:
        """
        get the updated leaderboard and send it to everyone on the lobby.
        """
        self.leaderboard = self.get_leaderboard()
        for player in self.players + self.spectators:
            player.push_notification("Leaderboard", {"Leaderboard": self.leaderboard})

    def get_leaderboard(self) -> list:
        """
        Get the leaderboard of the game.
        :return: The leaderboard of the game.
        """
        self.leaderboard = sorted(self.players_data.items(), key=lambda x: x[1]["score"], reverse=True)
        return self.leaderboard

    def __repr__(self):
        return {
            "code": self.code,
            "owner": self.owner.get_data("username"),
            "started": self.started,
            "max_players": self.MAX_PLAYERS,
            "players": [x.get_data("username") for x in self.players],
            "spectators": len(self.spectators),
            "players_colors": self.players_colors
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
