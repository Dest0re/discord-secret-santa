from utils import EnvironmentVariables
from discordclient import bot
from model import PCPerformance

bot_env = EnvironmentVariables('DISCORD_BOT_TOKEN')


if __name__ == '__main__':
    bot.run(bot_env.DISCORD_BOT_TOKEN)
