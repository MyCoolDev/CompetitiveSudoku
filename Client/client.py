import hashlib
import json
import socket
import threading
import time

from lobby import Lobby

from Client.Components.Notification import NotificationInterface
from Client.lobby import Message

from dotenv import dotenv_values

# Encryptions
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class ClientSocket:
    def __init__(self, application):
        """
        The client socket side, interact with the server to get and post data to the server.
        """

        # Create a pair of public and private keys
        # Generate RSA keys
        self.private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        public_key = self.private_key.public_key()

        # Serialize public key to send to client
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

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

            print("Sending public key to the server.")

            self.socket.sendall(public_pem)

            print("Waiting for aes key from the server.")

            # Receive aes key from the server
            aes_key = self.socket.recv(1024)

            print("Received aes key from the server.")

            # Decrypt the aes key using the private key
            aes_key = self.private_key.decrypt(
                aes_key,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # send confirmation to the server
            self.socket.send("AES key received".encode('utf-8'))

            print("Decrypted aes key.")

            # get the nonce key from the server

            nonce = self.socket.recv(1024)

            # Decrypt the nonce key using the private key
            nonce = self.private_key.decrypt(
                nonce,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            # send confirmation to the server
            self.socket.send("Nonce key received".encode('utf-8'))

            print("Decrypted nonce key.")

            # create a cipher
            self.cipher = Cipher(
                algorithms.AES(aes_key),
                modes.CFB(nonce),
                backend=default_backend()
            )

            threading.Thread(target=self.listener, daemon=True).start()

        except Exception as e:
            print(e)

    def get_data(self, name: str):
        """
        Get a specific key from the data collection.
        :param name: the key of the data value.
        :return: the value of the key in the data collection.
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

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt the data using the aes encryptor.
        :param data: the data to encrypt.
        :return: the encrypted data.
        """
        # create the aes encryptor.
        aes_encryptor = self.cipher.encryptor()

        # encrypt the data using the aes encryptor.
        return aes_encryptor.update(data) + aes_encryptor.finalize()

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypt the data using the aes encryptor.
        :param data: the data to decrypt.
        :return: the decrypted data.
        """
        # create the aes decryptor.
        aes_decryptor = self.cipher.decryptor()

        # decrypt the data using the aes decryptor.
        return aes_decryptor.update(data) + aes_decryptor.finalize()

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

            # encrypt the response using the aes encryptor.
            encrypted_response = self.encrypt(stringify_response)

            # send the response to the client.
            self.socket.sendall(encrypted_response)

            # send ending to server
            self.socket.send("-- End Request --".encode('utf-8'))

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
        """
        Listen to the server for incoming requests.
        """
        while True:
            try:
                response = b""

                # wait for the request to arrive.
                while True:
                    # receive the request from the server.
                    piece = self.socket.recv(1024)

                    # check if the request is the end of request signal.
                    if piece == b"-- End Request --":
                        break
                    else:
                        response += piece

                # decrypt the response using the aes encryptor.
                response = self.decrypt(response)

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
            self.set_data("go_to_home", True)

            # update the notification.
            self.notifications.append(NotificationInterface("Removed From Lobby", "You have been kicked from the lobby by the host.", span_color=(234, 68, 68)))
        elif update["Update"] == "Lobby_Ban":
            """
            On lobby user (this) ban.
            """
            self.lobby = None
            self.set_data("go_to_home", True)

            # update the notification.
            self.notifications.append(NotificationInterface("Baned From Lobby", "You have been baned from the lobby by the host.", span_color=(234, 68, 68)))
        elif update["Update"] == "User_Joined_Lobby":
            """
            On user join the lobby.
            """
            if update["Data"]["Role"] == "players":
                self.lobby.players.append(update["Data"]["Username"])
            else:
                self.lobby.spectators.append(update["Data"]["Username"])

            # update the notification if the user is not the current user.
            if self.get_data("username") != update["Data"]["Username"]:
                self.notifications.append(NotificationInterface("Lobby Update", f"{update['Data']['Username']} joined the lobby with {update['Data']['Role']} role."))
        elif update["Update"] == "User_Left_Lobby":
            """
            On user left the lobby.
            """
            if update["Data"]["Role"] == "players":
                self.lobby.players.remove(update["Data"]["Username"])
            else:
                self.lobby.spectators -= 1

            # update the notification if the user is not the current user.
            if self.get_data("username") != update["Data"]["Username"]:
                self.notifications.append(NotificationInterface("Lobby Update", f"{update['Data']['Username']} left the lobby."))
        elif update["Update"] == "Become_Spectator":
            """
            On user become spectator.
            """
            self.lobby.spectators += 1
            self.lobby.players.remove(update["Data"]["Username"])

            if self.get_data("username") == update["Data"]["Username"]:
                self.lobby.lobby_role = "spectators"
        elif update["Update"] == "Become_Player":
            """
            On user become player.
            """
            self.lobby.players.append(update["Data"]["Username"])
            self.lobby.spectators -= 1

            if self.get_data("username") == update["Data"]["Username"]:
                self.lobby.lobby_role = "players"
        elif update["Update"] == "Leaderboard":
            """
            On leaderboard update.
            """
            self.lobby.leaderboard = update["Data"]["Leaderboard"]
        elif update["Update"] == "Game_Started":
            """
            On lobby started.
            """
            print("Game started")
            self.lobby.lobby_board = update["Data"]["Board"]
            self.lobby.leaderboard = update["Data"]["Leaderboard"]
            self.lobby.set_ending_date(update["Data"]["Ending_Time"])
            self.lobby.started = True
            if self.lobby.lobby_role == "players":
                self.set_data("go_to_game", True)
            else:
                self.set_data("go_to_spectator", True)
        elif update["Update"] == "Chat_Message":
            """
            On chat message.
            """
            self.lobby.chat.append(Message(update["Data"]["Username"], update["Data"]["Message"], update["Data"]["Time"]))
            self.lobby.chat = self.lobby.chat[-4:]
        elif update["Update"] == "Game_Finished":
            """
            On max mistakes reached. move the player to spectator.
            """
            self.lobby.players.remove(self.get_data("username"))
            self.lobby.spectators += 1

            self.set_data("go_to_spectator", True)

            self.notifications.append(NotificationInterface("Game Finished", f"You have reached the max mistakes. You are now a spectator.", span_color=(234, 68, 68)))
        elif update["Update"] == "Game_Over":
            """
            On game over. move the player to spectator.
            """
            if self.lobby.lobby_role == "players":
                self.lobby.players.remove(self.get_data("username"))
            self.lobby.started = False
            self.lobby.leaderboard = update["Data"]["Leaderboard"]

            self.set_data("go_to_spectator", True)

            self.notifications.append(NotificationInterface("Game Over", f"The game is over."))
        elif update["Update"] == "Friend_Request":
            """
            On friend request received.
            """
            self.notifications.append(NotificationInterface("Friend Request", f"{update['Data']['Username']} sent you a friend request.", span_color=(234, 68, 68)))
            self.friends_information[1].append(update["Data"]["Username"])
        elif update["Update"] == "Friend_Request_Accepted":
            """
            On friend request accepted.
            """
            self.friends_information = update["Data"]["New_Friend_List"]

            self.notifications.append(NotificationInterface("Friend Request Accepted", f"{update['Data']['Username']} accepted your friend request.", span_color=(234, 68, 68)))

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
