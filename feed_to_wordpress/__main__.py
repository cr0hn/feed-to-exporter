import json
import base64
import logging
import os.path
import argparse
import requests
import datetime
import feedparser

from urllib.parse import urlparse
from types import SimpleNamespace

from slugify import slugify

log = logging.getLogger("f2w")


class FeedToWordpressException(Exception):
    pass


class AppConfig:

    REQUIRED_FIELDS_IN_MAPPING_FIELD = (
        'title',
        'content'
    )

    def __init__(self,
                 user: str,
                 app_auth: str,
                 feed: str,
                 filters_file: str,
                 wordpress_url: str,
                 mapping_path: str):
        self.feed = feed
        self.user = user
        self.app_auth = app_auth
        self.filters_file = os.path.abspath(filters_file)
        self.mapping_path = os.path.abspath(mapping_path)
        self.wordpress_host = wordpress_url

        #
        # Load filter file
        #
        if self.filters_file:
            g = {}
            exec(open(self.filters_file, "rb").read(), g)
            self.filters = g.get("FILTER_RULES", {})
            self.validation_rule = g.get("VALIDATION_FILTER", lambda **x: True)
        else:
            self.filters = {}
            self.validation_rule = lambda **x: True


        #
        # Some checks
        #
        if not self.wordpress_host.startswith("http"):
            raise FeedToWordpressException(
                "Invalid Wordpress URL. It must start with http/https")

        self._token: dict = None
        self._mapping_json: dict = None
        self._mapping_obj: SimpleNamespace = None
        self._wordpress_api: str = None

    def _calculate_api_token(self) -> dict:
        token = base64.standard_b64encode(
            f"{self.user}:{self.app_auth}".encode())
        headers = {'Authorization': f'Basic {token.decode()}'}

        return headers

    @property
    def token(self) -> dict:
        """Returns a HTTP header as dict with auth token inside"""
        if not self._token:
            self._token = self._calculate_api_token()
        return self._token

    @property
    def mapping_json(self) -> argparse.Namespace:
        if not self._mapping_json:
            # Load json
            try:
                loaded_mapping = json.load(open(self.mapping_path, "rb"))
            except IOError as e:
                raise FeedToWordpressException(
                    f"Can't find file {self.mapping_path}: {e}")
            except json.decoder.JSONDecodeError:
                raise FeedToWordpressException(
                    "Invalid format of JSON file. "
                    "Probably you have an error in the JSON format")
            else:

                # -------------------------------------------------------------
                # Check minimum required fields in mapping.json
                # -------------------------------------------------------------
                if "mapping" not in loaded_mapping:
                    raise FeedToWordpressException(
                        "You must specify, at least, a 'mapping' key entry in "
                        "mapping.json file"
                    )
                # -------------------------------------------------------------------------
                # Check minimum fields for 'mapping' key
                # -------------------------------------------------------------------------
                if not all(x in loaded_mapping['mapping']
                           for x in self.REQUIRED_FIELDS_IN_MAPPING_FIELD):
                    raise FeedToWordpressException(
                        f"Missing entry in mapping.json file. Required fields "
                        f"are: "
                        f"{','.join(self.REQUIRED_FIELDS_IN_MAPPING_FIELD)}")

                self._mapping_json = loaded_mapping

        return self._mapping_json

    @property
    def mapping_obj(self) -> SimpleNamespace:
        if not self._mapping_obj:
            temp = json.dumps(self.mapping_json)
            self._mapping_obj = json.loads(
                temp,
                object_hook=lambda d: SimpleNamespace(**d))
        return self._mapping_obj

    @property
    def wordpress_api_url(self):
        if not self._wordpress_api:
            scheme, host, *_ = urlparse(self.wordpress_host)
            self._wordpress_api = f"{scheme}://{host}/wp-json/wp/v2"

        return self._wordpress_api


# -------------------------------------------------------------------------
# Aux end-point
# -------------------------------------------------------------------------
def _post_with_url_already_exits(slug_title: str, config: AppConfig) -> bool:
    """
    Returns True if post already exits, False otherwise
    """
    response_draft = requests.get(
        f"{config.wordpress_api_url}/posts?slug={slug_title}&status=draft",
        headers=config.token)

    if not response_draft.json():
        response_published = requests.get(
            f"{config.wordpress_api_url}/"
            f"posts?slug={slug_title}&status=publish",
            headers=config.token)

        if not response_published.json():
            return False
        else:
            return True
    else:
        return True


def _get_or_create_tag_or_category(tag_or_category: str,
                                   name: str,
                                   config: AppConfig) -> str:
    """
    Returns tag Id of wordpress
    :param tag_or_category: possible values: tag|category
    :type tag_or_category: str

    """
    if tag_or_category not in ("tag", "category"):
        raise FeedToWordpressException(
            "Invalid value. Allowed values are: tag|category")

    if tag_or_category == "tag":
        endpoint = "tags"
    else:
        endpoint = "categories"

    response = requests.get(
        f"{config.wordpress_api_url}/{endpoint}",
        headers=config.token,
        json={"slug": name}
    )

    if response.json():
        return response.json()[0]['id']
    else:
        response = requests.post(
            f"{config.wordpress_api_url}/{endpoint}",
            headers=config.token,
            json={
                "name": name,
                "slug": name
            }
        )

        return response.json()['id']


