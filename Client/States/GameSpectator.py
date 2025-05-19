import datetime

import pygame

from Client.States.BaseState import BaseState
from Client.client import ClientSocket
from Client.Components.default_comp import *
from Client.default import *
from Client.lobby import Message

class GameSpectator(BaseState):
    def __init__(self, screen: pygame.Surface, client: ClientSocket):
        super().__init__(screen, client)

        # change the screen name
        self.leaderboard_rating = None
        pygame.display.set_caption("Competitive Sudoku - Spectating (" + self.client.lobby.code + ") - " + self.client.get_data("username"))

        self.__init_vars()

    def __init_vars(self, *args, **kwargs) -> None:
        self.puzzle = self.client.lobby.lobby_board

        self.leaderboard = MonoBehaviour(Vector2(640, 790), Vector2((self.screen.get_width() - 640) / 2, (self.screen.get_height() - 790) / 2), (81, 81, 81), border_radius=20)
        self.leaderboard_title = Text("Leaderboard", "Medium", 36,  + Vector2(self.leaderboard.position.x + self.leaderboard.size.x / 2, self.leaderboard.position.y - 30), (255, 255, 255), top_mode=True)
        self.leaderboard_rating = [(Text(f"{player[0]}", "Regular", 14, Vector2(self.leaderboard.position.x + 24,
                                                                                self.leaderboard_title.position.y + self.leaderboard_title.text_surface.get_height() + 20 + i * 28),
                                         ((251, 175, 55) if i == 0 else (201, 212, 203) if i == 1 else (
                                             187, 137, 121) if i == 2 else (218, 218, 218)), top_left_mode=True),
                                    Text(f"{player[1]}", "Regular", 14,
                                         Vector2(self.leaderboard.position.x + self.leaderboard.size.x - 24,
                                                 self.leaderboard_title.position.y + self.leaderboard_title.text_surface.get_height() + 20 + i * 28),
                                         ((251, 175, 55) if i == 0 else (201, 212, 203) if i == 1 else (
                                             187, 137, 121) if i == 2 else (218, 218, 218)), top_mode=True)) for
                                   i, player in enumerate(self.client.lobby.leaderboard)]
        # chat
        self.chat = MonoBehaviour(Vector2(383, 550),
                                  Vector2(self.screen.get_width() - 45 - 383, self.screen.get_height() - 55 - 550),
                                  (81, 81, 81), border_radius=15)
        self.chat_title = Text("Chat", "Medium", 16,
                               Vector2(self.chat.position.x + self.chat.size.x / 2, self.chat.position.y - 30),
                               (255, 255, 255), top_mode=True)
        self.chat_input = TextBox(Vector2(272, 56),
                                  Vector2(self.chat.position.x + 20, self.chat.position.y + self.chat.size.y - 10 - 56),
                                  (105, 105, 105), "Enter Message", "Regular", 16, (193, 193, 193), padding_left=20,
                                  border_radius=10)
        self.chat_input_send_button_bg = MonoBehaviour(Vector2(55, 55),
                                                       self.chat_input.position + Vector2(self.chat_input.size.x + 15,
                                                                                          0), (69, 72, 233),
                                                       border_radius=10)
        self.chat_input_send_button_icon = Image(os.path.join("Images", "Arrow.png"), Vector2(22, 19),
                                                 self.chat_input_send_button_bg.position + self.chat_input_send_button_bg.size / 2,
                                                 rotate=-90, centered=True)

        self.return_to_lobby_button = Button(Vector2(200, 50), Vector2(45, 35), (69, 72, 233), "Back to Lobby", "Regular", 16, (255, 255, 255), border_radius=10, top_left_mode=True)

        # setting some mouse cursors
        self.mouse_cursor["HAND"] = [self.chat_input_send_button_bg, self.chat_input_send_button_icon, self.return_to_lobby_button]
        self.mouse_cursor["IBEAM"] = [self.chat_input]

    def update_leaderboard(self):
        """
        Update the leaderboard with the current players scores.
        """
        self.leaderboard_rating.clear()
        self.leaderboard_rating = [(Text(f"{player[0]}", "Regular", 32, Vector2(self.leaderboard.position.x + 24,
                                                                                self.leaderboard_title.position.y + self.leaderboard_title.text_surface.get_height() + 20 + i * 28),
                                         ((251, 175, 55) if i == 0 else (201, 212, 203) if i == 1 else (
                                         187, 137, 121) if i == 2 else (218, 218, 218)), top_left_mode=True),
                                    Text(f"{player[1]}", "Regular", 32,
                                         Vector2(self.leaderboard.position.x + self.leaderboard.size.x - 24,
                                                 self.leaderboard_title.position.y + self.leaderboard_title.text_surface.get_height() + 20 + i * 28),
                                         ((251, 175, 55) if i == 0 else (201, 212, 203) if i == 1 else (
                                         187, 137, 121) if i == 2 else (218, 218, 218)), top_mode=True)) for
                                   i, player in enumerate(self.client.lobby.leaderboard)]

    def update(self, dt: float, events: list, *args, **kwargs):
        super().update(dt, events, *args, **kwargs)
        self.chat_input.update(dt, events)
        self.update_leaderboard()
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                if self.chat_input_send_button_bg.is_collide(mouse_pos):
                    if not self.chat_input.is_default_content_presented:
                        self.client.send_request("Chat_Message", {"Message": self.chat_input.content})
                        self.client.lobby.chat.append(Message(self.client.get_data("username"), self.chat_input.content, datetime.datetime.now().strftime("%H:%M:%S")))
                        self.client.lobby.chat = self.client.lobby.chat[-4:]
                        self.chat_input.update_text("")

        if not self.client.lobby.started:
            if self.return_to_lobby_button.update(dt, events):
                self.client.set_data("go_to_lobby", True)

    def render(self, *args, **kwargs):
        """
        Render the state.
        :param args:
        :param kwargs:
        :return:
        """
        self.leaderboard.render(self.screen)
        self.leaderboard_title.render(self.screen)
        for player_rating in self.leaderboard_rating:
            player_rating[0].render(self.screen)
            player_rating[1].render(self.screen)

        self.chat.render(self.screen)
        self.chat_title.render(self.screen)
        self.chat_input.render(self.screen)
        self.chat_input_send_button_bg.render(self.screen)
        self.chat_input_send_button_icon.render(self.screen)

        # get the last 5 messages from the chat
        next_pos = self.chat.position + Vector2(25, 30)
        for i, message in enumerate(self.client.lobby.chat[-4:]):
            author = Text(f"{message.username}", "Regular", 12, next_pos, (255, 255, 255), top_left_mode=True)
            msg = Text(f"{message.message}", "Regular", 12,
                       author.position + Vector2(25, author.text_surface.get_height() + 25), (255, 255, 255),
                       top_left_mode=True)
            box = MonoBehaviour(Vector2(25 * 2 + msg.text_surface.get_width(), 20 * 2 + msg.text_surface.get_height()),
                                author.position + Vector2(0, author.text_surface.get_height() + 5), (105, 105, 105),
                                border_radius=10)
            box.render(self.screen)
            author.render(self.screen)
            msg.render(self.screen)
            next_pos = box.position + Vector2(0, box.size.y + 20)

        if not self.client.lobby.started:
            self.return_to_lobby_button.render(self.screen)

