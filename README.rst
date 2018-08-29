Feed to Wordpress Post
======================

This project allow to get RSS Feed and create new Wordpress post from them.

Pre-requisites
--------------

Wordpress Mode
++++++++++++++

- You must install the Wordpress plugin: `Application Passwords <https://es.wordpress.org/plugins/application-passwords/>`_
- You must create a new Application Password
- **Python 3.6 or above**


mapping.json format
-------------------

Wordpress Mode
++++++++++++++

The mapping file has this format:

.. code-block:: json

    {
      "feed": "http://www.xxxx.es/blogs/xxxx/feed/",
      "exportMethod": "wordpress",
      "mapping": {
        "body": "summary"
      },
      "fixed": {
        "tags": ["one", "two", "general"],
        "categories": [
          {
            "category": "subcategory",
            "parent": "top-category"
          }
        ],
        "post_status": "publish"
      }
    }

Mongo Mode
++++++++++


.. code-block:: json

    {
      "feed": "http://www.xxxx.es/blogs/xxxx/feed/",
      "exportMethod": "mongo",
      "fixed": {
        "categories": [
          {
            "category": "subcategory",
            "parent": "top-category"
          }
        ]
      }
    }

Mapping key
+++++++++++

``mapping`` indicates how ``f2e`` must match the input feed values to the wordpress result.

- Left values of mapping will be the variables names of exported objects.
- Right values are the key names in feed where ``f2e`` must map to the output.

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

Fixed keys
++++++++++

Some times it should be interesting to add some static values to the result dict object. You can use fixed keys for this purpose.

**Wordpress mode**

In Wordpress there're two special keys: ``tags`` and ``categories``.

You can specify *tags* and *categories*. ``f2e`` will try to resolve the tag/category or create if it doesn't exits in the Wordpress site.

Filters
-------

There's situations where you may want to apply some advanced filters. To do that we must add some Python code.

You can use any name for the filter file, but for convention we'll use ``filters.py``. There a basic example:

Basics
++++++

.. code-block:: python

    from feed_to_exporter.filters import FeedInfo
    from feed_to_exporter.exceptions import FeedToWordpressNotValidInfoFound



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

Result data structure
+++++++++++++++++++++

``f2e`` export collected data from feed to a dictionary. Depending of the export method you want, it need some different keys:

**Wordpress**

FeedInfoWordpress has these properties:

- title: str
- slug: str
- link: str
- feed_source: str
- body: str -> raw information from Feed mapping
- content: str -> content that will send to the Wordpress Post. By default is a composition of: body + html link + feed_source. You can see at internal filters (``feed_to_exporter.filters.py``)
- raw_feed_info: dict -> raw content of feed
- ping_status: str (default: closed)
- feed_source: str (default: closed)
- post_status: str (default: draft)
- comment_status: str (default: closed)
- date: str (default: now time, with format: %Y-%m-%dT%H:%M:%S)

For fields ``ping_status``, ``feed_source``, ``post_status`` and ``comment_status`` you can check valid values at Wordpress REST API doc: https://developer.wordpress.org/rest-api/

**Mongo**

Mongo doesn't need any special value for the result dictionary. The whole dict will be stored into Mongo "as is".


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
    ├── __init__.py
    ├── site1.com
    │   ├── __ini__.py
    │   ├── filters.py
    │   └── mapping.json
    └── other-site.com
    │   ├── __ini__.py
        ├── f2eSkip
        ├── filters.py
        └── mapping.json

**IMPORTANT**: all of folders need the file ``__init__.py`` con convert it into a Python package.

**Ignoring directory**

If you want that a directory will be ignored, only create a file called ``f2eSkip`` into the directory and the engine will ignore it.


Running Examples
----------------

Without Docker
++++++++++++++

Install:

.. code-block:: bash

    > pip install -U feed-to-exporter

**Wordpress mode**


Basic Usage:


.. code-block:: bash

    > f2e wordpress -W https://mywordpress.com -U user -A "XXXX XXXX XXXX XXXX XXXX XXXX" examples/

Where ``-A`` indicates the Application Password

For more help type ``-h``:

.. code-block:: bash

    > f2e wordpress -h

    usage: f2e wordpress [-h] --wordpress-url WORDPRESS_URL --user USER --app-auth
                     APP_AUTH [--devel]
                     [feed_source [feed_source ...]]

    positional arguments:
      feed_source           target url or path

    optional arguments:
      -h, --help            show this help message and exit
      --wordpress-url WORDPRESS_URL, -W WORDPRESS_URL
                            wordpress url
      --user USER, -U USER  user to access to Wordpress
      --app-auth APP_AUTH, -A APP_AUTH
                            app auth code (from "Application Passwords" plugin)
      --devel               running in develop mode doesn't publish Wordpress Post


**MongoDB mode**

With default parameters (mongo in localhost without authentication, database=f2e, collection=f2e)

.. code-block:: bash

    > f2e mongo examples/

Setting some parameters:


.. code-block:: bash

    > f2e mongo -U mongoAdmin -M mongodb://10.0.0.1:27017 examples/

For more help type ``-h``:

.. code-block:: bash

    > f2e mongo -h

    usage: f2e mongo [-h] [--user USER] [--password PASSWORD]
                 [--collection COLLECTION] [--database DATABASE]
                 [--mongo-url MONGO_URN]
                 [feed_source [feed_source ...]]

    positional arguments:
      feed_source           target url or path

    optional arguments:
      -h, --help            show this help message and exit
      --user USER, -U USER  mongodb user
      --password PASSWORD, -P PASSWORD
                            mongodb password
      --collection COLLECTION, -C COLLECTION
                            mongo collection
      --database DATABASE, -D DATABASE
                            mongo database
      --mongo-url MONGO_URN, -M MONGO_URN
                            mongo URL. (Default: mongodb://127.0.0.1:27017/f2e)


Using Docker
++++++++++++

Docker only run in discovery mode and can schedule a new run each some seconds.

You can mount a dir with the filters/mapping, but it's highly recommended to put it into a git repository.

**Environment vars**

- f2e_CMD_PARAMETERS: f2e running options
- f2e_CHECK_TIME: time to launch in seconds
- f2e_FILTERS_GIT: git where to download filters and mapping

**Running examples**

Run feed each 3600 seconds:

.. code-block:: bash

    > docker run --rm \
        -e f2e_FILTERS_GIT=https://XXXXXXXXXXXXXX@github.com/cr0hn/myfeeds-repo.git \
        -e f2e_CMD_PARAMETERS='wordpress -W https://mywordpress.com -U admin -A "XXXX XXXX XXXX XXXX XXXX XXXX"' \
        -e f2e_CHECK_TIME=3600 f2e


Contributing
============

Any collaboration is welcome!

There're many tasks to do.You can check the `Issues <https://github.com/cr0hn/feed-to-exporter/issues/>`_ and send us a Pull Request.

License
=======

This project is distributed under `BSD 3 license <https://github.com/cr0hn/feed-to-exporter/blob/master/LICENSE>`_
