Wammu installatie
=================

Pakketten voor Linux
====================

Veel distibuties hebben kant en klare Wammu-software. Als je die kunt
gebruiken is dat zeker de eenvoudigste methode. Er zijn ook binaire
pakketten van de laatse officiële versie beschikbaar op de Wammu-website
<http://wammu.eu/download/wammu/>.


Bouwen vanaf de broncode
========================

Gebruikt de standaard Python distutils, dus:

    python setup.py build
    sudo python setup.py install

Je hebt python-gammu en wxPython [1] (Unicode versie) nodig om dit programma
te installeren of te gebruiken. Als je ondersteuning wilt voor het scannen
van Bluetooth-apparaten heb je ook PyBluez [2] nodig. Voor het afhandelen
van inkomende gebeurtenissen is dbus-python [3] nodig.

Voor Windows moet je ook Pywin32 [4] installeren.

Als je om een of andere reden geen afhankelijkheid wilt testen tijdens het
bouwen kun je de --skip-deps optie gebruiken.

[1]: http://wxpython.org/

[2]: http://code.google.com/p/pybluez/

[3]: http://www.freedesktop.org/wiki/Software/DBusBindings

[4]: https://sourceforge.net/projects/pywin32/


Kruiscompilatie voor Windows op Linux
=====================================

Je hebt Wine met alle afhankelijke bibloitheken nodig (zie hierboven waar je
die kunt vinden).

Het is makkelijk om de wammu installer voor een werkende Python omgeving te
bouwen:

    wine c:\\python25\\python setup.py build --skip-deps bdist_wininst

Maar op deze manier moet de gebruiker alle Python bibliotheken zelf ook
installeren. Dat is niet erg gebruikersvriendelijk. Dit kan verholpen worden
met behulp van py2exe[5]:

    wine c:\\python25\\python setup.py build --skip-deps py2exe

Maar je moet hiervoor een aantal dingen aanpassen om py2exe goed te laten
werken in Wine. Je moet het programma aanpassen met behulp van PE Tools
(zoals beschreven in een Wine [w1] foutmelding. Bovendien moet je een aantal
extra bibliotheken die in de dist map ontbreken kopiëren (python25.dll  en
alles van wxPython). Zie het script admin/make-release dat dit automatisch
doet.

Je kunt dan InnoSetup[6] gebruiken om een Wammu installatieprogramma te
bouwen:

    wine c:\\Program\ Files\\Inno\ Setup\ 5/\\ISCC.exe wammu.iss

[5]: http://www.py2exe.org/

[6]: http://www.jrsoftware.org/isinfo.php

[w1]: http://bugs.winehq.org/show_bug.cgi?id=3591
