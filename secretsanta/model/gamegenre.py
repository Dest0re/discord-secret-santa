from peewee import PrimaryKeyField, TextField

from .basemodel import BaseModel


class GameGenre(BaseModel):
    id = PrimaryKeyField(column_name='game_genre_id')
    name = TextField(column_name='game_genre_name')

    class Meta:
        table_name = 'GameGenre'
