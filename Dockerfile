FROM python:3.6-slim

RUN pip install -U pip \
    && rm -rf /var/cache/apt

COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh
RUN pip install -U feed-to-wordpress \
RUN pip install -U /temp/feed-to-wordpress-1.0.0.tar.gz \
    && chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
