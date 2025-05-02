import pygame
from Client.client import ClientSocket

from Client.Components.TextBox import TextBox


class SudokuBoard:
    def __init__(self, screen: pygame.Surface, board, client: ClientSocket):
        self.screen = screen
        self.board = board
        self.size = 910
        self.files = [
            [TextBox(pygame.Vector2(self.size / 9, self.size / 9), pygame.Vector2((self.screen.get_width() - self.size) / 2 + 100 * index_file + (5 if index_file % 3 == 0 and index_file != 0 else 0), (self.screen.get_height() - self.size) / 2 + 100 * index_line + (5 if index_line % 3 == 0 and index_line != 0 else 0)), (81, 81, 81), str(number) if number != 0 else "", "Regular", 24, (255, 255, 255), text_left_mode=False, text_centered=True, num_only=True) for index_file, number in enumerate(line)] for index_line, line in enumerate(board)
        ]

        self.client = client

    def update(self, dt, events):
        for row, line in enumerate(self.files):
            for column, file in enumerate(line):
                if file.default_content == "":
                    key = file.update_board_square(dt, events)
                    if key is not None:
                        response = self.client.send_request("game_move", {"Move": {"row": row, "column": column, "value": int(key)}})
                        if response["StatusCode"] == 200:
                            file.update_text(key)
                            file.lock = True
                        else:
                            file.text.update_color((255, 0, 0))
                            file.update_text(key)
                            file.lock = False

    def render(self):
        for line in self.files:
            for file in line:
                file.render(self.screen)
