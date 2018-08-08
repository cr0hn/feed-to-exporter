from slugify import slugify

from feed_to_wordpress.parsers import FeedInfo


def global_filter(feed: FeedInfo) -> dict:

    if not feed.content:
        content = [
            feed.body,
            "",
            f'<a target="_blank" href="{feed.link}">{feed.link}</a>',
            "",
            f"Fuente: <b>{feed.feed_source}</b>"
        ]

        #
        # Add some tags
        #
        feed.add_tag(slugify(feed.feed_source))

        return {
            "content": "\n".join(content)
        }
    else:
        return {}


def title_filter(field_value: str) -> dict:
    if field_value.isupper():
        return {"title": field_value.lower().capitalize()}
    else:
        return {}


GLOBAL_VALIDATOR = global_filter
INDIVIDUAL_VALIDATORS = {
    'title': title_filter
}
