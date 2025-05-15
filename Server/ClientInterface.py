import socket
import json
import hashlib

import utils


class Client:
    def __init__(self, address: tuple, con: socket.socket, cipher, **data):
        """
        Client interface for organized collection of the client data with the connection.
        :param address: the address of the client
        :param con: the socket connection with the client
        :param data: other data that connected to the client, the data will be saved in the data collection.
        """
        self.connection = con
        self.address = address
        self.aes_cipher = cipher
        self.running = True
        self.data = data

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
        rid = -1
        try:
            # wait for the request to arrive.
            encrypted_request = b""

            while True:
                piece = self.connection.recv(1024)
                if piece == b"-- End Request --":
                    break
                else:
                    encrypted_request += piece

            # decrypt the request using the aes decryptor.
            request = self.decrypt(encrypted_request)

            lower_request = request.lower()

            if request == "":
                return self.get_request()

            # convert to json object.
            request = json.loads(request)
            lower_request = json.loads(lower_request)

            # --- check the format requirements (see CommsProtocol.md) ---

            if "id" not in lower_request:
                self.send_response(rid, 400, "Bad Request", {"Msg": "Missing Request Id attribute."})
                return None

            rid = lower_request["id"]

            if "command" not in lower_request:
                self.send_response(rid, 400, "Bad Request", {"Msg": "Missing Command attribute."})
                return None

            if "data" not in lower_request:
                self.send_response(rid, 400, "Bad Request", {"Msg": "Missing Data attribute."})
                return None

            if "checksum" not in lower_request:
                self.send_response(rid, 400, "Bad Request", {"Msg": "Missing Checksum attribute."})
                return None

            # save the checksum.
            recv_checksum = request["Checksum"]

            # delete the checksum from the original request.
            del request["Checksum"]

            # generate a new checksum for the request.
            current_checksum = self.create_checksum(request)

            # check if the checksums match, if not send an error response.
            if current_checksum != recv_checksum:
                self.send_response(rid, 400, "Bad Request", {"Msg": "Invalid Checksum."})
                return None

            return request

        except ConnectionResetError:
            # if the connection is reset, return None.
            return None

        except Exception as e:
            # print the exception
            utils.server_print("Handler | get_request", str(e))

            # send an error response
            self.send_response(rid, 400, "Bad Request")

            return None

    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt the data using the aes encryptor.
        :param data: the data to encrypt.
        :return: the encrypted data.
        """
        # create the aes encryptor.
        aes_encryptor = self.aes_cipher.encryptor()

        # encrypt the data using the aes encryptor.
        return aes_encryptor.update(data) + aes_encryptor.finalize()

    def decrypt(self, data: bytes) -> bytes:
        """
        Decrypt the data using the aes encryptor.
        :param data: the data to decrypt.
        :return: the decrypted data.
        """
        # create the aes decryptor.
        aes_decryptor = self.aes_cipher.decryptor()

        # decrypt the data using the aes decryptor.
        return aes_decryptor.update(data) + aes_decryptor.finalize()

    def send_response(self, rid, status_code: int, status: str, data = None) -> bool:
        """
        Send a response to the client.
        :param rid: the request id of the response
        :param status_code: the status code of the request the response handling
        :param status: the status code in plain text
        :param data: data related to the response if needed.
        :return: the success of the operation.
        """
        try:
            # group all the response (except the checksum) into a json to calc the checksum.
            response = {
                "Id": rid,
                "StatusCode": status_code,
                "Status": status,
            }

            # add the data if exists.
            if data is not None:
                response["Data"] = data

            # calc the checksum, md5 to hex.
            checksum = self.create_checksum(response)

            # add the checksum to the response
            response["Checksum"] = checksum

            # stringify the json format and encode to bytes.
            stringify_response = json.dumps(response).encode('utf-8')

            # encrypt the response using the aes encryptor.
            encrypted_response = self.encrypt(stringify_response)

            # send the response to the client.
            sent = self.connection.send(encrypted_response)

            # check if the sent response length is the same the original stringify response.
            status = sent == len(encrypted_response)

            if status:
                # send the end of request signal to the client.
                self.connection.send(b"-- End Request --")

            return status

        except Exception as e:
            # print the exception to the console
            utils.server_print("Handler | send_response", str(e))

            return False

    def push_notification(self, update: str, data: dict = None) -> bool:
        """
        Send push notification to the client
        :param update:
        :param data:
        :return:
        """
        try:
            # group all the response (except the checksum) into a json to calc the checksum.
            response = {
                "Update": update,
            }

            # add the data if exists.
            if data is not None:
                response["Data"] = data

            # calc the checksum, md5 to hex.
            checksum = self.create_checksum(response)

            # add the checksum to the response
            response["Checksum"] = checksum

            # stringify the json format and encode to bytes.
            stringify_response = json.dumps(response).encode('utf-8')

            # encrypt the response using the aes encryptor.
            encrypted_response = self.encrypt(stringify_response)

            # send the response to the client.
            sent = self.connection.send(encrypted_response)

            # check if the sent response length is the same the original stringify response.
            status = sent == len(encrypted_response)

            if status:
                # send the end of request signal to the client.
                self.connection.send(b"-- End Request --")

            return status

        except Exception as e:
            # print the exception to the console
            utils.server_print("Handler | send_response", str(e))

            return False

    @staticmethod
    def create_checksum(subject: dict) -> str:
        """
        Generate md5 checksum to plain text.
        :param subject: the subject of the checksum.
        :return: the md5 generated checksum in hexdigits.
        """

        return hashlib.md5(json.dumps(subject).encode('utf-8')).hexdigest()

    def stop(self):
        self.running = False
