from peewee import PrimaryKeyField, TextField

from .basemodel import BaseModel


class GameGenre(BaseModel):
    id = PrimaryKeyField(column_name='game_genre_id')
    genre_name = TextField(column_name='genre_name')

    class Meta:
        table_name = 'GameGenre'
