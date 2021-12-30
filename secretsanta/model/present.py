from peewee import PrimaryKeyField, ForeignKeyField, BooleanField, TextField

from .basemodel import BaseModel
from .user import User
from .gamepackage import GamePackage


class Present(BaseModel):
    id = PrimaryKeyField(column_name='present_id')
    user = ForeignKeyField(User, column_name='user_id')
    game_package = ForeignKeyField(GamePackage, column_name='game_package_id')
    paid = BooleanField(column_name='is_paid')
    comment = TextField(column_name='comment', null=True)

    class Meta:
        table_name = 'Present'
