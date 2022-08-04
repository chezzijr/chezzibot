import discord
import random
from typing import Optional


def cmp(first: int, second: int) -> bool | None:
    """
    Compare two choices if second beats first
    1: rock
    2: paper
    3: scissor
    """
    if first == 1 and second == 3:
        return False

    if first == second:
        return None

    return first < second


def name(choice: int) -> str:
    match choice:
        case 1:
            return "Rock"
        case 2:
            return "Paper"
        case 3:
            return "Scissors"


class RPS(discord.ui.View):
    def __init__(self, ctx, first: discord.Member, second: Optional[discord.Member] = None):
        super().__init__()

        self.players = [
            first, ctx.me] if second is None else [first, second]
        self.choices = [
            None, random.randint(1, 3)] if second is None else [
            None, None]

    def get_index(self, user):
        return self.players.index(user)

    async def endgame(self, i: discord.Interaction):
        self.stop()
        for item in self.children:
            item.disabled = True
        res = cmp(self.choices[0], self.choices[1])
        if res is None:
            return await i.response.edit_message(
                content=f"It's a tie. Both chose **{name(self.choices[0])}**",
                view=self)
        if res:
            w, l = self.players[1], self.players[0]
            wc, lc = self.choices[1], self.choices[0]
        else:
            w, l = self.players[0], self.players[1]
            wc, lc = self.choices[0], self.choices[1]

        await i.response.edit_message(
            content=(f"`{w.display_name}` chose **{name(wc)}** and won, "
                     f"`{l.display_name}` chose **{name(lc)}** and lost"),
            view=self)

    @discord.ui.button(label="Rock", style=discord.ButtonStyle.blurple)
    async def rock(self, i: discord.Interaction, btn: discord.Button):
        idx = self.get_index(i.user)
        self.choices[idx] = 1

        if all(self.choices):
            return await self.endgame(i)

        await i.response.defer()

    @discord.ui.button(label="Paper", style=discord.ButtonStyle.gray)
    async def paper(self, i: discord.Interaction, btn: discord.Button):
        idx = self.get_index(i.user)
        self.choices[idx] = 2

        if all(self.choices):
            return await self.endgame(i)

        await i.response.defer()

    @discord.ui.button(label="Scissors", style=discord.ButtonStyle.success)
    async def scissors(self, i: discord.Interaction, btn: discord.Button):
        idx = self.get_index(i.user)
        self.choices[idx] = 3

        if all(self.choices):
            return await self.endgame(i)

        await i.response.defer()

    async def interaction_check(self, i: discord.Interaction) -> bool:
        return i.user in self.players
