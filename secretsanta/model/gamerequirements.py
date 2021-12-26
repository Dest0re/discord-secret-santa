from peewee import PrimaryKeyField, TextField, ForeignKeyField, BigIntegerField

from .basemodel import BaseModel
from .performance import Performance


class GameRequirements(BaseModel):
    id = PrimaryKeyField(column_name='game_requirements_id')
    performance = ForeignKeyField(Performance, column_name='performance_id')
    name = TextField(column_name='requirements_name')
    description = TextField(column_name='requirements_description')
    emoji_id = BigIntegerField(column_name='emoji_id')

    class Meta:
        table_name = 'GameRequirements'


if __name__ == '__main__':
    print(GameRequirements.select().execute())