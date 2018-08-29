FROM python:3.6-slim

RUN apt-get update \
    && apt-get install -y git-core \
    && pip install -U pip \
    && rm -rf /var/cache/apt

COPY ./entrypoint.sh /usr/local/bin/entrypoint.sh
RUN pip install -U feed-to-exporter \
    && chmod +x /usr/local/bin/entrypoint.sh

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
