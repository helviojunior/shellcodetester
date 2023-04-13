#!/bin/bash

C_BINUTILS_VERSION=2.39
C_GCC_VERSION=12.2.0
C_MINGW_VERSION=10.0.0

url=$(curl -s https://api.github.com/repos/helviojunior/shellcodetester/releases | jq -r '[ .[] | {id: .id, tag_name: .tag_name, assets: [ .assets[] | select(.name|match("mingw-latest.zip$")) | {name: .name, browser_download_url: .browser_download_url} ]} | select(.assets != []) ] | sort_by(.id) | reverse | .[].assets[].browser_download_url')

if [ "W$url" = "W" ]; then
    echo "::set-output name=DOWNLOAD_URL::"
    exit 0
fi

wget -O /tmp/mingw-latest.zip "$url"
unzip -o /tmp/mingw-latest.zip -d /tmp/
VERSION_FILE=$(find /tmp/ -name "VERSION.txt" -type f)

if [ "W$VERSION_FILE" = "W" ] || [ ! -f "$VERSION_FILE" ]; then
    echo "::set-output name=DOWNLOAD_URL::"
    exit 0
fi

BINUTILS_VERSION=$(cat "$VERSION_FILE" | grep -oE 'BINUTILS_VERSION=([0-9.]{1,50})' | cut -d'=' -f2)
GCC_VERSION=$(cat "$VERSION_FILE" | grep -oE 'GCC_VERSION=([0-9.]{1,50})' | cut -d'=' -f2)
MINGW_VERSION=$(cat "$VERSION_FILE" | grep -oE 'MINGW_VERSION=([0-9.]{1,50})' | cut -d'=' -f2)

if [ "W$BINUTILS_VERSION" != "W$C_BINUTILS_VERSION" ] || [ "W$GCC_VERSION" != "W$C_GCC_VERSION" ]|| [ "W$MINGW_VERSION" != "W$C_MINGW_VERSION" ]; then
    echo "::set-output name=DOWNLOAD_URL::"
    exit 0
fi

echo "::set-output name=DOWNLOAD_URL::${url}"