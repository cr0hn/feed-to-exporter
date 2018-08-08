FROM python:3.6-slim

RUN apt update \
    && apt install -y gosu \
    && pip install -U pip \
    && rm -rf /var/cache/apt \
    && adduser --uid 1024 --shell /dev/null --no-create-home produser

COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh
COPY ./dist/feed-to-wordpress-1.0.0.tar.gz /temp/
#RUN pip install -U feed-to-wordpress \
RUN pip install -U /temp/feed-to-wordpress-1.0.0.tar.gz \
    && chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
