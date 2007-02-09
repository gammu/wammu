#!/bin/sh
LOCS=`ls locale/*.po | while read name; do basename $name ; done | sed 's/\.po$//'`
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
    msgmerge -s -U locale/$loc.po locale/wammu.pot
done
