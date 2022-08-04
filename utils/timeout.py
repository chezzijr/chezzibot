import discord


class Timeout(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(
            style=discord.ButtonStyle.gray,
            label="Timeout",
            emoji="⚠",
            disabled=True
        ))
