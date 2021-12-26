from peewee import PrimaryKeyField, ForeignKeyField

from .basemodel import BaseModel
from .user import User
from .gamegenre import GameGenre


class UserPreferredGenre(BaseModel):
    id = PrimaryKeyField(column_name='user_preferred_genre_id')
    user = ForeignKeyField(User, column_name='user_id')
    genre = ForeignKeyField(GameGenre, column_name='game_genre_id')

    class Meta:
        table_name = 'UserPreferredGenre'
