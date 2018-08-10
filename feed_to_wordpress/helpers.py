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
