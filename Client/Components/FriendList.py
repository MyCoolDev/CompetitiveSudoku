from Client.default import *

from Client.Components.MonoBehaviour import MonoBehaviour
from Client.Components.Text import Text
from Client.client import ClientSocket
from Client.Components.Friend import Friend


class FriendList:
    def __init__(self, screen: pygame.Surface, client: ClientSocket):
        self.profile_picture_size = None
        self.friend_tab = None
        self.requests_selection_text = None
        self.requests_selection_bg = None
        self.friends_selection_text = None
        self.friends_selection_bg = None
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
        self.background = MonoBehaviour(Vector2(self.width, self.screen.get_height()), Vector2(-self.width, 0), (26, 26, 26))
        # small profile box for positioning only, will not be rendered.
        self.small_profile = MonoBehaviour(Vector2(self.width, 134), self.background.position, (255, 255, 255))
        self.small_profile_username = Text(self.client.get_data("username").strip(), "Medium", 26, Vector2(0, 0), (255, 255, 255), top_left_mode=True)

        # count all the online friends
        online = 0
        for friend in self.client.friends_information[0]:
            if friend["status"] == "Online":
                online += 1

        self.small_profile_friends_count = Text(f"{len(self.client.friends_information[0])} Friends / {online} Online", "Regular", 16, Vector2(0, 0), (255, 255, 255), top_left_mode=True)

        # profile picture
        self.profile_picture_size = Vector2(56, 56)

        # calc the position of the username and the friends count.
        self.small_profile_username.update_position(self.small_profile.position + Vector2(self.small_profile.size.x / 2 - (self.small_profile_username.text_surface.get_size()[0] + 140 + self.profile_picture_size.x) / 2, self.small_profile.size.y / 2 - (self.small_profile_username.text_surface.get_size()[1] + 12 + self.small_profile_friends_count.text_surface.get_size()[1]) / 2))
        self.small_profile_friends_count.update_position(self.small_profile_username.position + Vector2(0, self.small_profile_username.text_surface.get_size()[1] + 12))

        # Friends / Request Tab Selection
        self.friend_tab = True
        self.friends_selection_bg = MonoBehaviour(Vector2(self.width / 2, 54), self.small_profile.position + Vector2(0, self.small_profile.size.y), (32, 32, 32), border_top_right_radius=10)
        self.friends_selection_text = Text("Friends", "Medium", 16, self.friends_selection_bg.position + Vector2(self.friends_selection_bg.size[0] / 2, self.friends_selection_bg.size[1] / 2), (255, 255, 255), center_mode=True)

        self.requests_selection_bg = MonoBehaviour(Vector2(self.width / 2, 54), self.friends_selection_bg.position + Vector2(self.width / 2, 0),
                                                   (26, 26, 26), border_top_left_radius=10)
        self.requests_selection_text = Text("Requests", "Medium", 16, self.requests_selection_bg.position + Vector2(
                                            self.requests_selection_bg.size.x / 2, self.requests_selection_bg.size.y / 2), (255, 255, 255),
                                            center_mode=True)

        # Friends Tab
        self.online_display_bg = MonoBehaviour(Vector2(self.width, 65), self.friends_selection_bg.position + Vector2(0, self.friends_selection_bg.size.y), (32, 32, 32))
        self.online_text = Text("Online", "Medium", 10, self.friends_selection_bg.position + Vector2(0, 0), (87, 255, 53), left_mode=True)
        self.online_counter = Text(f"{online}/{len(self.client.friends_information[0])}", "Medium", 10, Vector2(0, 0), (255, 255, 255), left_mode=True)

        self.online_text.update_position(self.friends_selection_bg.position + Vector2(0, self.friends_selection_bg.size.y) + Vector2((self.width - self.online_text.text_surface.get_size()[0] - 300 - self.online_counter.text_surface.get_size()[0]) / 2, 65 / 2))
        self.online_counter.update_position(self.online_text.position + Vector2(self.online_text.text_surface.get_size()[0] + 300, 0))

        # Friends
        self.friends = []

        for i, friend in enumerate(self.client.friends_information[0]):
            self.friends.append(Friend(friend).to_renderable_list(self.friends_selection_bg.position + Vector2(0, self.friends_selection_bg.size.y + 65) + Vector2(0, i * (76 + 10))))

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
        self.small_profile_username.update_position(self.small_profile.position + Vector2(self.small_profile.size.x / 2 - (self.small_profile_username.text_surface.get_size()[0] + 230 + self.profile_picture_size.x) / 2, self.small_profile.size.y / 2 - (self.small_profile_username.text_surface.get_size()[1] + 12 + self.small_profile_friends_count.text_surface.get_size()[1]) / 2))
        self.small_profile_friends_count.update_position(self.small_profile_username.position + Vector2(0, self.small_profile_username.text_surface.get_size()[1] + 12))
        self.friends_selection_bg.position = self.small_profile.position + Vector2(0, self.small_profile.size.y)
        self.friends_selection_text.update_position(self.friends_selection_bg.position + Vector2(self.friends_selection_bg.size.x / 2, self.friends_selection_bg.size.y / 2))
        self.requests_selection_bg.position = self.friends_selection_bg.position + Vector2(self.width / 2, 0)
        self.requests_selection_text.update_position(self.requests_selection_bg.position + Vector2(self.requests_selection_bg.size.x / 2, self.requests_selection_bg.size.y / 2))
        self.online_display_bg.position = Vector2(self.background.position.x, self.online_display_bg.position.y)
        self.online_text.update_position(self.friends_selection_bg.position + Vector2(0, self.friends_selection_bg.size.y) + Vector2((self.width - self.online_text.text_surface.get_size()[0] - 300 - self.online_counter.text_surface.get_size()[0]) / 2, 65 / 2))
        self.online_counter.update_position(self.online_text.position + Vector2(self.online_text.text_surface.get_size()[0] + 300, 0))

        for friend in self.friends:
            for i, comp in enumerate(friend):
                if i == 1:
                    comp.update_position(Vector2(self.background.position.x + 40 + 42 + 35, comp.abs_position.y))
                elif i == 2:
                    comp.position = Vector2(self.background.position.x + 484 - 40 - 22, comp.position.y)
                else:
                    comp.position = Vector2(self.background.position.x, comp.position.y)

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
        if self.small_profile_username.position.x + self.small_profile_username.text_surface.get_size()[0] >= 0:
            self.small_profile_username.render(self.screen)
        if self.small_profile_username.position.x + self.small_profile_friends_count.text_surface.get_size()[0] >= 0:
            self.small_profile_friends_count.render(self.screen)
        if self.friends_selection_bg.position.x + self.friends_selection_bg.size.x >= 0:
            self.friends_selection_bg.render(self.screen)
        if self.friends_selection_text.position.x + self.friends_selection_text.text_surface.get_size()[0] >= 0:
            self.friends_selection_text.render(self.screen)
        if self.requests_selection_bg.position.x + self.requests_selection_bg.size.x >= 0:
            self.requests_selection_bg.render(self.screen)
        if self.requests_selection_text.position.x + self.requests_selection_text.text_surface.get_size()[0] >= 0:
            self.requests_selection_text.render(self.screen)
        if self.online_display_bg.position.x + self.online_display_bg.size.x >= 0:
            self.online_display_bg.render(self.screen)
        if self.online_text.position.x + self.online_text.text_surface.get_size()[0] >= 0:
            self.online_text.render(self.screen)
        if self.online_counter.position.x + self.online_counter.text_surface.get_size()[0] >= 0:
            self.online_counter.render(self.screen)

        for friend in self.friends:
            for comp in friend:
                if type(comp) is Text:
                    if comp.position.x + comp.text_surface.get_size()[0] >= 0:
                        comp.render(self.screen)
                elif comp.position.x + comp.size.x >= 0:
                    comp.render(self.screen)
