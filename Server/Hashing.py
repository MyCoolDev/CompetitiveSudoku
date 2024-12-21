"""
Manage all the hashing function that the server use.
"""

import hashlib
import bcrypt

def hash_password(password: str) -> bytes:
    """
    hash the password using bcrypt.
    :param password: the password to hash.
    :return: the hashed password.
    """
    # generate a bcrypt salt
    salt = bcrypt.gensalt()

    # hash the password using the salt
    hashed = bcrypt.hashpw(password.encode(), salt)

    return hashed

def hash_password_with_salt(password: str, salt: bytes) -> bytes:
    """
    hash the password using bcrypt and the given salt.
    :param password: the password to hash
    :param salt: the salt for the hash.
    :return: the hashed password.
    """
    hashed = bcrypt.hashpw(password.encode(), salt)

    return hashed

def check_password(hashed_password: bytes, password: str) -> bool:
    """
    check the real password with the salt match the password.
    :param hashed_password: the actual password.
    :param password: the password to check.
    :return: true if the real password match the password, otherwise false.
    """
    return bcrypt.checkpw(password.encode(), hashed_password)
