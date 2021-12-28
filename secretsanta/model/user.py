from peewee import PrimaryKeyField, ForeignKeyField

from .basemodel import BaseModel
from .pcperformance import PCPerformance
from .steamprofile import SteamProfile
from .discordprofile import DiscordProfile


class User(BaseModel):
    id = PrimaryKeyField(column_name='user_id')
    discord_profile = ForeignKeyField(DiscordProfile, column_name='discord_profile_id')
    steam_profile = ForeignKeyField(SteamProfile, column_name='steam_profile_id', null=True)
    pc_performance = ForeignKeyField(PCPerformance, column_name='pc_performance_id', null=True)

    class Meta:
        table_name = 'User'


if __name__ == '__main__':
    print(tuple(User.select().execute()))

