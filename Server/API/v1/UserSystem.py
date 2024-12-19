"""
All the user action system
register, login, delete account, get information...
"""
from Server.Database.Database import Database

def register(username: str, password: str, db_interface: Database) -> bool:
    """
    Register a new user to the database
    :param username: the user username
    :param password: the password of the user
    :param db_interface: the database interface of the server
    :return: return the success of the registration.
    """
    pass

def login(username: str, password: str):
    pass

def delete(username: str, password: str):
    pass

def get(username: str):
    pass