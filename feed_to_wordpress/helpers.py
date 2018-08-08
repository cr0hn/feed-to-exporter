from lxml.html.clean import Cleaner

from typing import Iterable


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
                  finding_sources: Iterable[Iterable or str]) -> bool:
    """

    Try to find keywords in a list of sources.

    Return True if find something. False otherwise

    :param keywords:
    :type keywords:

    :param finding_sources:
    :type finding_sources:
    """
    for keyword in keywords:
        for source in finding_sources:

            if type(source) in (list, set, tuple):
                if any(keyword in x for x in source):
                    return True
            else:
                if keyword in source:
                    return True

    return False
