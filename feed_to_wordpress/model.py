import json
import base64
import os.path

from types import SimpleNamespace
from urllib.parse import urlparse

from .exceptions import FeedToWordpressException


class AppConfig:

    REQUIRED_FIELDS_IN_MAPPING_FIELD = (
        'body',
    )

    def __init__(self,
                 user: str,
                 app_auth: str,
                 filters_file: str,
                 wordpress_url: str,
                 discover_mode: bool,
                 develop_mode: bool = False,
                 mapping_path: str = "mapping.json",
                 feed: str = None):
        self.feed = feed
        self.user = user
        self.app_auth = app_auth
        self.develop_mode = develop_mode
        self.discover_mode = discover_mode

        self.filters_file = None
        if filters_file:
            self.filters_file = os.path.abspath(filters_file)

        self.mapping_path = os.path.abspath(mapping_path)
        self.wordpress_host = wordpress_url

        #
        # Load filter file
        #
        if self.filters_file:
            g = {}
            exec(open(self.filters_file, "rb").read(), g)
            self.filters = g.get("INDIVIDUAL_VALIDATORS", {})
            self.validation_rule = g.get("GLOBAL_VALIDATOR", lambda x: {})
        else:
            self.filters = {}
            self.validation_rule = lambda x: {}

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

        #
        # Fill feed, if we're in discover mode
        #
        if self.discover_mode and self.feed:
            try:
                self.feed = self.mapping_json['feed']
            except KeyError:
                raise FeedToWordpressException(
                    "Invalid mapping.json format. When you're using discover"
                    "mode you must specify the field 'feed' with the remote"
                    "RSS location"
                )

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
    def mapping_json(self) -> SimpleNamespace:
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
                # -------------------------------------------------------------
                # Check for default values
                # -------------------------------------------------------------
                if "link" not in loaded_mapping['mapping']:
                    loaded_mapping['mapping'].update({"link": "link"})
                if "title" not in loaded_mapping['mapping']:
                    loaded_mapping['mapping'].update({"title": "title"})

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


__all__ = ("AppConfig", )

