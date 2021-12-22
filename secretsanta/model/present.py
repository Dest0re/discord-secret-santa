from peewee import PrimaryKeyField, ForeignKeyField

from .basemodel import BaseModel
from .user import User
from .gamepackage import GamePackage


class Present(BaseModel):
    id = PrimaryKeyField(column_name='present_id')
    user = ForeignKeyField(User, column_name='user_id')
    game_package = ForeignKeyField(GamePackage, column_name='game_package_id')

    class Meta:
        table_name = 'Present'
