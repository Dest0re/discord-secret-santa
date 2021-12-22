from peewee import PrimaryKeyField, TextField, ForeignKeyField

from .basemodel import BaseModel
from .performance import Performance


class GameRequirements(BaseModel):
    id = PrimaryKeyField(column_name='game_requirements_id')
    performance = ForeignKeyField(Performance, column_name='performance_id')
    name = TextField(column_name='game_requirements_name')

    class Meta:
        table_name = 'GameRequirements'


if __name__ == '__main__':
    print(GameRequirements.select().execute())