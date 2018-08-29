#!/usr/bin/env bash

if [ -z "${f2e_FILTERS_GIT}" ]; then
    echo "[!] Environment vars 'f2e_FILTERS_GIT' needed"
    exit 1
fi

if [ -z "${f2e_CMD_PARAMETERS}" ]; then
    echo "[!] Environment vars 'f2e_CMD_PARAMETERS' needed"
    exit 1
fi

if [ -z "${f2e_CHECK_TIME}" ]; then
    echo "[!] Environment vars 'f2e_CHECK_TIME' needed"
    exit 1
fi

#
# First clone of GIT
#
mkdir /tmp/f2e
cd /tmp/f2e

git clone ${f2e_FILTERS_GIT} /tmp/f2e/repo

while [ 1 ];
do
    echo f2e ${f2e_CMD_PARAMETERS} /tmp/f2e/repo/ | sh
    sleep ${f2e_CHECK_TIME}s

    # Update git
    cd /tmp/f2e/repo
    git pull
    cd /tmp/f2e
done