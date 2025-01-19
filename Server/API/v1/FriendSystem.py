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
