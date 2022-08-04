import json
import os
import discord

if __debug__:
    from dotenv import load_dotenv as _load_env
    _load_env()


def _try_load(map, key, msg=None):
    val = map.get(key)
    if val is None:
        if msg is None:
            msg = f"No key named {key} in {map}"
        raise ValueError(msg)
    return val


# Load from environment variables
TOKEN: str = _try_load(os.environ, "TOKEN")
OWNER: str = _try_load(os.environ, 'OWNER')

DEFAULT_PREFIX: str = "t."
VERSION: str = "0.1.0"

# If ffmpeg is in environment variable
# Else you can specify your own ffmpeg executable path
FFMPEG_PATH: str = "ffmpeg"

# Intents configs
INTENTS = discord.Intents.all()
INTENTS.presences = False
INTENTS.members = False

# Embed configs
MAX_FIELDS_PER_EMBED = 10

# Logger config
DPY_LOGGING = True
