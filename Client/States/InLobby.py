import pygame
import os
import pyperclip
import copy

from Client.States.BaseState import BaseState
from Client.Components.Text import Text
from Client.Components.Button import Button
from Client.Components.TextBox import TextBox
from Client.Components.Image import Image
from Client.Components.MonoBehaviour import MonoBehaviour
from Client.client import ClientSocket

COLOR_NAMES = {
    "[255, 90, 90]": "Red",
    "[96, 90, 255]": "Blue",
    "[255, 230, 90]": "Yellow",
    "[90, 255, 134]": "Green",
    "[66, 255, 211]": "Aqua",
    "[227, 90, 255]": "Purple"
}

class InLobby(BaseState):
    def __init__(self, screen: pygame.Surface, client: ClientSocket):
        super().__init__(screen, client)
        self.join_lobby = pygame.mixer.Sound(os.path.join("Sounds", "Join.wav"))
        self.join_lobby.set_volume(0.5)
        self.data_checksum = None
        self.old_data = None
        self.become_a_player_button = None
        self.__init_vars()
        self.join_lobby.play()

    def __init_vars(self, *args, **kwargs) -> None:
        self.data = self.client.get_data('lobby_info')
        self.old_data = copy.deepcopy(self.data)
        self.data_checksum = self.client.create_checksum(self.data)
        self.players_cards = []

        self.navbar = MonoBehaviour(pygame.Vector2(127, 45), pygame.Vector2(40, 40), (2, 2, 2), border_radius=10)
        self.menu_icon = Image(os.path.join("Images", "Menu.png"), pygame.Vector2(24, 24), pygame.Vector2(self.navbar.position.x + 20, self.navbar.position.y + 10))
        self.friend_icon = Image(os.path.join("Images", "Person.png"), pygame.Vector2(20, 20), self.menu_icon.position + pygame.Vector2(24 + 20, 3))

        self.title = Text(f"{self.data['owner']}'s Lobby", "SemiBold", 50, pygame.Vector2(80, 133), (255, 255, 255), top_left_mode=True)
        self.code_display_background = MonoBehaviour(pygame.Vector2(195, 55), self.title.position + pygame.Vector2(self.title.text_surface.get_width() + 35, 10), (2, 2, 2), border_radius=10)
        self.code_display = Text(self.data["code"], "Regular", 28, self.code_display_background.position + pygame.Vector2(25, self.code_display_background.size[1] / 2), (182, 182, 182), left_mode=True)
        self.code_copy_icon = Image(os.path.join("Images", "Copy.png"), pygame.Vector2(20, 22), self.code_display_background.position + pygame.Vector2(25 + self.code_display.text_surface.get_width() + 24, 16))

        self.number_of_players = Text(f"{len(self.data['players'])} / {self.data['max_players']} Players", "Regular", 24, self.title.position + pygame.Vector2(0, self.title.text_surface.get_size()[1] + 30), (226, 226, 226), top_left_mode=True)
        self.init_players()

        self.left_image = Image(os.path.join("Images", "LobbyImage.png"), pygame.Vector2(1234, 1080), pygame.Vector2(self.screen.get_width() - 1234, 0))
        self.spectator_icon = Image(os.path.join("Images", "Spectator.png"), pygame.Vector2(18, 14), pygame.Vector2(70, self.screen.get_height() - 40))
        self.spectator_count = Text(str(self.data["spectators"]), "Regular", 22, self.spectator_icon.position + pygame.Vector2(self.spectator_icon.size[0] + 10, self.spectator_icon.size[1] / 2), (255, 255, 255), left_mode=True)

        # setting some mouse cursors
        self.mouse_cursor["HAND"] = [self.menu_icon, self.code_copy_icon]

    def update(self, dt: float, events: list, *args, **kwargs):
        super().update(dt, events, args, kwargs)

        if self.code_copy_icon.update(events):
            pyperclip.copy(self.data["code"])

        # check if data has changed, if not don't update.

        new_data_checksum = self.client.create_checksum(self.data)
        if new_data_checksum == self.data_checksum:
            return

        # update some staff
        if len(self.data["players"]) != len(self.old_data["players"]):
            self.number_of_players.update_text(f"{len(self.data['players'])} / {self.data['max_players']} Players")
            self.init_players()

            if len(self.data["players"]) > len(self.old_data["players"]):
                self.join_lobby.play()

        self.data_checksum = new_data_checksum
        self.old_data = copy.deepcopy(self.data)

    def init_players(self):
        """
        init all the players, add them into players_cards list for future render.
        """
        colors = self.data["players_colors"]
        for i, player in enumerate(self.data['players']):
            color = COLOR_NAMES[str(colors[i])]
            self.players_cards.append(self.init_player_card(player, color, i, self.number_of_players.position + pygame.Vector2(20, self.number_of_players.text_surface.get_height() + 50)))

        if len(self.players_cards) < 6 and self.client.get_data("Lobby_Role") == "spectators":
            self.become_a_player_button = self.init_player_card("Become A Player", COLOR_NAMES[str(colors[len(self.data["players"])])], len(self.data["players"]), self.number_of_players.position + pygame.Vector2(20, self.number_of_players.text_surface.get_height() + 50), True)
        else:
            self.become_a_player_button = None

    def init_player_card(self, username: str, color: str, index: int, base: pygame.Vector2, is_not_player=False) -> list:
        """
        init a player card, with positions using index.
        :param username: the username.
        :param color: the color name of the player.
        :param index: the index of the player (for position).
        :param base: the base position (layout base position).
        :return: the player card (list of all the elements for render).
        """

        NAME_ICON_GAP = 15
        BACKGROUND_PADDING_LEFT = 25
        CARDS_GAP = 30

        card_background = Image(os.path.join("Images", "PlayerCard", color + ".png"), pygame.Vector2(467, 60), base + pygame.Vector2(0, (60 + CARDS_GAP) * index))

        player_name = None
        icon = None

        if self.data["owner"] == username:
            icon = Image(os.path.join("Images", "PlayerCard", "Icons",  "Owner.png"), pygame.Vector2(22, 22), card_background.position + pygame.Vector2(BACKGROUND_PADDING_LEFT, 17))
        elif not is_not_player:
            icon = Image(os.path.join("Images", "PlayerCard", "Icons", color + ".png"), pygame.Vector2(22, 22), card_background.position + pygame.Vector2(BACKGROUND_PADDING_LEFT, 17))

        if is_not_player:
            player_name = Text(username, "Regular", 16, card_background.position + pygame.Vector2(BACKGROUND_PADDING_LEFT, card_background.size[1] / 2), (226, 226, 226), left_mode=True)
        else:
            player_name = Text(username, "Regular", 16, card_background.position + pygame.Vector2(25 + 22 + NAME_ICON_GAP, card_background.size[1] / 2), (226, 226, 226), left_mode=True)

        objs = [card_background, icon, player_name]

        if is_not_player:
            return objs

        my_username = self.client.get_data("username")

        if username == my_username:
            obj = Image(os.path.join("Images", "Spectator.png"), pygame.Vector2(21, 16), card_background.position + pygame.Vector2(card_background.size[0] - 25 - 21, 21))
            objs.append(obj)
            self.mouse_cursor["HAND"].append(obj)
        elif self.data["owner"] == my_username:
            obj = Image(os.path.join("Images", "Kick.png"), pygame.Vector2(16, 16), card_background.position + pygame.Vector2(card_background.size[0] - 25 - 16, 21))
            objs.append(obj)
            self.mouse_cursor["HAND"].append(obj)
            obj = Image(os.path.join("Images", "Block.png"), pygame.Vector2(16, 16), objs[-1].position + pygame.Vector2(-15 - 16, 0))
            objs.append(obj)
            self.mouse_cursor["HAND"].append(obj)
            obj = Image(os.path.join("Images", "Spectator.png"), pygame.Vector2(21, 16), objs[-1].position + pygame.Vector2(-15 - 21, 0))
            objs.append(obj)
            self.mouse_cursor["HAND"].append(obj)

        return objs

    def render(self, *args, **kwargs):
        self.navbar.render(self.screen)
        self.menu_icon.render(self.screen)
        self.friend_icon.render(self.screen)
        self.left_image.render(self.screen)
        self.title.render(self.screen)
        self.code_display_background.render(self.screen)
        self.code_display.render(self.screen)
        self.code_copy_icon.render(self.screen)
        self.number_of_players.render(self.screen)

        for card in self.players_cards:
            for element in card:
                element.render(self.screen)

        if self.become_a_player_button is not None:
            for element in self.become_a_player_button:
                element.render(self.screen)

        self.spectator_icon.render(self.screen)
        self.spectator_count.render(self.screen)
