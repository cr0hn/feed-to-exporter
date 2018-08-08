#!/usr/bin/env bash

#exec gosu produser f2w -W ${F2W_WORDPRESS_SITE} \
f2w -W ${F2W_WORDPRESS_SITE} \
    -F ${F2W_FILTERS} \
    -U ${F2W_USER} \
    -m ${F2W_MAPPING} \
    -A "${F2W_APPLICATION_PASSWORD}" \
    "${F2W_FEED_URL}"
