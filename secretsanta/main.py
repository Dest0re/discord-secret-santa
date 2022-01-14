from enum import Enum
from utils import EnvironmentVariables
from model import PCPerformance


class WorkModes(Enum):
    collecting=1,
    preparing=2,
    back_gifting=3,
    goodbye=4


WORK_MODE = WorkModes.goodbye

if WORK_MODE == WorkModes.collecting:
    from discordclient import bot
elif WORK_MODE == WorkModes.preparing:
    from discordclient.friendrequests import SendFriendRequestsBotClient
    bot = SendFriendRequestsBotClient()
elif WORK_MODE == WorkModes.back_gifting:
    from discordclient.giftingconcept import PresentBot
    bot = PresentBot()
elif WORK_MODE == WorkModes.goodbye:
    from discordclient.goodbyemessage import GoodByeBot
    bot = GoodByeBot()


bot_env = EnvironmentVariables('DISCORD_BOT_TOKEN')


if __name__ == '__main__':
    bot.run(bot_env.DISCORD_BOT_TOKEN)
    pass
