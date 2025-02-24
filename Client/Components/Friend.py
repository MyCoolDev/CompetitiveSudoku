from Client.default import *
import os

from Client.Components.MonoBehaviour import MonoBehaviour
from Client.Components.Text import Text
from Client.Components.Image import Image

class Friend:
    def __init__(self, friend_information: dict):
        self.username = friend_information["username"]
        self.last_login = friend_information["last_login"]
        self.playtime = friend_information["playtime"]
        self.games_played = friend_information["games_played"]
        self.games_won = friend_information["games_won"]
        self.account_level = friend_information["account_level"]
        self.status = friend_information.get("status", None)

    def to_renderable_list(self, position: Vector2, extended=False) -> list:
        """
        Convert the friend information to a list of Components.
        The list represents a player card for render.
        :return: The player card, list of Components.
        """
        card = [
            MonoBehaviour(Vector2(484, 76), position, (22, 22, 22), border_radius=10),
            # profile picture, size - 42x42, position from left 40, top 17, gap with username 35.
            Text(self.username, "Medium", 22, position + Vector2(40 + 42 + 35, 76 / 2), (220, 220, 220), left_mode=True),
            Image(os.path.join("Images", "Arrow.png"), Vector2(22, 19), position + Vector2(484 - 40 - 22, 76 / 2 - 19 / 2))
        ]

        # here we will add the extended information.
        pass

        return card
