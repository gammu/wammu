#!/bin/sh
xgettext -o locale/wammu.pot `find Wammu/ -name '*.py'`
msgmerge -U locale/cs.po locale/wammu.pot
