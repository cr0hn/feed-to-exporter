from slugify import slugify

from feed_to_exporter.model import AbstractFeedInfo


def global_filter(feed: AbstractFeedInfo) -> dict:

    results = {}

    if feed.app_config.mode == "wordpress":

        if not feed.content:
            content = [
                feed.body,
                "<br />",
                f'<a target="_blank" href="{feed.link}">{feed.link}</a>',
                "",
                f"Fuente: <b>{feed.feed_source}</b>"
            ]

            #
            # Add some tags
            #
            feed.add_tag(slugify(feed.feed_source))

            results["content"] = "\n".join(content)

        if feed.feed_source:
            results['slug'] = f"{feed.date.split('T')[0]}-" \
                              f"{slugify(feed.feed_source)}-{slugify(feed.title)}"

    return results


def title_filter(field_value: str) -> dict:
    if field_value.isupper():
        return {"title": field_value.lower().capitalize()}
    else:
        return {}


GLOBAL_VALIDATOR = global_filter
INDIVIDUAL_VALIDATORS = {
    'title': title_filter
}
