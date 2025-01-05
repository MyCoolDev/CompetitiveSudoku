"""
All the user action system
register, login, delete account, get information...
"""
from Server.Database.Database import Database
import hashlib
import string
import random
import datetime
import Server.Hashing as Hashing


def register(username: str, password: str, db_interface: Database) -> bool:
    """
    Register a new user to the database
    :param username: the user username
    :param password: the password of the user
    :param db_interface: the database interface of the server
    :return: the success of the registration.
    """

    users = db_interface.submit_read("Users")

    hashed_password = Hashing.hash_password(password).hex()

    users[username] = {
        "password": hashed_password,
        "last_login": datetime.datetime.now()
    }

    return db_interface.submit_update("Users", users)


def delete(username: str, password: str):
    pass


def get(username: str, db_interface: Database) -> dict or None:
    """
    get the user's information from the database.
    :param username: the username of the user.
    :param db_interface: the database interface of the server
    :return: the information of the user if exists, otherwise None.
    """
    # read the database table.
    users = db_interface.submit_read("Users")

    # check if the user exists
    if username in users:
        return users[username]

    return None
