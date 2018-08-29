import datetime
import pymongo

from typing import List
from pymongo import MongoClient

from feed_to_exporter.model import AbstractAppConfig, AbstractFeedInfo
from feed_to_exporter.exceptions import FeedToWordpressException


class FeedInfoWordpress(AbstractFeedInfo):

    def __init__(self,
                 app_config: AbstractAppConfig,
                 raw_feed_info: dict,
                 date: str = None,
                 **kwargs):
        super(FeedInfoWordpress, self).__init__(
            app_config,
            raw_feed_info=raw_feed_info,
            date=date,
            **kwargs
        )

    @property
    def tags(self) -> List:
        return self._tags

    @property
    def categories(self) -> List:
        return self._categories

    @property
    def to_json(self):
        r = self.raw_feed_info

        if "_id" not in r:
            r["_id"] = f"{self.date}#{self.raw_feed_info['link']}"

        r['date'] = self.date

        return r


class AppConfigMongo(AbstractAppConfig):

    def __init__(self,
                 user: str,
                 password: str,
                 mongo_urn: str,
                 collection: str,
                 database: str,
                 filter_file: str = "filters.py",
                 mapping_path: str = "mapping.json",
                 feed_source: str = None):

        super(AppConfigMongo, self).__init__(
            filter_file=filter_file,
            mapping_path=mapping_path,
            feed_source=feed_source
        )
        self.user = user
        self.database = database
        self.password = password
        self.mongo_urn = mongo_urn
        self.collection = collection

        if not self.mongo_urn.startswith("mongodb://"):
            raise FeedToWordpressException(
                "Invalid MongoDB URL format. URL must start with 'mongodb://'"
            )

        # ---------------------------------------------------------------------
        # Opening connector...
        # ---------------------------------------------------------------------
        self.client = MongoClient(self.mongo_urn)
        self.client_db_instance = getattr(self.client, self.database)
        self.client_collection = getattr(self.client_db_instance,
                                         self.collection)

    @property
    def mode(self) -> str:
        return "mongo"

    def push(self, feed_info) -> None:
        f = FeedInfoWordpress(self, **feed_info)
        try:
            self.client_collection.insert_one(f.to_json)
        except pymongo.errors.DuplicateKeyError:
            print("    - Repeated entry. Skipping")

