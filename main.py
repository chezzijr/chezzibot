"""Main entry point for ChezziBot."""

import asyncio
import signal
import sys
from contextlib import asynccontextmanager

import aiohttp
import discord
from discord.ext import commands

import config
from bot import ChezziBot
from logger import logger

@asynccontextmanager
async def create_bot():
    """Create and manage bot instance with proper cleanup."""
    async with aiohttp.ClientSession() as session:
        bot = ChezziBot(http_session=session)
        try:
            yield bot
        finally:
            await bot.close()

async def main():
    """Main bot runner with graceful shutdown."""
    # Set up signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, shutting down...")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        async with create_bot() as bot:
            logger.info("Starting ChezziBot...")
            await bot.start(config.TOKEN)
    except discord.LoginFailure:
        logger.error("Invalid bot token provided")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Bot shutdown requested")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot shutdown complete")
