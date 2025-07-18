"""Modern pagination utilities using discord.py 2.x Views."""


import asyncio
from abc import ABC, abstractmethod
from typing import Any, Generic, Optional, TypeVar, Union

import discord
from discord.ext import commands

from logger import logger

T = TypeVar('T')

class PaginationSource(ABC, Generic[T]):
    """Abstract base class for pagination sources."""
    
    def __init__(self, entries: list[T], *, per_page: int = 10):
        self.entries = entries
        self.per_page = per_page
    
    @property
    def max_pages(self) -> int:
        """Get the maximum number of pages."""
        return (len(self.entries) + self.per_page - 1) // self.per_page
    
    def get_page_entries(self, page: int) -> list[T]:
        """Get entries for a specific page."""
        start = page * self.per_page
        end = start + self.per_page
        return self.entries[start:end]
    
    @abstractmethod
    async def format_page(self, page: int, entries: list[T]) -> Union[str, discord.Embed]:
        """Format a page for display."""
        pass

class EmbedPaginationSource(PaginationSource[T]):
    """Pagination source that formats pages as embeds."""
    
    def __init__(
        self,
        entries: list[T],
        *,
        per_page: int = 10,
        title: str = "Pagination",
        color: discord.Color = discord.Color.blue(),
        formatter: Optional[callable] = None
    ):
        super().__init__(entries, per_page=per_page)
        self.title = title
        self.color = color
        self.formatter = formatter or str
    
    async def format_page(self, page: int, entries: list[T]) -> discord.Embed:
        """Format entries as an embed."""
        embed = discord.Embed(
            title=self.title,
            color=self.color,
            description="\n".join(self.formatter(entry) for entry in entries)
        )
        
        if self.max_pages > 1:
            embed.set_footer(text=f"Page {page + 1}/{self.max_pages}")
        
        return embed

class PaginationView(discord.ui.View):
    """A view for paginating through content."""
    
    def __init__(
        self,
        source: PaginationSource,
        *,
        author: Union[discord.User, discord.Member],
        timeout: float = 300.0
    ):
        super().__init__(timeout=timeout)
        self.source = source
        self.author = author
        self.current_page = 0
        self.message: Optional[discord.Message] = None
        
        # Update button states
        self._update_buttons()
    
    def _update_buttons(self) -> None:
        """Update button states based on current page."""
        if self.source.max_pages <= 1:
            # Hide all buttons if there's only one page
            for item in self.children:
                item.disabled = True
            return
        
        # Update individual buttons
        self.first_page.disabled = self.current_page == 0
        self.previous_page.disabled = self.current_page == 0
        self.next_page.disabled = self.current_page == self.source.max_pages - 1
        self.last_page.disabled = self.current_page == self.source.max_pages - 1
    
    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Check if the user can interact with this view."""
        if interaction.user != self.author:
            await interaction.response.send_message(
                "❌ You cannot use this pagination menu.",
                ephemeral=True
            )
            return False
        return True
    
    async def _show_page(self, interaction: discord.Interaction, page: int) -> None:
        """Show a specific page."""
        self.current_page = max(0, min(page, self.source.max_pages - 1))
        self._update_buttons()
        
        entries = self.source.get_page_entries(self.current_page)
        content = await self.source.format_page(self.current_page, entries)
        
        if isinstance(content, discord.Embed):
            await interaction.response.edit_message(embed=content, view=self)
        else:
            await interaction.response.edit_message(content=content, view=self)
    
    @discord.ui.button(emoji="⏮️", style=discord.ButtonStyle.secondary)
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the first page."""
        await self._show_page(interaction, 0)
    
    @discord.ui.button(emoji="⏪", style=discord.ButtonStyle.secondary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the previous page."""
        await self._show_page(interaction, self.current_page - 1)
    
    @discord.ui.button(emoji="🗑️", style=discord.ButtonStyle.danger)
    async def stop_pagination(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Stop the pagination."""
        self.stop()
        for item in self.children:
            item.disabled = True
        await interaction.response.edit_message(view=self)
    
    @discord.ui.button(emoji="⏩", style=discord.ButtonStyle.secondary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the next page."""
        await self._show_page(interaction, self.current_page + 1)
    
    @discord.ui.button(emoji="⏭️", style=discord.ButtonStyle.secondary)
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        """Go to the last page."""
        await self._show_page(interaction, self.source.max_pages - 1)
    
    async def on_timeout(self) -> None:
        """Handle view timeout."""
        for item in self.children:
            item.disabled = True
        
        if self.message:
            try:
                await self.message.edit(view=self)
            except discord.HTTPException:
                pass
    
    async def start(self, ctx: commands.Context) -> None:
        """Start the pagination."""
        if self.source.max_pages == 0:
            await ctx.send("❌ No entries to paginate.")
            return
        
        entries = self.source.get_page_entries(0)
        content = await self.source.format_page(0, entries)
        
        if isinstance(content, discord.Embed):
            self.message = await ctx.send(embed=content, view=self)
        else:
            self.message = await ctx.send(content=content, view=self)

async def paginate(
    ctx: commands.Context,
    entries: list[T],
    *,
    per_page: int = 10,
    title: str = "Pagination",
    formatter: Optional[callable] = None
) -> None:
    """Quick pagination helper function."""
    source = EmbedPaginationSource(
        entries,
        per_page=per_page,
        title=title,
        formatter=formatter
    )
    
    view = PaginationView(source, author=ctx.author)
    await view.start(ctx)
