import asyncio
import config
from log import logger
from discord.ext import commands
from bot import ChezziBot
from aiohttp import ClientSession


async def main():
    logger.info("Initializing bot...")

    async with ClientSession() as session:
        async with ChezziBot(
            http_session=session,
            command_prefix=commands.when_mentioned_or(config.DEFAULT_PREFIX),
            help_command=None,
            owner=config.OWNER,
            intents=config.INTENTS,
        ) as bot:
            await bot.start(config.TOKEN)

if __name__ == "__main__":
    asyncio.run(main())
