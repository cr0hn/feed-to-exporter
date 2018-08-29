import os
import json
import inspect
import unidecode

from typing import Iterable
from lxml.html.clean import Cleaner


def clean_html(dirty_html):
    cleaner = Cleaner(page_structure=True,
                      meta=False,
                      embedded=True,
                      links=True,
                      style=False,
                      processing_instructions=False,
                      inline_style=False,
                      scripts=False,
                      javascript=False,
                      comments=False,
                      frames=True,
                      forms=False,
                      annoying_tags=False,
                      remove_unknown_tags=True,
                      safe_attrs_only=True,
                      safe_attrs=frozenset(
                          ['src', 'href', 'title', 'name']),
                      remove_tags=('span', 'font', 'div')
                      )

    return cleaner.clean_html(dirty_html)


def find_matching(keywords: Iterable,
                  finding_sources: Iterable[Iterable or str],
                  case_sensitive: bool = False) -> bool:
    """

    Try to find keywords in a list of sources.

    Return True if find something. False otherwise
    """
    for keyword in keywords:
        for source in finding_sources:

            if type(source) in (list, set, tuple):
                for x in source:
                    if not case_sensitive:
                        x_clean = x.lower()
                    else:
                        x_clean = x

                    x_clean = unidecode.unidecode(x_clean)

                    if keyword in x_clean:
                        return True
            else:
                if not case_sensitive:
                    source_clean = source.lower()
                else:
                    source_clean = source

                source_clean = unidecode.unidecode(source_clean)

                if keyword in source_clean:
                    return True

    return False


class MatchKeywords:

    def __init__(self, keywords_json_path: str = None):
        self._keywords_mapping: list = []
        self._keywords_json_path = keywords_json_path
        self._local_path = None
        self._load_keywords()

        self.matches_found = False

    def _load_keywords(self):
        self._local_path = os.path.abspath(self._keywords_json_path)
        loaded_data = json.load(open(self._local_path, "rb"))

        for entry in loaded_data:
            self._keywords_mapping.append([
                entry["keywords"],
                entry["tagName"],
                entry["tagDescription"]
            ])

    def match_entries(self, sources: Iterable) -> Iterable:
        # Reset
        self.matches_found = False

        for keywords, tag_name, tag_description in self._keywords_mapping:

            if find_matching(keywords, sources):
                self.matches_found = True

                yield (tag_name, tag_description)

    @staticmethod
    def resolve_keywords_file(caller_file: str = None,
                              keywords_file_name: str=None) -> str:
        """
        If caller_file and not keywords_file_name ->
            keyword file = dir(caller_file) + 'keywords.json"

        If caller_file and keywords_file_name ->
            keyword file = dir(caller_file) + keywords_file_name

        If not caller_file and keywords_file_name ->
            keyword file = keywords_file_name
        """
        if caller_file and not keywords_file_name:
            result_path = os.path.join(os.path.dirname(caller_file),
                                       "keywords.json")
        elif caller_file and keywords_file_name:
            result_path = os.path.join(os.path.dirname(caller_file),
                                       keywords_file_name)
        else:
            result_path = keywords_file_name

        return os.path.abspath(result_path)

