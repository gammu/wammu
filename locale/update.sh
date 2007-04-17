#!/bin/sh
LOCS=`ls locale/*/wammu.po | sed 's@.*/\(.*\)/[^/]*@\1@'`
xgettext \
    -d wammu \
    --msgid-bugs-address=michal@cihar.com \
    -o locale/wammu.pot \
    --language=Python \
    --add-comments=l10n \
    --add-location \
    --copyright-holder="Michal Čihař" \
    `find Wammu/ -name '*.py'` wammu-configure.py wammu.py

ver=`python -c 'import Wammu; print Wammu.__version__'`
sed -i '
    s/SOME DESCRIPTIVE TITLE/Wammu translation/;
    s/PACKAGE/Wammu/;
    s/(C) YEAR/(C) 2003 - 2007/;
    s/VERSION/'$ver'/;
    ' locale/wammu.pot

for loc in $LOCS ; do
    msgmerge -U locale/$loc/wammu.po locale/wammu.pot
done
