import socket
import os

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
        self.data = data
        # self.token = ?

    def get_data(self, name: str):
        """
        get a specific key from the data collection.
        :param name: the key of the data value
        :return: the value of the key in the data collection
        """
        if name in self.data:
            return self.data[name]

        return None

    def set_data(self, name: str, value: any):
        """
        set a specific data to the data collection.
        :param name: the key of the data value.
        :param value: the value of the key that will be saved in the data collection.
        :return: the success of the operation.
        """
        self.data[name] = value
