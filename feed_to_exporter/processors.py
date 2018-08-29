from .model import AbstractAppConfig
from .parsers import parse_entries


def process_feed(config: AbstractAppConfig):

    #
    # Load mapping file
    #
    for feed_entry in parse_entries(config):
        config.push(feed_entry)


__all__ = ("process_feed", )
