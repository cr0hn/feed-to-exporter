Feed to Wordpress Post
======================

This project allow to get RSS Feed and create new Wordpress post from them.

Pre-requisites
--------------

- You must install the Wordpress plugin: `Application Passwords <https://es.wordpress.org/plugins/application-passwords/>`_
- You must create a new Application Password
- **Python 3.6 or above**

mapping.json format
-------------------

The mapping file has this format:

.. code-block:: json

    {
      "mapping": {
        "title": "title",
        "body": "summary",
        "link": "link"
      },
      "fixed": {
        "tags": ["one", "two", "general"],
        "categories": ["mycategory"]
      }
    }

By default ``title`` and ``link`` keys are mapped like above example. Then, you can write:

.. code-block:: json

    {
      "mapping": {
        "body": "summary"
      },
      "fixed": {
        "tags": ["one", "two", "general"],
        "categories": ["mycategory"]
      }
    }

``f2w`` can run in ``discover`` mode. So, you can specify the RSS Feed source in the mapping.json, like that:

.. code-block:: json

    {
      "feed": "https://myfeedsource.som",
      "mapping": {
        "body": "summary"
      },
      "fixed": {
        "tags": ["one", "two", "general"],
        "categories": ["mycategory"]
      }
    }



Mapping key
+++++++++++

``mapping`` indicates how ``f2w`` must match the input feed values to the wordpress result.

- Left values of mapping (title, body, link) are always the same.
- Right values are the key names in feed where ``f2w`` must map to the output.

For example:

Suppose this RSS:

.. code-block:: xml

    <?xml version="1.0" encoding="ISO-8859-1"?>
    <rss version="2.0">
        <channel>
            <title>Trabajo y empleo - BOE - Boletín Oficial del Estado</title>
            <link>http://www.boe.es/diario_boe/</link>
            <description>Legislación relativa a Trabajo y empleo ingresada en los últimos dos meses en la base de datos del Boletín Oficial del Estado</description>
            <language>es-es</language>
            <pubDate>Mon, 06 Aug 2018 00:00:00 +0200</pubDate>
            <lastBuildDate>Mon, 06 Aug 2018 14:55:03 +0200</lastBuildDate>
            <webMaster>webmaster@boe.es</webMaster>
            <item>
              <title>Pleno. Sentencia 78/2018, de 5 de julio de 2018. Recurso de inconstitucionalidad 3720-2017. Interpuesto por el Presidente del Gobierno en relación con los artículos 13 y 36 de la Ley 10/2016, de 27 de diciembre, del presupuesto de la Comunidad Autónoma de Andalucía para el año 2017. Competencias sobre ordenación general de la economía, hacienda general y función pública: nulidad parcial del precepto legal autonómico relativo a la oferta de empleo público de 2017 u otro instrumento similar de gestión de la provisión de necesidades de personal (STC 142/2017). Voto particular.</title>
              <link>http://www.boe.es/diario_boe/txt.php?id=BOE-A-2018-11276</link>
              <description>Tribunal Constitucional - Publicado el 06/08/2018 - Referencia: BOE-A-2018-11276</description>
              <guid isPermaLink="true">http://www.boe.es/boe/dias/2018/08/06/pdfs/BOE-A-2018-11276.pdf</guid>
              <pubDate>Mon, 06 Aug 2018 00:00:00 +0200</pubDate>
            </item>
        </channel>
    </rss>

Where each item has this format:

.. code-block:: xml

    <item>
      <title>Pleno. Sentencia 78/2018, de 5 de julio de 2018. Recurso de inconstitucionalidad 3720-2017. Interpuesto por el Presidente del Gobierno en relación con los artículos 13 y 36 de la Ley 10/2016, de 27 de diciembre, del presupuesto de la Comunidad Autónoma de Andalucía para el año 2017. Competencias sobre ordenación general de la economía, hacienda general y función pública: nulidad parcial del precepto legal autonómico relativo a la oferta de empleo público de 2017 u otro instrumento similar de gestión de la provisión de necesidades de personal (STC 142/2017). Voto particular.</title>
      <link>http://www.boe.es/diario_boe/txt.php?id=BOE-A-2018-11276</link>
      <description>Tribunal Constitucional - Publicado el 06/08/2018 - Referencia: BOE-A-2018-11276</description>
      <guid isPermaLink="true">http://www.boe.es/boe/dias/2018/08/06/pdfs/BOE-A-2018-11276.pdf</guid>
      <pubDate>Mon, 06 Aug 2018 00:00:00 +0200</pubDate>
    </item>

