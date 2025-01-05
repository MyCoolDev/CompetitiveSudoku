import socket


class ClientSocket:
    def __init__(self):
        """
        The client socket side, interact with the server to get and post data to the server.
        """

        self.server_address = "127.0.0.1"
        self.server_port = 8080

        try:
            self.socket = socket.socket()
            self.socket.connect((self.server_address, self.server_port))
            print("Connected to the server.")

        except Exception as e:
            print(e)

    def send_request(self, command: int, data: str) -> bool:
        pass

    @staticmethod
    def create_checksum(subject: str) -> str:
        """
        Generate md5 checksum to plain text.
        :param subject: the subject of the checksum
        :return: the md5 generated checksum in hexdigits.
        """

        return hashlib.md5(subject.encode('utf-8')).hexdigest()