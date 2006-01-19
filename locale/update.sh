#!/bin/sh
xgettext -d wammu -F --msgid-bugs-address=michal@cihar.com -o locale/wammu.pot `find Wammu/ -name '*.py'`
for loc in cs de fr hu it ; do
    msgmerge -F -U locale/$loc.po locale/wammu.pot
done
