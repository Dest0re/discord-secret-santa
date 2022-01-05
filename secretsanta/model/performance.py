from peewee import PrimaryKeyField

from .basemodel import BaseModel


class Performance(BaseModel):
    id = PrimaryKeyField(column_name='performance_id')

    class Meta:
        table_name = 'Performance'
