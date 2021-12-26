import asyncio
import time

import discord
from discord.components import SelectOption

from utils.strings import text_strings as ts
from utils.embed import WarningText
from model import GameRequirements


class PackageSelectOption(SelectOption):
    def __init__(self, game_package):
        self.game_package = game_package
        super().__init__(
            label=game_package.name,
            description=f'{game_package.price}₽'
        )


class PCPerformanceSelectOption(SelectOption):
    def __init__(self, pc_performance, emoji):
        self.pc_performance = pc_performance
        super().__init__(
            label=pc_performance.name,
            description=pc_performance.description,
            emoji=emoji
        )


class GameRequirementsSelectOption(SelectOption):
    def __init__(self, game_requirements, emoji):
        self.game_requirements = game_requirements
        super().__init__(
            label=game_requirements.name,
            description=game_requirements.description,
            emoji=emoji
        )

class GameGenreSelectOption(SelectOption):
    def __init__(self, game_genre):
        self.game_genre = game_genre
        super().__init__(
            label=game_genre.name
        )


class Dropdown(discord.ui.Select):
    def __init__(self, placeholder: str, options: SelectOption, min_values, max_values):
        super().__init__(
            placeholder=placeholder, 
            min_values=min_values, 
            max_values=max_values
        )

        self._filled = False
        self._options = {}
        self._is_ready = False

        for option in options:
            self._options[option.label] = option
            self.append_option(option)
        
    async def callback(self, interaction: discord.Interaction):
        self._is_ready = True
        self.disabled = True

    async def get_choices(self, timeout):
        execute_time = time.time()

        while not self._is_ready:
            if time.time() - execute_time > timeout:
                raise asyncio.TimeoutError
            await asyncio.sleep(0.2)
        
        return list(map(lambda gp: self._options[gp], self.values))


class PersonalDropdown(Dropdown):
    def __init__(self, user: discord.User, placeholder: str, options: SelectOption, min_values, max_values):
        super().__init__(
            placeholder=placeholder,
            options=options,
            min_values=min_values,
            max_values=max_values
        )

        self._user = user

    async def callback(self, interaction: discord.Interaction):
        if interaction.user == self._user:
            await super().callback(interaction)
        else:
            await interaction.response.send_message(embed=WarningText(ts.someone_elses_interaction_warning), ephemeral=True)


class OneChoiceDropdown(Dropdown):
    def __init__(self, placeholder: str, options: SelectOption):
        super().__init__(
            placeholder=placeholder, 
            options=options,
            min_values=1,
            max_values=1
        )
    
    async def get_choices(self, timeout):
        return (await super().get_choices(timeout))[0]


class PersonalOneChoiceDropdown(PersonalDropdown):
    def __init__(self, user, placeholder: str, options: SelectOption):
        super().__init__(
            user=user,
            placeholder=placeholder, 
            options=options,
            min_values=1,
            max_values=1
        )
    
    async def get_choices(self, timeout):
        return (await super().get_choices(timeout))[0]


class GamePackageChooseDropdown(PersonalOneChoiceDropdown):
    def __init__(self, user, options: PackageSelectOption):
        super().__init__(
            user=user,
            placeholder=ts.game_choose_placeholder,
            options=options
        )


# Можно было отнаследоваться от одного класса Performance, как изначально и планировалось в схеме, но надо торопиться
class PCPerformanceChooseDropdown(PersonalOneChoiceDropdown):
    def __init__(self, user, options: PCPerformanceSelectOption):
        super().__init__(
            user=user,
            placeholder=ts.pc_performance_choose_placeholder,
            options=options
        )


class GameRequirementsChooseDropdown(PersonalOneChoiceDropdown):
    def __init__(self, user, options: GameRequirementsSelectOption):
        super().__init__(
            user=user,
            placeholder=ts.game_requirements_choose_placeholder,
            options=options
        )


class PersonalGenreDropdown(PersonalDropdown):
    def __init__(self, user, options: GameGenreSelectOption):
        super().__init__(
            user=user,
            placeholder=ts.game_genres_choose_placeholder,
            options=options,
            min_values=1,
            max_values=3
        )
