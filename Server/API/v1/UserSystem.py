"""
All the user action system
register, login, delete account, get information...
"""
from Server.Database.Database import Database
import hashlib
import string
import random
import datetime


def register(username: str, password: str, db_interface: Database) -> bool:
    """
    Register a new user to the database
    :param username: the user username
    :param password: the password of the user
    :param db_interface: the database interface of the server
    :return: return the success of the registration.
    """

    users = db_interface.submit_read("Users")

    # encrypt the password with salt.
    salt = ""
    for _ in range(8):
        salt += string.hexdigits[random.randint(0, len(string.hexdigits) - 1)]

    users[username] = {
        "password": hashlib.sha256((salt + password).encode()).hexdigest(),
        "salt": salt,
        "last_login": datetime.datetime.now()
    }

    return db_interface.submit_update("Users", users)


def login(username: str, password: str):
    pass


def delete(username: str, password: str):
    pass


def get(username: str):
    pass
