import asyncio
from time import time

import discord
from discord.enums import ButtonStyle

from utils.embed import EmbedText
from utils.strings import text_strings as ts


class PersonalAcceptButton(discord.ui.Button):
        def __init__(self, member: discord.Member):
            self._member = member
            self._is_active = True

            super().__init__(
                style=ButtonStyle.green,
                emoji="✔️"
            )
        
        async def callback(self, interaction: discord.Interaction):
            if self._is_active:
                if interaction.user != self._member:
                    await interaction.response.send_message(embed=EmbedText(ts.someone_elses_interaction_warning), ephemeral=True)
                else:
                    self._is_active = False
                    self.disabled = True
        
        async def wait_for_accept(self, timeout=120):
            execute_time = time()
            while self._is_active:
                if time() - execute_time >= timeout:
                    raise asyncio.TimeoutError
                await asyncio.sleep(0.1)


class PersonalYesOrNoButtonsView(discord.ui.View):
    def __init__(self, member: discord.Member):
        super().__init__()

        self._member = member
        self._result = None


    @discord.ui.button(style=ButtonStyle.green, emoji='✔️')
    async def _accept_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not self._member == interaction.user:
            await interaction.response.send_message(embed=EmbedText(ts.someone_elses_interaction_warning), ephemeral=True)
        else:
            await self._set_result(interaction, True)

    @discord.ui.button(style=ButtonStyle.red, emoji='❌')
    async def _deny_button_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
        if not self._member == interaction.user:
            await interaction.response.send_message(embed=EmbedText(ts.someone_elses_interaction_warning), ephemeral=True)
        else:
            await self._set_result(interaction, False)

    async def wait_for_result(self, timeout):
        start_time = time()
        while self._result == None:
            await asyncio.sleep(0.1)
            if time() - start_time >= timeout:
                raise asyncio.TimeoutError
        
        return self._result

    async def _set_result(self, interaction: discord.Interaction, result):
        self._result = result
        
        for children in self.children:
            children.disabled = True
