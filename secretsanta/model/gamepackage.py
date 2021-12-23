from peewee import PrimaryKeyField, ForeignKeyField, BigIntegerField, FloatField, TextField

from .basemodel import BaseModel
from .gamerequirements import GameRequirements


class GamePackage(BaseModel):
    id = PrimaryKeyField(column_name='game_package_id')
    requirements = ForeignKeyField(GameRequirements, column_name='game_requirements_id')
    steam_id = BigIntegerField(column_name='game_package_steam_id')
    price = FloatField(column_name='price')
    name = TextField(column_name='game_package_name')

    class Meta:
        table_name = 'GamePackage'
