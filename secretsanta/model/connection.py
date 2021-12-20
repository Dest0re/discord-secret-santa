import os

from peewee import MySQLDatabase

# Maybe a class for the constants
_DATABASE_HOST = os.getenv('DATABASE_HOST')
_DATABASE_PORT = os.getenv('DATABASE_PORT')
_MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
_MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
_DATABASE_NAME = os.getenv('DATABASE_NAME')

try:
    assert _DATABASE_HOST and _DATABASE_PORT and _MYSQL_USERNAME and _MYSQL_PASSWORD and _DATABASE_NAME
except AssertionError:
    raise KeyError("Some important stuff is missing.")


connection = MySQLDatabase(
    database=_DATABASE_NAME,
    host=_DATABASE_HOST,
    port=int(_DATABASE_PORT),
    user=_MYSQL_USERNAME,
    passwd=_MYSQL_PASSWORD
)

connection.connect()
