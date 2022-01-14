import random

import discord
from discord.ext import commands

from model import User, UserPreferredGenre, GameGenre, PCPerformance, GameRequirements, Performance, GamePackageGenre, GamePackage, Present
from utils.environmentvariables import EnvironmentVariables
from steammarket import SteamStore
from utils.embed import ErrorText, SuccessText, WarningText, DebugText, EmbedText
from utils.strings import text_strings as ts


env = EnvironmentVariables('STEAM_TOKEN', 'STEAM_LOGIN', 'STEAM_PASSWORD')

steam = SteamStore(env.STEAM_LOGIN, env.STEAM_PASSWORD, env.STEAM_TOKEN)


class CannotPresentToAuthor(Exception):
    pass


class Presentable:
    async def present_to(self, user):
        pass


class LocalUser:
    def __init__(self, user: User):
        self._model_user = user
        self._presented_games = []
        self._steam_games = steam.user_games_sync(self._model_user.steam_profile.steam_id64)
    
    def __str__(self):
        return f'<LocalUser: performance={self.performance} gift_price={self.gift_price} games=[{", ".join(map(str, self.presented_games))}]>'
    
    def __repr__(self):
        return self.__str__()
    
    @property
    def performance(self):
        if self._model_user.pc_performance:
            return self._model_user.pc_performance.performance.id
        else:
            return None

    @property
    def all_games(self):
        return [game.game.app_id for game in self.presented_games] + self._steam_games
    
    @property
    def genres(self):
        model_genres = (
            GameGenre
            .select()
            .join(UserPreferredGenre)
            .where(UserPreferredGenre.user == self._model_user)
            .execute()
        )

        return list(model_genres)
    
    @property
    def presented_games(self):
        return self._presented_games

    @property
    def presents_id(self):
        return map(lambda p: p.presents_id, self._presented_games)
    
    @property
    def gift_price(self):
        return sum(map(lambda g: g.price, self._presented_games))

    @property
    def model_user(self):
        return self._model_user

    def present_me(self, present: Presentable):
        present.present_to(self)


class GamePresent(Presentable):
    def __init__(self, present: Present):
        self._model_present = present

    def __str__(self):
        return f'<GamePresent price={self.price} requirements={self.requirements}>'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    @property
    def presenter(self):
        return self._model_present.user
    
    @property
    def game(self):
        return self._model_present.game_package
    
    @property
    def message(self):
        return self._model_present.comment

    @property
    def requirements(self):
        if self._model_present.game_package.requirements:
            return self._model_present.game_package.requirements.performance.id
        else:
            return None

    @property
    def name(self):
        return self.game.name

    @property
    def price(self):
        return self._model_present.game_package.price

    @property
    def genres(self):
        model_genres = (
            GameGenre
            .select()
            .join(GamePackageGenre)
            .where(GamePackageGenre.game_package == self.game)
            .execute()
        )

        return list(model_genres)
    
    @property
    def app_id(self):
        return self._model_present.game_package.app_id
    
    def present_to(self, user: LocalUser):
        if self.presenter == user:
            raise CannotPresentToAuthor

        user._presented_games.append(self)    


class GamePresentBundle(Presentable):
    def __init__(self, *args: GamePresent):
        self._presents = args

    def __str__(self):
        return f'<GamePresentBundle price={self.price} requirements={self.requirements} presents=[{", ".join(map(str, self.presents))}]>'

    def __repr__(self) -> str:
        return self.__str__()

    @property
    def presents(self):
        return self._presents
    
    @property
    def presenter(self):
        return self._presents[0].presenter
    
    @property
    def name(self):
        return ' + '.join(map(lambda g: g.name, self._presents))
    
    @property
    def price(self):
        return sum(map(lambda g: g.price, self._presents))
    
    @property
    def requirements(self):
        return max(map(lambda g: g.requirements if g.requirements else 0, self._presents))
    
    @property
    def genres(self):
        _genres = set()
        for game in self._presents:
            _genres |= set(game.genres)

        return list(_genres)

    @property
    def presents_id(self):
        return list(map(lambda p: p.game.steam_id, self.presents))
 
    @property
    def message(self):
        return "\n\n".join(map(lambda p: f'> {p.message}', self._presents))

    def present_to(self, user: LocalUser):
        for present in self.presents:
            present.present_to(user)


