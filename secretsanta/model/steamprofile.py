from peewee import PrimaryKeyField, BigIntegerField

from .basemodel import BaseModel


class SteamProfile(BaseModel):
    id = PrimaryKeyField(column_name='steam_profile_id')
    steam_id = BigIntegerField(column_name='steam_id')

    class Meta:
        table_name = 'SteamProfile'
