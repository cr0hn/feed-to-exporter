Feed to Wordpress Post
======================

This project allow to get RSS Feed and create new Wordpress post from them.

Pre-requisites
--------------

- You must install the Wordpress plugin: `Application Passwords <https://es.wordpress.org/plugins/application-passwords/>`_
- You must create a new Application Password

mapping.json format
-------------------

The mapping file has this format:

.. code-block:: json

    {
      "mapping": {
        "title": "title",
        "content": "summary",
        "link": "link"
      },
      "fixed": {
        "tags": ["one", "two", "general"],
        "categories": ["mycategory"]
      }
    }

Mapping key
+++++++++++

`mapping` indicates how `f2w` must match the input feed values to the wordpress result.

- Left values of mapping (title, content, link) are always the same.
- Right values are the key names in feed where `f2w` must map to the output.

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

Then, if we want to recover the title, description and published date, we must write this `mapping.json`:

.. code-block:: json

    {
      "mapping": {
        "title": "title",
        "content": "description",
        "link": "link"
      }
    }

Fixed key
+++++++++

Some times it should be interesting to add some static values to the post results, like tags or categories.

You can specify any values as keys but **only tags and categories** have sense to be send to Wordpress API.

You can specify *tags* and *categories*. `f2w` will try to resolve the tag/category or create if it doesn't exits.

Filters
-------

There's situations where you can want to apply some advanced filters. You can do data adding some Python code.

You can use any name for the filter file, but for convention we'll use `filters.py`. There a basic example:

Basics
++++++

.. code-block:: python

    def content_filter(text) -> dict:
        results = {"tags": []}
        if "goal" in text:
            results["tags"] = "goal"

        return results


    def validation_filter(**kwargs) -> bool:
        if

    # THIS VAR NAME IS MANDATORY!
    FILTER_RULES = {
        'content': content_filter
    }

    # THIS VAR NAME IS OPTIONAL!
    VALIDATION_FILTER = validation_filter

As you can see you must define the var name `FILTER_RULES` that indicates the field where it will apply the filter.

Filters **always** must return a dictionary and it can overwrite the original content of a field.

The parameters passed in each filter function is the value of the field.

Input fields
++++++++++++

The object that `f2w` handles is like that:

.. code-block:: json

    {
        "title": "My Custom Title for the Post",
        "slug": "my-custom-title-for-post",
        "content": "long description for the post",
        "date": "2018-07-11T21:11:20",
        "format" = "standard",
        "status" = "draft",
        "comment_status" = "closed",
        "ping_status" = "closed",
        "tags": ["1", "2"],
        "categories": ["4", "5"]
    }

You can write a filter for each key.

Validation rule
+++++++++++++++

Some times you could want to use a global validation rule. This validation could implies more than one field. If this is the case then you must use the a new function and map to `VALIDATION_FILTER` variable.

This function must returns a **boolean** value: True, validations pass. False, otherwise.

Examples
--------

Basic

.. code-block:: bash

    > f2w -W https://mysite.com -U user -m examples/mapping.json -A "XXXX XXXX XXXX XXXX XXXX XXXX" "http://www.mjusticia.gob.es/cs/Satellite?c=Page&cid=1215197792452&lang=es_es&pagename=eSEDE%2FPage%2FSE_DetalleRSS"

Where `-A` indicates the Application Password

Using a filter file:

.. code-block:: bash

    > f2w -W https://mysite.com -F filters.py -U user -m examples/mapping.json -A "XXXX XXXX XXXX XXXX XXXX XXXX" "http://www.mjusticia.gob.es/cs/Satellite?c=Page&cid=1215197792452&lang=es_es&pagename=eSEDE%2FPage%2FSE_DetalleRSS"



Contributing
============

Any collaboration is welcome!

There're many tasks to do.You can check the `Issues <https://github.com/cr0hn/feed-to-wordpress/issues/>`_ and send us a Pull Request.

License
=======

This project is distributed under `BSD 3 license <https://github.com/cr0hn/feed-to-wordpress/blob/master/LICENSE>`_
