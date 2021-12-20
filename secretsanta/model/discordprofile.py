from peewee import PrimaryKeyField, BigIntegerField

from basemodel import BaseModel


class DiscordProfile(BaseModel):
    id = PrimaryKeyField(column_name='discord_profile_id')
    discord_id = BigIntegerField(column_name='discord_id')

    class Meta:
        table_name = 'DiscordProfile'
