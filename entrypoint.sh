#!/usr/bin/env bash

if [ -n "${F2W_DISCOVER_MODE}" ]; then
    # Run discover mode
    f2w -W ${F2W_WORDPRESS_SITE} \
        -U ${F2W_USER} \
        -D \
        -A "${F2W_APPLICATION_PASSWORD}" \
        "${F2W_FEED}"
else
    # Run normal mode
    f2w -W ${F2W_WORDPRESS_SITE} \
        -F ${F2W_FILTERS} \
        -U ${F2W_USER} \
        -m ${F2W_MAPPING} \
        -A "${F2W_APPLICATION_PASSWORD}" \
        "${F2W_FEED}"

fi
