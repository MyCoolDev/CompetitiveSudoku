"""
All the friend action system
"""
from Server.Database.Database import Database


def get_friend_list(username: str, db_interface: Database) -> None or list[str]:
    """
    get a list of the unique key (usernames) of the friends.
    :param username: the user username.
    :param db_interface: the database interface of the server.
    :return: a list of the unique key (usernames) of the friends.
    """
    # read the database table.
    users = db_interface.submit_read("Users")

    # check if the user exists
    if username in users:
        return [(friend_name, users[friend_name]["last_login"] for friend_name in users[username]["friends"])]

    return None


def get_friend_information(username: str, db_interface: Database) -> None or dict:
    """
    get the public information of the friend of a user.
    :param username: the user username.
    :param db_interface: the database interface of the server.
    :return: a dictionary of the friend information.
    """

    # read the database table.
    users = db_interface.submit_read("Users")

    # check if the user exists
    if username in users:
        data = users[username]
        del data["password"]
        del data["messages"]
        # Should I remove the friend list from the information?

        return data

    return None

def add_friend(username: str, requested_username, db_interface: Database) -> bool:
    """
    Send a friend request to other user.
    :param username: The user username.
    :param requested_username: The other user username.
    :param db_interface: The database interface of the server.
    :return: The success of sending the request.
    """

    users = db_interface.submit_read("Users")

    if username not in users or requested_username not in users:
        return False

    if username in users[requested_username]["friend_requests"] + users[requested_username]["friends"]:
        return False

    users[requested_username]["friend_requests"].append(username)
    users[requested_username]["friends"].append(username)

    return db_interface.submit_update("Users", users)

def accept_friend(username: str, requested_username, db_interface: Database) -> bool:
    """
    Accept a friend request from other user.
    :param username: The user username.
    :param requested_username: The requested user username.
    :param db_interface: The database interface of the server.
    :return: The success of the acceptance.
    """

    users = db_interface.submit_read("Users")

    if username not in users or requested_username not in users:
        return False

    if username not in users[requested_username]["friend_requests"]:
        return False

    users[requested_username]["friend_requests"].remove(username)
    users[requested_username]["friends"].append(username)

    return db_interface.submit_update("Users", users)