class Shuffler:
    def __init__(self, users, presents):
        self._users = users
        self._presents = presents

        self._average_gift_price = sum(map(lambda p: p.price, self._presents)) / len(self._users)

    @classmethod
    def _count_relevance(cls, game, user):
        relevance = 0

        if user.performance and game.requirements:
            if user.performance == game.requirements:
                relevance += 0.7
            elif user.performance > game.requirements:
                relevance += 0.5
            else:
                relevance -= 0.1
        else:
            relevance += 1.5

        if user.genres and game.genres:
            coefficient = 0.3 / len(game.genres)
            relevance += coefficient * len(set(user.genres) and set(game.genres))
        else:
            relevance += 0.15

        return relevance
    
    async def shuffle(self):
        lower_coefficient = 5
        while True:
            if not self._presents:
                break

            if lower_coefficient == -1:
                break
            
            user_list = [user for user in self._users if user.gift_price < self._average_gift_price - (100 * lower_coefficient)]

            if not user_list:
                lower_coefficient -= 1
                continue
            
            random.shuffle(user_list)

            for user in user_list:
                print('начали')
                games_for_user = sorted(
                    (game for game in self._presents if (
                        game.presenter != user.model_user and
                        len(set(map(lambda p: p.game.app_id, game.presents)) & set(user.all_games)) == 0
                    )),
                    key=lambda g: self._count_relevance(g, user),
                    reverse=True
                )[:3]
                print('закончили')

                if not games_for_user:
                    break

                game = random.choice(games_for_user)

                game.present_to(user)

                self._presents.remove(game)


class PresentBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        self._is_ready = False

        self._users = []
        self._presents = []
        
        presents = (
            Present
            .select()
            .where(Present.paid == True)
        )

        db_users = []

        for present in presents:
            if present.user not in db_users:
                db_users.append(present.user)
            
            if present.id == 103:
                continue

            if present.id == 102:
                _presents = map(GamePresent, (present, Present.get_by_id(103)))
            else:
                _presents = (GamePresent(present),)

            self._presents.append(GamePresentBundle(*_presents))

        for user in db_users:
            self._users.append(LocalUser(user))

        super().__init__(*args, **kwargs)

    def generate_final_embed(self, user):
        game_text = ''

        for present in user.presented_games:
            game_text += f'**{present.name}** за {present.price}₽\n'
            game_text += f'{present.message}\n\n'

        return EmbedText(ts.final_embed.format(presented_games=game_text))

    async def on_ready(self):
        if not self._is_ready:
            self._is_ready = True
        else:
            return
        
        print(f'Logged in Discord as {self.user}')

        await steam.login()

        await self.shuffle_games()

    async def shuffle_games(self):
        shuffler = Shuffler(self._users, self._presents)

        await shuffler.shuffle()

        with open('gifts.txt', 'w', encoding='utf-8') as f:
            for user in shuffler._users:
                f.write(f'({user.gift_price}) {user.model_user.discord_profile.discord_id} | {user.model_user.steam_profile.steam_id64}\n')

                for present in user.presented_games:
                    f.write(f'{present.price} : {present.presenter.discord_profile.discord_id} : {present.game.name} : [{present.message}]\n')

                f.write(f'===========================\n\n')

        await self.finally_present(shuffler._users)

    
    async def finally_present(self, users_with_presents):
        for user in users_with_presents:
            discord_user = await self.fetch_user(user.model_user.discord_profile.discord_id)
            
            for present in user.presented_games:
                await steam.buy_gifts((present._model_present.game_package.steam_id,), user.model_user.steam_profile.steam_id32, 'Дорогой друг', present.message, 'Тайный Санта')
                pass

            if discord_user:
                await discord_user.send(embed=self.generate_final_embed(user))
