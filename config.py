"""Configuration module for ChezziBot."""
import os
import discord
from pathlib import Path
from typing import Optional

# Load environment variables in development
if __debug__:
    from dotenv import load_dotenv
    load_dotenv()

def get_required_env(key: str, error_msg: Optional[str] = None) -> str:
    """Get a required environment variable or raise an error."""
    value = os.getenv(key)
    if value is None:
        raise ValueError(error_msg or f"Missing required environment variable: {key}")
    return value

# Bot configuration
TOKEN = get_required_env("TOKEN", "Bot token is required")
OWNER_ID = int(get_required_env("OWNER", "Owner ID is required"))
DEFAULT_PREFIX = "t."
VERSION = "2.0.0"

# File paths
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
FONTS_DIR = ASSETS_DIR / "fonts"
JSONS_DIR = ASSETS_DIR / "jsons"

# External tools
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")

# Discord configuration
INTENTS = discord.Intents.default()
INTENTS.message_content = True
INTENTS.guilds = True
INTENTS.guild_messages = True
INTENTS.members = False
INTENTS.presences = False

# Bot settings
MAX_FIELDS_PER_EMBED = 10
COMMAND_TIMEOUT = 300.0  # 5 minutes
MAX_MESSAGE_LENGTH = 2000

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_DPY_LOGGING = True
LOG_FORMAT = "[%(asctime)s] [%(name)s:%(funcName)s:%(lineno)d] %(levelname)s %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
