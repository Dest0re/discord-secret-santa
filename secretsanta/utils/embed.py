import discord

class EmbedText(discord.Embed):
    def __init__(self, text: str, color=0xFFFFFF):
        super().__init__(description=text, color=color)


class ErrorText(EmbedText):
    def __init__(self, text: str):
        super().__init__(text, color=0xFF0000)


class TitledText(discord.Embed):
    def __init__(self, title: str, text: str, color=0xFFFFFF):
        super().__init__(title=title, description=text, color=color)


class DebugText(TitledText):
    def __init__(self, text: str):
        super().__init__('Это дебаг, он тут ненадолго', text, color=0xFF00FF)
