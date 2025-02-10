import pygame

from Client.client import ClientSocket

from Client.Components.MonoBehaviour import MonoBehaviour
from Client.Components.Text import Text
from Client.Components.Button import Button


class FriendList:
    def __init__(self, screen: pygame.Surface, client: ClientSocket):
        self.friends_selection_text = None
        self.friends_selection_bg = None
        self.small_profile_username_position = None
        self.small_profile_friends_count = None
        self.small_profile_username = None
        self.small_profile = None
        self.background = None
        self.client = client
        self.screen = screen
        self.width = 484
        self.init_components()
        self.shown = False

        # the sliding animation
        self.animation_status = False
        self.animation_time = 0.5

    def init_components(self):
        """
        Initialize the components of the friend list display.
        """
        self.background = MonoBehaviour(pygame.Vector2(self.width, self.screen.get_height()), pygame.Vector2(-self.width, 0), (32, 32, 32))
        # small profile box for positioning only, will not be rendered.
        self.small_profile = MonoBehaviour(pygame.Vector2(self.width, 134), self.background.position, (255, 255, 255))
        self.small_profile_username = Text(self.client.get_data("username"), "Medium", 26, pygame.Vector2(0, 0), (255, 255, 255), top_left_mode=True)

        # count all the online friends
        online = 0
        for friend in self.client.friends_information[0]:
            if friend["status"] == "Online":
                online += 1

        self.small_profile_friends_count = Text(f"{len(self.client.friends_information[0])} Friends / {online} Online", "Regular", 16, pygame.Vector2(0, 0), (255, 255, 255), top_left_mode=True)

        # calc the position of the username and the friends count.
        self.__calc_small_profile_username_position()
        self.small_profile_username.update_position(self.small_profile_username_position)
        self.small_profile_friends_count.update_position(self.small_profile_username_position + pygame.Vector2(0, 10))

        # tab selection
        self.friends_selection_bg = MonoBehaviour(pygame.Vector2(self.width / 2, 54), self.small_profile.position + pygame.Vector2(0, self.small_profile.size[1]), (32, 32, 32), border_top_right_radius=10)
        self.friends_selection_text = Text("Friends", "Medium", 16, self.friends_selection_bg.position + pygame.Vector2(self.friends_selection_bg.size[0] / 2, self.friends_selection_bg.size[1] / 2), (255, 255, 255))

    def toggle(self):
        """
        Toggle the friend list display.
        """
        self.shown = not self.shown
        self.animation_status = True

    def __calc_small_profile_username_position(self):
        """
        Calculate the position of the username and friend count (x) of the small profile.
        """
        self.small_profile_username_position = pygame.Vector2(self.small_profile.position.x + 70, (self.small_profile.position.y + self.small_profile.size[1] - (self.small_profile_username.text_surface.get_size()[1] + 10 + self.small_profile_friends_count.text_surface.get_size()[1])) / 2)

    def __update_positions(self):
        """
        Update the positions.
        """
        self.small_profile.position = self.background.position
        self.__calc_small_profile_username_position()
        self.small_profile_username.update_position(self.small_profile_username_position)
        self.small_profile_friends_count.update_position(self.small_profile_username_position + pygame.Vector2(0, self.small_profile_username.text_surface.get_size()[1] + 10))
        self.friends_selection_bg.position = self.small_profile.position + pygame.Vector2(0, self.small_profile.size[1])
        self.friends_selection_text.update_position(self.friends_selection_bg.position + pygame.Vector2(self.friends_selection_bg.size[0] / 2, self.friends_selection_bg.size[1] / 2))

    def update(self, dt: float, events: list):
        """
        Update the friend list display.
        :param dt: the delta time between each frame.
        :param events: the events that are happening in the game.
        """
        if self.animation_status:
            if self.shown and self.background.position.x < 0:
                self.background.position.x += self.width * (dt / self.animation_time)
            elif self.shown and self.background.position.x >= 0:
                self.animation_status = False
                self.background.position.x = 0
                self.small_profile.position.x = self.background.position.x
            elif not self.shown and self.background.position.x > -self.width:
                self.background.position.x -= self.width * (dt / self.animation_time)
            elif self.shown and self.background.position.x <= -self.width:
                self.animation_status = False
                self.background.position.x = -self.width

            self.__update_positions()

    def render(self):
        """
        Render the friend list display.
        """
        self.background.render(self.screen)
        if self.small_profile_username_position.x + self.small_profile_username.text_surface.get_size()[0] >= 0:
            self.small_profile_username.render(self.screen)
        if self.small_profile_username_position.x + self.small_profile_friends_count.text_surface.get_size()[0] >= 0:
            self.small_profile_friends_count.render(self.screen)

        self.friends_selection_bg.render(self.screen)
        self.friends_selection_text.render(self.screen)
