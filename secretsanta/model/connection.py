import os

from peewee import MySQLDatabase

from .utils import EnvironmentVariables


env = EnvironmentVariables(
    'DATABASE_HOST', 
    'DATABASE_PORT', 
    'MYSQL_USERNAME', 
    'MYSQL_PASSWORD', 
    'DATABASE_NAME'
)


# # Maybe a class for the constants
# _DATABASE_HOST = os.getenv('DATABASE_HOST')
# _DATABASE_PORT = os.getenv('DATABASE_PORT')
# _MYSQL_USERNAME = os.getenv('MYSQL_USERNAME')
# _MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
# _DATABASE_NAME = os.getenv('DATABASE_NAME')

# try:
#     assert _DATABASE_HOST and _DATABASE_PORT and _MYSQL_USERNAME and _MYSQL_PASSWORD and _DATABASE_NAME
# except AssertionError:
#     raise KeyError("Some important stuff is missing.")


connection = MySQLDatabase(
    database=env.DATABASE_NAME,
    host=env.DATABASE_HOST,
    port=int(env.DATABASE_PORT),
    user=env.MYSQL_USERNAME,
    passwd=env.MYSQL_PASSWORD
)

connection.connect()
