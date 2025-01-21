import socket
import hashlib
import json
import time
import threading

from States.Home import Home


class ClientSocket:
    def __init__(self, application):
        """
        The client socket side, interact with the server to get and post data to the server.
        """

        self.application = application

        self.server_address = "127.0.0.1"
        self.server_port = 8080

        # auth token
        self.token = None

        # saved data
        self.data = {}

        self.requests_id_counter = 0
        self.responses = {}

        try:
            self.socket = socket.socket()
            self.socket.connect((self.server_address, self.server_port))
            print("Connected to the server.")

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

    def send_request(self, command: str, data: dict, timeout=1) -> dict:
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
                    if "Id" in response:
                        self.responses[response["Id"]] = response
                        continue
                    else:
                        # push server notifications.
                        self.handle_server_notification(response)
            except Exception as e:
                print(e)

    def handle_server_notification(self, update: dict):
        """
        Handle server push notification.
        :param update: the push notification received from the server.
        :return:
        """
        if update["Update"] == "Lobby_Kick":
            self.application.current_state = Home(self.application.screen, self)

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
