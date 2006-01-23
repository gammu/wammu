#!/bin/sh
. locale/list.sh
xgettext -s -d wammu --msgid-bugs-address=michal@cihar.com -o locale/wammu.pot `find Wammu/ -name '*.py'`
for loc in $LOCS ; do
    msgmerge -s -U locale/$loc.po locale/wammu.pot
done
