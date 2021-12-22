import discord

class EmbedText(discord.Embed):
    def __init__(self, text: str):
        super().__init__(description=text)
