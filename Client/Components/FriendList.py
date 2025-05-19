from Client.default import *

from Client.Components.default_comp import *
from Client.client import ClientSocket
from Client.Components.Friend import FriendInterface, FriendRequest


class FriendList:
    def __init__(self, screen: pygame.Surface, client: ClientSocket, mouse_cursor: dict):
        self.offline_counter = None
        self.online_counter = None
        self.renderable_requests = None
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
        self.mouse_cursor = mouse_cursor

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

        # Friends
        self.online_friends = []
        self.offline_friends = []

        # online friends

        self.online_display_bg = MonoBehaviour(Vector2(self.width, 65), self.friends_selection_bg.position + Vector2(0, self.friends_selection_bg.size.y), (32, 32, 32))
        self.online_text = Text("Online", "Medium", 10, self.friends_selection_bg.position + Vector2(0, 0), (87, 255, 53), left_mode=True)
        self.online_counter = Text(f"{online}/{len(self.client.friends_information[0])}", "Medium", 10, Vector2(0, 0), (255, 255, 255), left_mode=True)

        self.online_text.update_position(self.friends_selection_bg.position + Vector2(0, self.friends_selection_bg.size.y) + Vector2((self.width - self.online_text.text_surface.get_size()[0] - 300 - self.online_counter.text_surface.get_size()[0]) / 2, 65 / 2))
        self.online_counter.update_position(self.online_text.position + Vector2(self.online_text.text_surface.get_size()[0] + 300, 0))

        for i, friend in enumerate(filter(lambda x: x["status"] == "Online", self.client.friends_information[0])):
                self.online_friends.append(FriendInterface(friend).to_renderable_list(self.friends_selection_bg.position + Vector2(0, self.friends_selection_bg.size.y + 65) + Vector2(0, i * (76 + 10))))

        # offline friends

        self.offline_display_bg = MonoBehaviour(Vector2(self.width, 65), (self.online_friends[-1][0].position + Vector2(0, self.online_friends[-1][0].size.y) if len(self.online_friends) > 0 else self.online_display_bg.position + Vector2(0, self.online_display_bg.size.y)), (32, 32, 32))
        self.offline_text = Text("Offline", "Medium", 10, self.offline_display_bg.position, (180, 180, 180), left_mode=True)
        self.offline_counter = Text(f"{len(self.client.friends_information[0]) - online}/{len(self.client.friends_information[0])}", "Medium", 10, Vector2(0, 0), (255, 255, 255), left_mode=True)

        self.offline_text.update_position(self.offline_display_bg.position + Vector2((self.width - self.offline_text.text_surface.get_size()[0] - 300 - self.offline_counter.text_surface.get_size()[0]) / 2, 65 / 2))
        self.offline_counter.update_position(self.offline_text.position + Vector2(self.offline_text.text_surface.get_size()[0] + 300, 0))

        for i, friend in enumerate(filter(lambda x: x["status"] == "Offline", self.client.friends_information[0])):
            self.offline_friends.append(FriendInterface(friend).to_renderable_list(self.offline_display_bg.position + Vector2(0, self.offline_display_bg.size.y) + Vector2(0, i * (76 + 10))))

        # request sections
        self.renderable_requests = []

        for index, request_username in enumerate(self.client.friends_information[1]):
            self.renderable_requests.append(FriendRequest(request_username, self.friends_selection_bg.position + Vector2(0, self.friends_selection_bg.size.y) + Vector2(0, index * (76 + 10))))

        # Add Friend
        self.add_friend_bg = MonoBehaviour(Vector2(self.width, 75), Vector2(self.friends_selection_bg.position.x, self.screen.get_height() - 75), (32, 32, 32))
        self.add_friend_text_box = TextBox(Vector2(383, 55), self.add_friend_bg.position + Vector2(15, 10), (22, 22, 22), "Add Friend", "Regular", 16, (255, 255, 255), padding=(20, 0, 20, 0), border_radius=10, text_left_mode=True)
        self.add_friend_send_button_bg = MonoBehaviour(Vector2(55, 55), self.add_friend_text_box.position + Vector2(self.add_friend_text_box.size.x + 15, 0), (69, 72, 233), border_radius=10)
        self.add_friend_send_button_icon = Image(os.path.join("Images", "Arrow.png"), Vector2(22, 19), self.add_friend_send_button_bg.position + self.add_friend_send_button_bg.size / 2, rotate=-90, centered=True)

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
        self.offline_display_bg.position = (self.online_friends[-1][0].position + Vector2(0, self.online_friends[-1][0].size.y) if len(self.online_friends) > 0 else self.online_display_bg.position + Vector2(0, self.online_display_bg.size.y))
        self.offline_text.update_position(self.offline_display_bg.position + Vector2((self.width - self.offline_text.text_surface.get_size()[0] - 300 - self.offline_counter.text_surface.get_size()[0]) / 2, 65 / 2))
        self.offline_counter.update_position(self.offline_text.position + Vector2(self.offline_text.text_surface.get_size()[0] + 300, 0))
        self.add_friend_bg.position = Vector2(self.friends_selection_bg.position.x, self.screen.get_height() - 75)
        self.add_friend_text_box.update_position(self.add_friend_bg.position + Vector2(15, 10))
        self.add_friend_send_button_bg.position = self.add_friend_text_box.position + Vector2(self.add_friend_text_box.size.x + 15, 0)
        self.add_friend_send_button_icon.position = self.add_friend_send_button_bg.position + self.add_friend_send_button_bg.size / 2

        self.renderable_requests = []

        # need to work on the online friend and fix the offline friends base pos

        for friend in self.offline_friends:
            for i, comp in enumerate(friend):
                if i == 1:
                    comp.update_position(Vector2(self.background.position.x + 40 + 42 + 35, comp.abs_position.y))
                elif i == 2:
                    comp.position = Vector2(self.background.position.x + 484 - 40 - 22, comp.position.y)
                else:
                    comp.position = Vector2(self.background.position.x, comp.position.y)

        self.renderable_requests = []

        for index, request_username in enumerate(self.client.friends_information[1]):
            self.renderable_requests.append(FriendRequest(request_username, self.friends_selection_bg.position + Vector2(0, self.friends_selection_bg.size.y) + Vector2(0, index * (76 + 10))))

    def update_data(self):
        """
        Update the friend list using the new data
        :return:
        """
        # count all the online friends
        online = 0
        for friend in self.client.friends_information[0]:
            if friend["status"] == "Online":
                online += 1

        self.small_profile_friends_count = Text(f"{len(self.client.friends_information[0])} Friends / {online} Online", "Regular", 16, Vector2(0, 0), (255, 255, 255), top_left_mode=True)
        self.online_counter = Text(f"{online}/{len(self.client.friends_information[0])}", "Medium", 10, Vector2(0, 0), (255, 255, 255), left_mode=True)
        for i, friend in enumerate(filter(lambda x: x["status"] == "Online", self.client.friends_information[0])):
            self.online_friends.append(FriendInterface(friend).to_renderable_list(self.friends_selection_bg.position + Vector2(0, self.friends_selection_bg.size.y + 65) + Vector2(0, i * (76 + 10))))

        self.offline_counter = Text(f"{len(self.client.friends_information[0]) - online}/{len(self.client.friends_information[0])}", "Medium", 10, Vector2(0, 0), (255, 255, 255), left_mode=True)

        for i, friend in enumerate(filter(lambda x: x["status"] == "Offline", self.client.friends_information[0])):
            self.offline_friends.append(FriendInterface(friend).to_renderable_list(self.offline_display_bg.position + Vector2(0, self.offline_display_bg.size.y + 65) + Vector2(0, i * (76 + 10))))

        self.renderable_requests = []

        for index, request_username in enumerate(self.client.friends_information[1]):
            self.renderable_requests.append(FriendRequest(request_username, self.friends_selection_bg.position + Vector2(0, self.friends_selection_bg.size.y) + Vector2(0, index * (76 + 10))))

        self.__update_positions()

    def update(self, dt: float, events: list):
        """
        Update the friend list display.
        :param dt: the delta time between each frame.
        :param events: the events that are happening in the game.
        """
        self.add_friend_text_box.update(dt, events)
        if self.animation_status:
            if self.shown and self.background.position.x < 0:
                self.background.position.x += self.width * (dt / self.animation_time)
            elif self.shown and self.background.position.x >= 0:
                self.animation_status = False
                self.background.position.x = 0
                self.small_profile.position.x = self.background.position.x
                self.mouse_cursor["HAND"] += [self.friends_selection_bg, self.requests_selection_bg, self.add_friend_send_button_bg, self.add_friend_send_button_icon]
                self.mouse_cursor["IBEAM"] += [self.add_friend_text_box]
            elif not self.shown and self.background.position.x > -self.width:
                self.background.position.x -= self.width * (dt / self.animation_time)
            elif self.shown and self.background.position.x <= -self.width:
                self.animation_status = False
                self.background.position.x = -self.width

                # remove friend list components only from mouse cursor
                self.mouse_cursor["HAND"].remove(self.friends_selection_bg, self.requests_selection_bg, self.add_friend_send_button_bg, self.add_friend_send_button_icon)
                self.mouse_cursor["IBEAM"].remove(self.add_friend_text_box)

            self.__update_positions()

        elif self.shown:
            if self.friend_tab:
                pass
            else:
                for request in self.renderable_requests:
                    status = request.update(dt, events)
                    if status is not None:
                        if status:
                            response = self.client.send_request("accept_friend", {"Username": request.username})

                            if response["StatusCode"] == 200:
                                print("Friend request accepted successfully")

                                # update the friend list data
                                self.client.friends_information[0].append(response["Data"]["Friend_Information"])
                        else:
                            response = self.client.send_request("reject_friend", {"Username": request.username})

                            if response["StatusCode"] == 200:
                                print("Friend request rejected successfully")

                                # update the requests in the client
                                self.client.friends_information[1].remove(request.username)

            # update the friend list data
            self.update_data()

            for event in events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    if self.friends_selection_bg.is_collide(mouse_pos):
                        self.friend_tab = True
                        self.friends_selection_bg.color = (32, 32, 32)
                        self.requests_selection_bg.color = (26, 26, 26)
                    elif self.requests_selection_bg.is_collide(mouse_pos):
                        self.friend_tab = False
                        self.friends_selection_bg.color = (26, 26, 26)
                        self.requests_selection_bg.color = (32, 32, 32)
                    elif self.add_friend_send_button_bg.is_collide(mouse_pos):
                        response = self.client.send_request("Add_Friend", {"Username": self.add_friend_text_box.content})
                        self.add_friend_text_box.update_text("")
                        if response["StatusCode"] == 200:
                            print("Friend request sent successfully")
                        else:
                            print("Friend request failed")

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
        if self.friend_tab and self.online_display_bg.position.x + self.online_display_bg.size.x >= 0:
            self.online_display_bg.render(self.screen)
        if self.friend_tab and self.online_text.position.x + self.online_text.text_surface.get_size()[0] >= 0:
            self.online_text.render(self.screen)
        if self.friend_tab and self.online_counter.position.x + self.online_counter.text_surface.get_size()[0] >= 0:
            self.online_counter.render(self.screen)
        if self.friend_tab and self.offline_display_bg.position.x + self.offline_display_bg.size.x >= 0:
            self.offline_display_bg.render(self.screen)
        if self.friend_tab and self.offline_text.position.x + self.offline_text.text_surface.get_size()[0] >= 0:
            self.offline_text.render(self.screen)
        if self.friend_tab and self.offline_counter.position.x + self.offline_counter.text_surface.get_size()[0] >= 0:
            self.offline_counter.render(self.screen)
        if self.add_friend_bg.position.x + self.add_friend_bg.size.x >= 0:
            self.add_friend_bg.render(self.screen)
        if self.add_friend_text_box.position.x + self.add_friend_text_box.size.x >= 0:
            self.add_friend_text_box.render(self.screen)
        if self.add_friend_send_button_bg.position.x + self.add_friend_send_button_bg.size.x >= 0:
            self.add_friend_send_button_bg.render(self.screen)
        if self.add_friend_send_button_icon.position.x + self.add_friend_send_button_icon.size.x >= 0:
            self.add_friend_send_button_icon.render(self.screen)

        if self.friend_tab:
            for friend in self.online_friends + self.offline_friends:
                for comp in friend:
                    if type(comp) is Text:
                        if comp.position.x + comp.text_surface.get_size()[0] >= 0:
                            comp.render(self.screen)
                    elif comp.position.x + comp.size.x >= 0:
                        comp.render(self.screen)

        else:
            for request in self.renderable_requests:
                request.render(self.screen)

