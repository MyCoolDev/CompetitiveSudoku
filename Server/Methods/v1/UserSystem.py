"""
All the user action system
register, login, delete account, get information...
"""
import datetime

import Server.Hashing as Hashing
from Server.Database.Database import Database


def register(address: tuple, username: str, password: str, db_interface: Database) -> bool:
    """
    Register a new user to the database.
    :param address: The address of the user.
    :param username: The user username.
    :param password: The password of the user.
    :param db_interface: The database interface of the server.
    :return: The success of the registration.
    """

    users = db_interface.submit_read("Users")

    hashed_password = Hashing.hash_password(password).hex()

    users[username] = {
        "username": username,
        "password": hashed_password,
        "last_login": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "last_login_address": address,
        "friends": [],
        "friend_requests": [],
        "lifetime": 0,
        "account_level": 1,
        "account_experience": 0,
        "playtime": 0,
        "games_played": 0,
        "games_won": 0,
    }

    return db_interface.submit_update("Users", users)


def delete(username: str, password: str):
    pass

def update_login_data(address: tuple, username: str, db_interface: Database) -> bool:
    """
    Update the login time of the user.
    :param address: The address of the user.
    :param username: The user username.
    :param db_interface: The database interface of the server.
    :return: The success of the update.
    """
    users = db_interface.submit_read("Users")

    if username not in users:
        return False

    users[username]["last_login"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    users[username]["last_login_address"] = address

    return db_interface.submit_update("Users", users)

def update_playtime(username: str, have_won: bool, playtime: str, account_exp: float, db_interface: Database):
    """
    Update the playtime of the user.
    :param username: The user username.
    :param db_interface: The database interface of the server.
    :return: The success of the update.
    """
    users = db_interface.submit_read("Users")

    if username not in users:
        return False

    # update the playtime of the user, playtime is presented in minutes.
    users[username]["playtime"] += playtime
    users[username]["account_experience"] += account_exp
    users[username]["games_played"] += 1
    users[username]["games_won"] += 1 if have_won else 0

    return db_interface.submit_update("Users", users)

def update_logout(username: str, db_interface: Database):
    """
    Update the lifetime of the user.
    :param username: The user username.
    :param db_interface: The database interface of the server.
    """
    users = db_interface.submit_read("Users")

    if username not in users:
        return False

    # update the lifetime of the user, lifetime is presented in minutes.
    users[username]["lifetime"] += round((datetime.datetime.now() - datetime.datetime.strptime(users[username]["last_login"], "%Y-%m-%d %H:%M:%S")).seconds / 60, 2)

    return db_interface.submit_update("Users", users)

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
