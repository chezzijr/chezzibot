# I got this from media forge bot. Check them out https://github.com/HexCodeFFF/mediaforge

import logging
import coloredlogs
import config

logger = logging.getLogger(__name__)

field_styles = {
    'levelname': {'bold': True, 'color': 'blue'},
    'asctime': {'color': 2},
    'filename': {'color': 6},
    'funcName': {'color': 5},
    'lineno': {'color': 13}
}
level_styles = coloredlogs.DEFAULT_LEVEL_STYLES
loglevel = logging.DEBUG

coloredlogs.install(level=loglevel, fmt='[%(asctime)s] [%(filename)s:%(funcName)s:%(lineno)d] '
                                        '%(levelname)s %(message)s',
                    datefmt='%d/%m/%Y %I:%M:%S %p', field_styles=field_styles, level_styles=level_styles, logger=logger)

if hasattr(config, "DPY_LOGGING") and config.DPY_LOGGING:
    dlogger = logging.getLogger('discord')
    dlogger.setLevel(logging.DEBUG)
    handler = logging.FileHandler(
        filename='discord.log', encoding='utf-8', mode='w+')
    handler.setFormatter(logging.Formatter('[%(asctime)s] [%(filename)s:%(funcName)s:%(lineno)d] '
                                           '%(levelname)s %(message)s'))
    handler.setLevel(logging.DEBUG)
    dlogger.addHandler(handler)