This implies that we'll have these keys:

- title
- link
- description
- pubDate
- guid

Then, if we want to recover the title, description and published date, we must write this ``mapping.json``:

.. code-block:: json

    {
      "mapping": {
        "body": "description"
      }
    }

Fixed key
+++++++++

Some times it should be interesting to add some static values to the post results, like tags or categories.

You can specify any values as keys but **only tags and categories** have sense to be send to Wordpress API.

You can specify *tags* and *categories*. ``f2w`` will try to resolve the tag/category or create if it doesn't exits.

Filters
-------

There's situations where you may want to apply some advanced filters. To do that we must add some Python code.

You can use any name for the filter file, but for convention we'll use ``filters.py``. There a basic example:

Basics
++++++

.. code-block:: python

    from feed_to_wordpress.filters import FeedInfo
    from feed_to_wordpress.exceptions import FeedToWordpressNotValidInfoFound



    def link_filter(field_value: str) -> dict:
        """
        this filter will download the link pointing by the field and replace
        the content of the web page.

        Also try to check if some keywords are available and generate some tags

        Content filter must return a dictionary type, otherwise, engine will
        release an exception
        """
        response = request.get(field_value)

        results = {
            'body': response.content
        }

        # Try to find tags
        if any(x in response.content for x in ('hacking', 'security',
            'pentesting')):
            results['tags'] = ['security']

        return results

    def body_filter(field_value: str) -> dict:
        """
        This filter remove the words 'SEO' from the body field and return
        the new 'body' value for the field. The engine will update that
        with this information.

        Content filter must return a dictionary type, otherwise, engine will
        release an exception
        """
        return {'body': field_value.replace('SEO', '')}


    def global_filter(feed_info: FeedInfo) -> \
            dict or FeedToWordpressNotValidInfoFound:
        """
        Global filter enables a validation with the context of all of fields
        values. This filter must return a dictionary or an exception.

        If one exception is returned, engine will interpret that the current
        feed must not be processed and continue to the next feed.

        Global filter will executed after the individual filters.
        """

        if not feed_info.title or not feed_info.body:
            raise FeedToWordpressNotValidInfoFound()

        if "security" in feed_info.title and "hacking" in feed_info.body:
            return {"category": ["hard-security"]}
        elif "ciso" in feed_info.body.lower():
            return {"category": ["ciso-news"]}
        else:
            return {}

    #
    # Order of filters are following the definition in the bellow dictionary
    #
    # The name of the variable must be the following for the individual filters
    INDIVIDUAL_VALIDATORS = {
        'link': link_filter,
        'body': body_filter
    }

    # The name of the variable must be the following for global validator
    GLOBAL_VALIDATOR = global_filter

As you can see you must define the var name ``INDIVIDUAL_VALIDATORS`` indicates the field where it will apply the filter.

Filters **always** must return a dictionary and it can overwrite the original content of a field.

Filters execution order are defined by the order indicated in the ``INDIVIDUAL_VALIDATORS`` var.

The parameters passed in each individual filter function is the value of the field.

Input fields
++++++++++++

FeedInfo has these properties:

- title: str
- app_config: str
- link: str
- feed_source: str
- body: str -> raw information from Feed mapping
- content: str -> content that will send to the Wordpress Post. By default is a composition of: body + html link + feed_source. You can see at internal filters (``feed_to_wordpress.filters.py``)
- raw_feed_info: dict -> raw content of feed
- pint_status: str (default: closed)
- feed_source: str (default: closed)
- post_status: str (default: draft)
- comment_status: str (default: closed)
- date: str (default: now time, with format: %Y-%m-%dT%H:%M:%S)

Validation rule
+++++++++++++++

Some times you could want to use a global validation rule. This validation could implies more than one field. If this is the case then you must use the a new function and map to ``GLOBAL_VALIDATOR`` variable.

