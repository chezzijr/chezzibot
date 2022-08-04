from __future__ import annotations
import discord
from typing import Any, Callable, Coroutine, Generic, Optional, TypeVar
from discord import ui
from discord.ext import commands, menus

T = TypeVar('T')
EntryType = str | discord.Embed | dict[str, Any]
FormatType = Callable[[menus.MenuPages, T],
                      Coroutine[Any, Any, EntryType]]


class MenuPages(ui.View, menus.MenuPages, Generic[T]):
    def __init__(self, source: MenuSource[T]):
        super().__init__(timeout=60)
        self._source = source
        self.current_page = 0
        self.ctx: commands.Context = None
        self.message: discord.Message = None

    async def start(self, ctx: commands.Context, *, channel=None, wait=False):
        # We wont be using wait/channel, you can implement them yourself. This is to match the MenuPages signature.
        await self._source._prepare_once()
        self.ctx = ctx
        self.message = await self.send_initial_message(ctx, ctx.channel)

    async def _get_kwargs_from_page(self, page):
        """This method calls ListPageSource.format_page class"""
        value = await super()._get_kwargs_from_page(page)
        if 'view' not in value:
            value.update({'view': self})
        return value

    async def interaction_check(self, interaction: discord.Interaction):
        """Only allow the author that invoke the command to be able to use the interaction"""
        return interaction.user == self.ctx.author

    async def show_page(self, page_number: int, i: discord.Interaction):
        page = await self._source.get_page(page_number)
        self.current_page = page_number
        kwargs = await self._get_kwargs_from_page(page)
        await i.response.edit_message(**kwargs)

    async def show_checked_page(self, page_number, i):
        max_pages = self._source.get_max_pages()
        try:
            if max_pages is None:
                # If it doesn't give maximum pages, it cannot be checked
                await self.show_page(page_number, i)
            elif max_pages > page_number >= 0:
                await self.show_page(page_number, i)
        except IndexError:
            # An error happened that can be handled, so ignore it.
            pass

    # This is extremely similar to Custom MenuPages(I will not explain these)
    @ui.button(emoji='⏮', style=discord.ButtonStyle.blurple)
    async def first_page(self, interaction: discord.Interaction, button: discord.Button):
        await self.show_page(0, interaction)

    @ui.button(emoji='⏪', style=discord.ButtonStyle.blurple)
    async def before_page(self, interaction: discord.Interaction, button: discord.Button):
        await self.show_checked_page(self.current_page - 1, interaction)

    @ui.button(emoji='⏹', style=discord.ButtonStyle.blurple)
    async def stop_page(self, interaction: discord.Interaction, button: discord.Button):
        self.stop()
        self.children.clear()
        await self.show_page(self.current_page, interaction)

    @ui.button(emoji='⏩', style=discord.ButtonStyle.blurple)
    async def next_page(self, interaction: discord.Interaction, button: discord.Button):
        await self.show_checked_page(self.current_page + 1, interaction)

    @ui.button(emoji='⏭', style=discord.ButtonStyle.blurple)
    async def last_page(self, interaction: discord.Interaction, button: discord.Button):
        await self.show_page(self._source.get_max_pages() - 1, interaction)


class MenuSource(menus.ListPageSource, Generic[T]):
    def __init__(self, entries: list[T], *, per_page: int, format: Optional[FormatType] = None):
        super().__init__(entries, per_page=per_page)
        self.fmt = format if format is not None else super().format_page

    async def format_page(self, menu: MenuPages, page: T):
        return await self.fmt(menu, page)
