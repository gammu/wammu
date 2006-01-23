#!/bin/sh
. locale/list.sh
for loc in $LOCS ; do
    mkdir -p locale/$loc/LC_MESSAGES
    echo -n "$loc: "
    msgfmt --statistics -o locale/$loc/LC_MESSAGES/wammu.mo locale/$loc.po
done
