from peewee import PrimaryKeyField, BigIntegerField

from .basemodel import BaseModel


class SteamProfile(BaseModel):
    id = PrimaryKeyField(column_name='steam_profile_id')
    steam_id32 = BigIntegerField(column_name='steam_id32')
    steam_id64 = BigIntegerField(column_name='steam_id64')

    class Meta:
        table_name = 'SteamProfile'
