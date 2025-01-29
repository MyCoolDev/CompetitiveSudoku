"""
All the user action system
register, login, delete account, get information...
"""
from Server.Database.Database import Database
import datetime
import Server.Hashing as Hashing


def register(username: str, password: str, db_interface: Database) -> bool:
    """
    Register a new user to the database.
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
        "messages": {
            "seen": {},
            "unseen": []
        },
        "friends": [],
        "friend_requests": [],
        "playtime": 0,
        "games_played": 0,
        "games_won": 0,
        "account_level": 1,
        "account_experience": 0
    }

    return db_interface.submit_update("Users", users)


def delete(username: str, password: str):
    pass

def update_login_time(username: str, db_interface: Database) -> bool:
    """
    Update the login time of the user.
    :param username: The user username.
    :param db_interface: The database interface of the server.
    :return: The success of the update.
    """
    users = db_interface.submit_read("Users")

    if username not in users:
        return False

    users[username]["last_login"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

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