# -------------------------------------------------------------------------
# TODO: los tags
# -------------------------------------------------------------------------
def publish_post(post_data: dict, config: AppConfig):
    # -------------------------------------------------------------------------
    # Check if already exits this post
    # -------------------------------------------------------------------------
    slug = post_data['slug']
    a = _post_with_url_already_exits(slug, config)

    print(f"    -> Checking if '{slug}' already exits")
    if not a:
        print(f"    -> Creating: Post with url '{slug}' doesn't exits")
        response = requests.post(f"{config.wordpress_api_url}/posts",
                                 headers=config.token,
                                 json=post_data)

        if str(response.status_code).startswith("20"):
            print(f"    -> Created: Post with url '{slug}' created")
        else:
            print(f"    !> Can't create post with url '{slug}'. "
                  f"Error: {response.json()['message']}")

    else:
        print(f"    i> Post with url '{slug}' already exits. Skipping...")


def parse_entries_entries(config: AppConfig):
    d = feedparser.parse(config.feed)
    source = d['feed']['title']

    for new in d['entries']:
        build_obj = {}

        # ---------------------------------------------------------------------
        # Only entries with summary-like will be processed
        # ---------------------------------------------------------------------
        if config.mapping_obj.mapping.content not in new:
            continue

        # ---------------------------------------------------------------------
        # Map input feed key to output Wordpress json format
        # ---------------------------------------------------------------------
        for out_key, in_key in config.mapping_json['mapping'].items():
            build_obj[out_key] = new.get(in_key)

        content = [
            build_obj['content'],
            "",
            f'<a target="_blank" href="{new["link"]}">{new["link"]}</a>',
            "",
            f"Fuente: <b>{source}</b>"
        ]

        build_obj['slug'] = slugify(build_obj['title'])
        build_obj['content'] = "\n".join(content)
        build_obj['date'] = datetime.datetime.now().strftime(
            "%Y-%m-%dT%H:%M:%S")
        build_obj['format'] = 'standard'
        build_obj['status'] = 'draft'
        build_obj['comment_status'] = 'closed'
        build_obj['ping_status'] = 'closed'

        # ---------------------------------------------------------------------
        # Attach fixed fields
        # ---------------------------------------------------------------------
        if hasattr(config.mapping_obj, "fixed"):
            for k, v in config.mapping_json['fixed'].items():

                if "tag" in k:
                    operation = "tag"
                elif "categories" in k:
                    operation = "category"
                else:
                    operation = None

                if operation:
                    build_obj[k] = []
                    for value in v:
                        build_obj[k].append(_get_or_create_tag_or_category(
                            operation,
                            value,
                            config
                        ))
                else:
                    build_obj[k] = v

        # ---------------------------------------------------------------------
        # Apply filters
        # ---------------------------------------------------------------------
        for key_name, key_function in config.filters.items():
            if key_name in build_obj:
                ret = key_function(build_obj[key_name])

                if not isinstance(ret, dict):
                    raise FeedToWordpressException(
                        f"Filter '{key_function.__name__}' returns invalid "
                        f"type: '{type(ret)}'. Only allowed type: dict"
                    )

                for k, v in ret.items():
                    #
                    # Checks returns types. Only allowed:
                    #
                    #   tags. categories, title, content
                    #
                    if k in ("tags", "categories", "title", "content"):
                        #
                        # Update value
                        #
                        build_obj[k] = v
                    else:
                        raise FeedToWordpressException(
                            f"Filter '{key_function.__name__}' "
                            f"returns invalid dictionary entry. Allowed:"
                            f"tags, categories, title, content")

        # ---------------------------------------------------------------------
        # Apply general validation rule
        # ---------------------------------------------------------------------
        if not config.validation_rule(**build_obj):
            pass

        yield build_obj


def process_feed(config: AppConfig):
    #
    # Load mapping file
    #
    for feed_entry in parse_entries_entries(config):
        print(f"[*] Processing title: {feed_entry['title']}")
        publish_post(feed_entry, config)


def main():
    parser = argparse.ArgumentParser(
        description='Parse feed and publish Wordpress post')
    parser.add_argument('feed', metavar='FEED_URL', type=str,
                        help='url to feed to parse')

    parser.add_argument('--wordpress-url', '-W',
                        dest='wordpress_url',
                        required=True,
                        help='wordpress url')
    parser.add_argument('--filters-file', '-F',
                        dest='filters_file',
                        help='file with filters')
    parser.add_argument('--mapping', '-m',
                        dest='mapping_path',
                        required=False,
                        default="mapping.json",
                        help='file path to mapping.json file')
    parser.add_argument('--user', '-U',
                        dest='user',
                        required=True,
                        help='user to access to Wordpress')
    parser.add_argument('--app-auth', '-A',
                        dest='app_auth',
                        required=True,
                        help='app auth code (from "Application '
                             'Passwords" plugin)')
    args = parser.parse_args()

    config = AppConfig(**args.__dict__)
    process_feed(config)


if __name__ == '__main__':
    main()


