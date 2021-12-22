from peewee import MySQLDatabase

from utils import EnvironmentVariables


env = EnvironmentVariables(
    'DATABASE_HOST', 
    'DATABASE_PORT', 
    'MYSQL_USERNAME', 
    'MYSQL_PASSWORD', 
    'DATABASE_NAME'
)


connection = MySQLDatabase(
    database=env.DATABASE_NAME,
    host=env.DATABASE_HOST,
    port=int(env.DATABASE_PORT),
    user=env.MYSQL_USERNAME,
    passwd=env.MYSQL_PASSWORD
)

connection.connect()
