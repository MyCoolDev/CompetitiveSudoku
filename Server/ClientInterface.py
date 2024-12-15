import socket
import json
import hashlib


class Client:
    def __init__(self, address: str, con: socket.socket, **data):
        """
        Client interface for organized collection of the client data with the connection.
        :param address: the address of the client
        :param con: the socket connection with the client
        :param data: other data that connected to the client, the data will be saved in the data collection.
        """
        self.connection = con
        self.address = address
        self.running = True
        self.data = data
        # self.token = ?

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

    def get_request(self) -> dict or None:
        """
        Wait for the client to send a request to the server.
        :return: the request after formation.
        """
        try:
            # wait for the request to arrive.
            request = self.connection.recv(1024).decode('utf-8').lower()

            # convert to json object.
            request = json.loads(request)

            # --- check the format requirements (see CommsProtocol.md) ---

            # check the command
            if "command" not in request:
                self.send_response(400, "Bad Request", {"msg": "Missing Command attribute."})
                return None

            if "data" not in request:
                self.send_response(400, "Bad Request", {"msg": "Missing Data attribute."})
                return None

            if "checksum" not in request:
                self.send_response(400, "Bad Request", {"msg": "Missing Checksum attribute."})
                return None

            # save the checksum.
            recv_checksum = request["checksum"]

            # delete the checksum from the original request.
            del request["checksum"]

            # generate a new checksum for the request.
            current_checksum = self.create_checksum(request)

            # check if the checksums match, if not send an error response.
            if current_checksum != recv_checksum:
                self.send_response(400, "Bad Request", {"msg": "Invalid Checksum."})
                return None

            return request

        except Exception as e:
            # print the exception
            print(e)

            # send an error response
            self.send_response(400, "Bad Request")

            return None

    def send_response(self, status_code: int, status: str, data=None) -> bool:
        """
        Send a response to the client.
        :param status_code: the status code of the request the response handling
        :param status: the status code in plain text
        :param data: data related to the response if needed.
        :return: the success of the operation.
        """
        try:
            # group all the response (except the checksum) into a json to calc the checksum.
            response = {
                "StatusCode": status_code,
                "Status": status,
            }

            # add the data if exists.
            if data is not None:
                response["Data"] = data

            # calc the checksum, md5 to hex.
            checksum = self.create_checksum(json.dumps(response))

            # add the checksum to the response
            response["Checksum"] = checksum

            # stringify the json format and encode to bytes.
            stringify_response = json.dumps(response).encode('utf-8')

            # send the response to the client.
            sent = self.connection.send(stringify_response)

            # check if the sent response length is the same the original stringify response.
            return sent == len(stringify_response)

        except Exception as e:
            # print the exception to the console
            print(e)

            return False

    @staticmethod
    def create_checksum(subject: str) -> str:
        """
        Generate md5 checksum to plain text.
        :param subject: the subject of the checksum
        :return: the md5 generated checksum in hexdigits.
        """

        return hashlib.md5(subject.encode('utf-8')).hexdigest()

    def stop(self):
        self.running = False
