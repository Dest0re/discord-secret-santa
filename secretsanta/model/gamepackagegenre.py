from peewee import PrimaryKeyField, ForeignKeyField

from basemodel import BaseModel
from gamepackage import GamePackage
from gamegenre import GameGenre


class GamePackageGenre(BaseModel):
    id = PrimaryKeyField(column_name='game_package_id')
    game_package = ForeignKeyField(GamePackage, column_name='game_package_id')
    game_genre = ForeignKeyField(GameGenre, column_name='game_genre_id')

    class Meta:
        table_name = 'GamePackageGenre'
