"""
All the friend action system
"""
from Server.Database.Database import Database


def get_friend_list(username: str, logged_users: dict, db_interface: Database) -> None or list[list[str]]:
    """
    get a list of the unique key (usernames) of the friends.
    :param username: the user username.
    :param logged_users: the dictionary of the logged users.
    :param db_interface: the database interface of the server.
    :return: a list of the unique key (usernames) of the friends.
    """
    # read the database table.
    users = db_interface.submit_read("Users")

    # check if the user exists
    if username in users:
        return [
            [[get_friend_information(friend_name, db_interface, is_logged=(friend_name in logged_users), users=users) for
             friend_name in users[username]["friends"]], [friend_name for friend_name in users[username]["friends"]]], [friend_name for friend_name in users[username]["friend_requests"]]]

    return None


def get_friend_information(username: str, db_interface: Database, is_logged=None, users=None) -> None or dict:
    """
    get the public information of the friend of a user.
    :param username: the user username.
    :param db_interface: the database interface of the server.
    :param is_logged: the status of the friend.
    :param users: the users database dictionary.
    :return: a dictionary of the friend information.
    """

    # read the database table.
    if users is None:
        users = db_interface.submit_read("Users")

    # check if the user exists
    if username in users:
        data = users[username]

        send_data = {
            "username": username,
            "last_login": data["last_login"],
            "playtime": data["playtime"],
            "games_played": data["games_played"],
            "games_won": data["games_won"],
            "account_level": data["account_level"],
        }

        if is_logged is not None:
            send_data["status"] = "Online" if is_logged else "Offline"

        return send_data

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
    users[username]["friends"].append(requested_username)

    return db_interface.submit_update("Users", users)


def reject_friend(username: str, requested_username: str, db_interface: Database) -> bool:
    """
    Reject a friend request from other user.
    :param username: The user username.
    :param requested_username: The requested user username.
    :param db_interface: The database interface of the server.
    :return: The success of the rejection.
    """

    users = db_interface.submit_read("Users")

    if username not in users[requested_username]["friend_requests"]:
        return False

    users[requested_username]["friend_requests"].remove(username)

    return db_interface.submit_update("Users", users)


def invite_friend(username: str, friend_username: str, lobby_code: str, db_interface: Database) -> bool:
    """
    Invite a friend to lobby.
    :param username: The user username.
    :param friend_username: The friend username.
    :param lobby_code: The code of the lobby.
    :param db_interface: The database interface of the server.
    :return: The success of the invitation.
    """
    pass


def accept_friend_invite(username: str, friend_name: str, db_interface: Database) -> bool:
    pass


def reject_friend_invite(username: str, friend_name: str, db_interface: Database) -> bool:
    pass