This function must returns a **dict** value or a Exception.

Working modes
-------------

Simple
++++++

Simple mode is the usual mode. Explained above.

Discovery mode
++++++++++++++

Discover mode discover recursively the directories, form a base dir given. The engine will get each directory and manage it as and independent running.

For this mode works well each crawler must in an independent directory and have only 2 files: ``filters.py`` and ``mapping.json``.

To enable this mode you must use the ``-D`` option and each m¡``mapping.json`` must have an additional entry: ``feed``:

.. code-block:: json

    {
      "feed": "http://www.mysite.com/feed/",
      "mapping": {
        "body": "summary"
      },
      "fixed": {
        "categories": ["myCategory"]
      }
    }

**Example of directory structure**

.. code-block:: bash

    > tree examples/
    examples
    ├── site1.com
    │   ├── filters.py
    │   └── mapping.json
    └── other-site.com
        ├── f2wSkip
        ├── filters.py
        └── mapping.json

**Ignoring directory**

If you want that a directory will be ignored, only create a file called ``f2wSkip`` into the directory and the engine will ignore it.


Running Examples
----------------

Without Docker
++++++++++++++

Install:

.. code-block:: bash

    > pip install -U feed-to-wordpress

Basic Usage:


.. code-block:: bash

    > f2w -W https://mysite.com -U user -m examples/mapping.json -A "XXXX XXXX XXXX XXXX XXXX XXXX" "http://www.mjusticia.gob.es/cs/Satellite?c=Page&cid=1215197792452&lang=es_es&pagename=eSEDE%2FPage%2FSE_DetalleRSS"

Where ``-A`` indicates the Application Password

Using a filter file:

.. code-block:: bash

    > f2w -W https://mysite.com -F filters.py -U user -m examples/mapping.json -A "XXXX XXXX XXXX XXXX XXXX XXXX" "http://www.mjusticia.gob.es/cs/Satellite?c=Page&cid=1215197792452&lang=es_es&pagename=eSEDE%2FPage%2FSE_DetalleRSS"

Using Docker
++++++++++++

**Environment vars**

- F2W_WORDPRESS_SITE: Wordpress site where to publish the new post
- F2W_FILTERS: filters file, for example: filters.py
- F2W_USER: Wordpress user
- F2W_MAPPING: mapping.json location
- F2W_APPLICATION_PASSWORD: Application password
- F2W_FEED: Feed URL or path
- F2W_DISCOVER_MODE: Feed URL or path

Running normal mode:

.. code-block:: bash

    > ls examples/
    filters.py mapping.json

    > docker run --rm -v "$(pwd)/examples/":/tmp -e F2W_WORDPRESS_SITE=https://mysite.com \
        -e F2W_FILTERS=/tmp/filters.py \
        -e F2W_USER=user \
        -e F2W_MAPPING=/tmp/mapping.json \
        -e F2W_APPLICATION_PASSWORD="XXXX XXXX XXXX XXXX XXXX XXXX" \
        -e F2W_FEED="http://www.mjusticia.gob.es/cs/Satellite?c=Page&cid=1215197792452&lang=es_es&pagename=eSEDE%2FPage%2FSE_DetalleRSS" \
        cr0hn/feed-to-wordpress

Running discover mode:

.. code-block:: bash

    > ls examples/
    filters.py mapping.json

    > docker run --rm -v "$(pwd)/examples/":/tmp/myfeeds -e F2W_WORDPRESS_SITE=https://mysite.com \
        -e F2W_USER=user \
        -e F2W_DISCOVER_MODE=1 \
        -e F2W_APPLICATION_PASSWORD="XXXX XXXX XXXX XXXX XXXX XXXX" \
        -e F2W_FEED="/tmp/myfeeds" \
        cr0hn/feed-to-wordpress


Contributing
============

Any collaboration is welcome!

There're many tasks to do.You can check the `Issues <https://github.com/cr0hn/feed-to-wordpress/issues/>`_ and send us a Pull Request.

License
=======

This project is distributed under `BSD 3 license <https://github.com/cr0hn/feed-to-wordpress/blob/master/LICENSE>`_
