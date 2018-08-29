import base64

from typing import List
from urllib.parse import urlparse

from feed_to_exporter.exceptions import FeedToWordpressException
from feed_to_exporter.model import AbstractAppConfig, AbstractFeedInfo

from .wordpress_queries import get_or_create_tag_or_category, publish_post


class FeedInfoWordpress(AbstractFeedInfo):

    def __init__(self,
                 app_config: AbstractAppConfig,
                 raw_feed_info: dict,
                 **kwargs):
        super(FeedInfoWordpress, self).__init__(
            app_config,
            raw_feed_info=raw_feed_info,
            **kwargs
        )

        # Fixed values
        self.ping_status: str = kwargs.get("ping_status", "closed")
        self.feed_source: str = kwargs.get("feed_source", "")
        self.post_status: str = kwargs.get("post_status", "draft")
        self.comment_status: str = kwargs.get("comment_status", "closed")

        self.body: str = kwargs.get("body", "")
        self.link: str = kwargs.get("link", "")
        self.slug = ""
        self.content = ""
        self._tag_ids = set()
        self._categories_ids = set()
        self._generated_fields_by_filters = set()

        for cat in kwargs.get("categories", []):
            cat_name = cat["category"]
            cat_parent = cat["parent"]

            self.add_category(name=cat_name, parent_category_name=cat_parent)

        for tag in kwargs.get("tags", []):
            self.add_tag(name=tag)

    @property
    def to_wordpress_json(self) -> dict:

        return {
            'title': self.title,
            'content': self.content,
            'slug': self.slug,
            'date': self.date,
            'format': 'standard',
            'status': self.post_status,
            'comment_status': self.comment_status,
            'ping_status': self.ping_status,
            'tags': self.tags,
            'categories': self.categories
        }

    def active_categories_and_tags_in_wordpress(self):
        """This method create the categories and tags en the a
        remote Wordpress"""

        # ---------------------------------------------------------------------
        # Categories
        # ---------------------------------------------------------------------
        for category_name, prop in self._categories.items():
            category_description = prop.get("name")
            category_parent = prop.get("parent")

            # -----------------------------------------------------------------
            # Getting parent category, if necessary
            # -----------------------------------------------------------------
            parent = None
            if category_parent:
                parent = get_or_create_tag_or_category(
                    "category",
                    category_name,
                    self.app_config,
                    category_description)

            category_id = get_or_create_tag_or_category(
                "category",
                category_name,
                self.app_config,
                category_description,
                parent
            )

            # Update with ID
            self._categories[category_name]["id"] = category_id
            self._categories_ids.add(category_id)

        # ---------------------------------------------------------------------
        # Tags
        # ---------------------------------------------------------------------
        for tag_name, prop in self._tags.items():
            description = prop.get("description")

            tag_id = get_or_create_tag_or_category(
                "tag",
                tag_name,
                self.app_config,
                description
            )

            self._tags[tag_name]["id"] = tag_id
            self._tag_ids.add(tag_id)

    @property
    def tags(self) -> List[str]:
        return list(self._tag_ids)

    @property
    def categories(self) -> List[str]:
        return list(self._categories_ids)


class AppConfigWordpress(AbstractAppConfig):

    REQUIRED_FIELDS_IN_MAPPING_FIELD = (
        'body',
    )

    def __init__(self,
                 user: str,
                 app_auth: str,
                 wordpress_url: str,
                 develop_mode: bool,
                 filter_file: str = "filters.py",
                 mapping_path: str = "mapping.json",
                 feed_source: str = None):

        super(AppConfigWordpress, self).__init__(
            feed_source=feed_source,
            filter_file=filter_file,
            mapping_path=mapping_path

        )

        self.user = user
        self.app_auth = app_auth
        self.develop_mode = develop_mode

        self._target_url = wordpress_url
        self._target_url_fixed = None
        self._token = None

    def _load_json(self, mapping_path: str) -> dict:

        loaded_mapping = super()._load_json(mapping_path)

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

        return loaded_mapping

    @property
    def token(self) -> dict:
        """Returns a HTTP header as dict with auth token inside"""
        if not self._token:
            token = base64.standard_b64encode(
                f"{self.user}:{self.app_auth}".encode())

            headers = {'Authorization': f'Basic {token.decode()}'}

            self._token = headers

        return self._token

    @property
    def wordpress_url(self):
        if not self._target_url_fixed:
            scheme, host, *_ = urlparse(self._target_url)
            self._target_url_fixed = f"{scheme}://{host}/wp-json/wp/v2"

        return self._target_url_fixed

    @property
    def mode(self) -> str:
        return "wordpress"

    def push(self, feed_data: dict) -> None:
        f = FeedInfoWordpress(self, **feed_data)

        if self.develop_mode is False:

            # Setup remote tags/categories
            f.active_categories_and_tags_in_wordpress()

            # Apply filters
            f.apply_filters()

            # Publish post
            publish_post(f.to_wordpress_json, self)
