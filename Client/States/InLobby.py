import pygame
import os
import pyperclip

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
        self.data_checksum = None
        self.__init_vars()

    def __init_vars(self, *args, **kwargs) -> None:
        self.data = self.client.get_data('lobby_info')
        self.data_checksum = self.client.create_checksum(self.data)
        self.navbar = MonoBehaviour(pygame.Vector2(127, 45), pygame.Vector2(40, 40), (2, 2, 2), border_radius=10)
        self.menu_icon = Image(os.path.join("Images", "Menu.png"), pygame.Vector2(24, 24), pygame.Vector2(self.navbar.position.x + 20, self.navbar.position.y + 10))
        self.friend_icon = Image(os.path.join("Images", "Person.png"), pygame.Vector2(20, 20), self.menu_icon.position + pygame.Vector2(24 + 20, 3))
        self.title = Text(f"{self.data['owner']}'s Lobby", "SemiBold", 50, pygame.Vector2(80, 133), (255, 255, 255), top_left_mode=True)
        self.code_display_background = MonoBehaviour(pygame.Vector2(195, 55), self.title.position + pygame.Vector2(self.title.text_surface.get_width() + 35, 10), (2, 2, 2), border_radius=10)
        self.code_display = Text(self.data["code"], "Regular", 28, self.code_display_background.position + pygame.Vector2(25, self.code_display_background.size[1] / 2), (182, 182, 182), left_mode=True)
        self.code_copy_icon = Image(os.path.join("Images", "Copy.png"), pygame.Vector2(20, 22), self.code_display_background.position + pygame.Vector2(25 + self.code_display.text_surface.get_width() + 24, 16))
        self.number_of_players = Text(f"{len(self.data['players'])} / {self.data['max_players']} Players", "Regular", 24, self.title.position + pygame.Vector2(0, self.title.text_surface.get_size()[1] + 30), (226, 226, 226), top_left_mode=True)
        self.left_image = Image(os.path.join("Images", "LobbyImage.png"), pygame.Vector2(1234, 1080), pygame.Vector2(self.screen.get_width() - 1234, 0))
        self.players_cards = []
        self.init_players()

    def update(self, dt: float, events: list, *args, **kwargs):
        if self.code_copy_icon.update(events):
            pyperclip.copy(self.data["code"])

        # check if data has changed, if not don't update.

        new_data_checksum = self.client.create_checksum(self.data)
        if new_data_checksum == self.data_checksum:
            return

        self.data_checksum = new_data_checksum
        self.number_of_players.update_text(f"{len(self.data['players'])} / {self.data['max_players']} Players")
        self.init_players()

    def init_players(self):
        for i, player in enumerate(self.data['players']):
            color = COLOR_NAMES[str(self.data["players_colors"][i])]
            self.players_cards.append(self.init_player_card(player, color, i, self.number_of_players.position + pygame.Vector2(20, self.number_of_players.text_surface.get_height() + 50)))

    def init_player_card(self, username: str, color: str, index: int, base: pygame.Vector2) -> list:
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
        player_name = Text(username, "Regular", 16, card_background.position + pygame.Vector2(25 + 22 + NAME_ICON_GAP, card_background.size[1] / 2), (226, 226, 226), left_mode=True)

        icon = None

        if self.data["owner"] == username:
            icon = Image(os.path.join("Images", "PlayerCard", "Icons",  "Owner.png"), pygame.Vector2(22, 22), card_background.position + pygame.Vector2(BACKGROUND_PADDING_LEFT, 17))
        else:
            icon = Image(os.path.join("Images", "PlayerCard", "Icons", color + ".png"), pygame.Vector2(22, 22), card_background.position + pygame.Vector2(BACKGROUND_PADDING_LEFT, 17))

        return [card_background, icon, player_name]

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
