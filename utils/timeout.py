"""Enhanced timeout view with better styling."""

import discord
from typing import Optional

class TimeoutView(discord.ui.View):
    """A view that shows when something has timed out."""
    
    def __init__(self, message: Optional[str] = None):
        super().__init__(timeout=None)  # This view doesn't timeout
        
        self.add_item(discord.ui.Button(
            style=discord.ButtonStyle.secondary,
            label=message or "Timed Out",
            emoji="⏰",
            disabled=True
        ))
