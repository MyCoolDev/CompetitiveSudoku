import hashlib
import json
import socket
import threading
import time

from lobby import Lobby

from Client.Components.Notification import NotificationInterface

from dotenv import dotenv_values


class ClientSocket:
    def __init__(self, application):
        """
        The client socket side, interact with the server to get and post data to the server.
        """

        self.application = application

        self.config = dotenv_values(".env")

        self.server_address = self.config["SERVER_ADDRESS"]
        self.server_port = int(self.config["SERVER_PORT"])

        # auth token
        self.token = None

        self.friends_information = []

        self.lobby: Lobby = None

        # saved data
        self.data = {}

        # notifications
        self.notifications = []

        self.requests_id_counter = 0
        self.responses = {}

        try:
            self.socket = socket.socket()
            self.socket.connect((self.server_address, self.server_port))
            print("Connected to the server.")

            threading.Thread(target=self.listener, daemon=True).start()

        except Exception as e:
            print(e)

    def get_data(self, name: str):
        """
        Get a specific key from the data collection.
        :param name: the key of the data value
        :return: the value of the key in the data collection
        """
        if name in self.data:
            return self.data[name]

        return None

    def set_data(self, name: str, value: any):
        """
        Set a specific data to the data collection.
        :param name: the key of the data value.
        :param value: the value of the key that will be saved in the data collection.
        :return: the success of the operation.
        """
        self.data[name] = value

    def send_request(self, command: str, data: dict, timeout=5) -> dict:
        """
        Send request to the server.
        :param command:
        :param data:
        :param timeout: timeout of response in seconds.
        :return: response of the server.
        """
        # group all the response (except the checksum) into a json to calc the checksum.
        rid = self.requests_id_counter
        request = {
            "Id": rid,
            "Command": command,
            "Data": data,
        }

        self.requests_id_counter += 1

        if self.token is not None:
            request["Token"] = self.token

        # calc the checksum, md5 to hex.
        checksum = self.create_checksum(request)

        # add the checksum to the response
        request["Checksum"] = checksum

        try:
            # stringify the json format and encode to bytes.
            stringify_response = json.dumps(request).encode('utf-8')

            # send the response to the client.
            sent = self.socket.send(stringify_response)

            # check if the sent response length is the same the original stringify response.
            if not sent == len(stringify_response):
                return {}

            print("Request sent.")

            start = time.time()
            end_time = time.time()

            response = {}

            while rid not in self.responses and end_time - start < timeout:
                end_time = time.time()

            if rid in self.responses:
                response = self.responses[rid]

            if response["StatusCode"] != 200 and response["StatusCode"] != 201:
                # add notification with the status and message
                self.notifications.append(NotificationInterface(response["Status"], response["Data"]["Msg"], span_color=(234, 68, 68)))

            return response
        except Exception as e:
            print(e)

    def listener(self):
        while True:
            try:
                # wait for the request to arrive.
                response = self.socket.recv(1024).decode('utf-8')

                # convert to json object.
                response = json.loads(response)

                # save the checksum.
                recv_checksum = response["Checksum"]

                # delete the checksum from the original request.
                del response["Checksum"]

                # generate a new checksum for the request.
                current_checksum = self.create_checksum(response)

                # check if the checksums match, if not send an error response.
                if current_checksum == recv_checksum:
                    if self.check_response_protocol(response):
                        self.responses[response["Id"]] = response
                        continue
                    elif self.check_push_notification_protocol(response):
                        # push server notifications.
                        self.handle_server_notification(response)
                        continue
            except Exception as e:
                print(e)

    @staticmethod
    def check_response_protocol(response: dict):
        """
        Check if the response is in the correct format.
        :param response: the response to check.
        :return: True if the response is in the correct format, False otherwise.
        """
        if "Id" not in response:
            return False

        if "StatusCode" not in response:
            return False

        if "Status" not in response:
            return False

        if "Data" not in response:
            return False

        if "Msg" not in response["Data"]:
            return False

        return True

    def handle_server_notification(self, update: dict):
        """
        Handle server push notification.
        :param update: the push notification received from the server.
        :return:
        """

        if update["Update"] == "Lobby_Kick":
            """
            On lobby user (this) kick.
            """
            self.lobby = None

            # update the notification.
            self.notifications.append(NotificationInterface("Removed From Lobby", "You have been kicked from the lobby by the host.", span_color=(234, 68, 68)))
        elif update["Update"] == "Lobby_Ban":
            """
            On lobby user (this) ban.
            """
            self.lobby = None

            # update the notification.
            self.notifications.append(NotificationInterface("Baned From Lobby", "You have been baned from the lobby by the host.", span_color=(234, 68, 68)))
        elif update["Update"] == "User_Joined_Lobby":
            """
            On user join the lobby.
            """
            self.lobby[update["Data"]["Role"]].append(update["Data"]["Username"])

            # update the notification if the user is not the current user.
            if self.get_data("username") != update["Data"]["Username"]:
                self.notifications.append(NotificationInterface("Lobby Update", f"{update['Data']['Username']} joined the lobby with {update['Data']['Role']} role."))
        elif update["Update"] == "User_Left_Lobby":
            """
            On user left the lobby.
            """
            self.lobby[update["Data"]["Role"]].remove(update["Data"]["Username"])

            # update the notification if the user is not the current user.
            if self.get_data("username") != update["Data"]["Username"]:
                self.notifications.append(NotificationInterface("Lobby Update", f"{update['Data']['Username']} left the lobby."))
        elif update["Update"] == "Become_Spectator":
            """
            On user become spectator.
            """
            self.lobby["spectators"] += 1
            self.lobby["players"].remove(update["Data"]["Username"])

            if self.get_data("username") == update["Data"]["Username"]:
                self.set_data("Lobby_Role", "spectators")
        elif update["Update"] == "Become_Player":
            """
            On user become player.
            """
            self.lobby["players"].append(update["Data"]["Username"])
            self.lobby["spectators"] -= 1

    @staticmethod
    def check_push_notification_protocol(update: dict):
        """
        Check if the push notification is in the correct format.
        :param update: the push notification to check.
        :return: True if the push notification is in the correct format, False otherwise.
        """
        if "Update" not in update:
            return False

        if "Data" not in update:
            return False

        return True

    def set_token(self, token: str):
        """
        set the authentication token
        """
        self.token = token

    @staticmethod
    def create_checksum(subject: dict) -> str:
        """
        Generate md5 checksum to plain text.
        :param subject: the subject of the checksum
        :return: the md5 generated checksum in hexdigits.
        """

        return hashlib.md5(json.dumps(subject).encode('utf-8')).hexdigest()
