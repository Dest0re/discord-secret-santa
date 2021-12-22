from peewee import Model

from .connection import connection


class BaseModel(Model):
    class Meta:
        database = connection
