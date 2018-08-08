from .model import AppConfig
from .parsers import parse_entries
from .wordpress_queries import publish_post


def process_feed(config: AppConfig):
    #
    # Load mapping file
    #
    for feed_entry in parse_entries(config):
        publish_post(feed_entry, config)


__all__ = ("process_feed", )
