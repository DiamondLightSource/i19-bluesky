import logging

from dodal.log import LOGGER as dodal_logger

LOGGER = logging.getLogger("i19_bluesky")
LOGGER.setLevel(logging.DEBUG)
LOGGER.parent = dodal_logger
