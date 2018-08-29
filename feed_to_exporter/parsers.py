import datetime
import feedparser

from typing import Iterable

from .model import AbstractAppConfig


def parse_entries(config: AbstractAppConfig) -> Iterable[dict]:
    d = feedparser.parse(config.feed_source)
    source = d['feed']['title']
    print(f"[*] Parsed feed source: '{source}'")

    for i, new in enumerate(d['entries'], start=1):
        pp = new.published_parsed
        date = datetime.datetime(
            pp.tm_year,
            pp.tm_mon,
            pp.tm_mday,
            pp.tm_hour,
            pp.tm_min,
            pp.tm_sec).strftime(
            "%Y-%m-%dT%H:%M:%S")

        feed_result = dict(raw_feed_info=new,
                           title=new['title'],
                           date=date,
                           feed_source=source)

        print(f"<*> Processing entry: '{i}' - {feed_result['title']}")

        # ---------------------------------------------------------------------
        # Map input feed key to output Wordpress json format
        # ---------------------------------------------------------------------
        if "mapping" in config.mapping_json:
            for out_key, in_key in config.mapping_json['mapping'].items():
                feed_result[out_key] = new.get(in_key)

        # ---------------------------------------------------------------------
        # Attach fixed fields
        # ---------------------------------------------------------------------
        if hasattr(config.mapping_obj, "fixed"):
            for k, fixed_values in config.mapping_json['fixed'].items():

                # if not isinstance(fixed_values, list):
                #     list_fixed_values = [fixed_values]
                # else:
                #     list_fixed_values = fixed_values
                feed_result[k] = fixed_values

        # Yield the content ready to send to Wordpress
        yield feed_result


__all__ = ( "parse_entries", )

