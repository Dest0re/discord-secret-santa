import discord
from discord.ext import commands
from peewee import fn

from utils.embed import TitledText
from model import User, DiscordProfile, Present, GamePackage


user_list = ['<@368953518196785152>', '<@332938926375305218>', '<@360858402911420416>']


class GoodByeBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self._is_ready = False

        super().__init__(*args, **kwargs)

    async def on_ready(self):
        if not self._is_ready:
            print(f'Logged in Discord as {self.user}')

            self._is_ready = True

            query = (
                User
                .select()
                .join(Present)
                .join(GamePackage)
                .where(Present.paid == True)
                .group_by(User.id)
                .having(fn.SUM(GamePackage.price) >= 500, User.discord_profile != None)
            )

            for user in set(query):
                
                discord_user = await self.fetch_user(user.discord_profile.discord_id)

                if discord_user:
                    embed_text = (
                        """Наконец-то!

                        Друзья, пусть не без проблем и выйдя за всякие сроки, но мы закончили наш ивент "Тайный Санта"!!!
                        
                        Мы очень рады, что всё наконец-то закончилось, потому что вы даже не представляете, сколько нервов и сил было потрачено на разработку и поддержание бота и хост ивента. Не говоря уже о денежной волоките и расходах, без которых было никуда!
                        
                        Тем не менее, мы искренне надеемся, что вам всё понравилось и что вы оказались довольны играми, которые прилетели вам в ответ.
                        
                        Важный момент! В связи со сложившейся ситуацией (а нас забанили в стиме до конца распродажи) многие игры подорожали кратно. И некоторые ребята не стали выбирать новые игры, а докинули деняк, чтобы всё-таки подарить старые. И можете поверить, это совсем не маленькие деньги.
                        Так что скажем им "Спасибо!": """ 
                        + ', '.join(user_list) + 
                        """!
                        
                        Спасибо и вам всем за участие в этом по сути экспериментальном ивенте!
                        Осталось разобраться, кому дарить печеньки? 🍪
                        
                        Для вас:

                        **Писали и обслуживали бота, проводили ивент**: 
                        <@350206214782582784>, <@141424884466057217> 
                        
                        **Рисовал боту аватарку**: <@332938926375305218> 
                        
                        **Подарил Вам игру**: *???*


                        С новым 2022 годом! До свидания!



                        Все участники ивента: 
                        """ 
                        + ', '.join(map(lambda u: f'<@{u.discord_profile.discord_id}>', query))
                    )

                    await discord_user.send(embed=TitledText('Ура!!!!!!', embed_text))
            
