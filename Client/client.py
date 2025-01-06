import socket
import hashlib
import json


class ClientSocket:
    def __init__(self):
        """
        The client socket side, interact with the server to get and post data to the server.
        """

        self.server_address = "127.0.0.1"
        self.server_port = 8080

        # auth token
        self.token = None

        try:
            self.socket = socket.socket()
            self.socket.connect((self.server_address, self.server_port))
            print("Connected to the server.")

        except Exception as e:
            print(e)

    def send_request(self, command: str, data: dict) -> dict:
        """
        Send request to the server.
        :param command:
        :param data:
        :return: response of the server
        """
        # group all the response (except the checksum) into a json to calc the checksum.
        request = {
            "Command": command,
            "Data": data,
        }

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
            if current_checksum != recv_checksum:
                return {}

            return response
        except Exception as e:
            print(e)

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
