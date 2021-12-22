from peewee import PrimaryKeyField

from .basemodel import BaseModel


class Performance(BaseModel):
    id = PrimaryKeyField()

    class Meta:
        table_name = 'Performance'
