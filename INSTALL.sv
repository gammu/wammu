Wammu-installation
==================

Paket för Linux
===============

Många distributioner har förbyggda Wammu-binärer, om du kan använda dem är
det definitivt det lättaste. Det finns också binärpaket för de senaste
versionerna byggda för många distributioner via Wammu:s webbplats
<https://wammu.eu/download/wammu/>.


Att bygga från källkod
======================

Standard distutils används, så:

    python setup.py build
    sudo python setup.py install

Du behöevr python-gammu och wxPython [1] (Unicode-aktiverat bygge)
installerat för att köra och installera detta program. Om du vill ha stöd
för genomsökning efter Blutooth-enheter behöver du PyBluez [2]. För
inkommande händelseaviseringar behöver du dbus-python [3].

För Windows måste du också installera Pywin32 [4].

Om du av någon anledning vill följa beroendekontroll vid byggtid kan du
använda --skip-deps flaggan.

[1]: http://wxpython.org/

[2]: http://code.google.com/p/pybluez/

[3]: http://www.freedesktop.org/wiki/Software/DBusBindings

[4]: https://sourceforge.net/projects/pywin32/


Korskompilering för Windows på Linux
====================================

Du behöver Wine med alla beroende installerade (se avsnittet ovan för
information om var de finns).

Att bygg installeraren för wammu för Python är lätt:

    wine c:\\python25\\python setup.py build --skip-deps bdist_wininst

Men på detta sätt behöver användaren också installera alla beroenden, vilket
inte är betryggande. Detta bör lösas med att använda py2exe [5]:

    wine c:\\python25\\python setup.py build --skip-deps py2exe

Men förutom detta behöver du även justera en del saker manuellt. För att få
py2exe att fungera i Window behöver du fixa dessa binär med PE Tools
(beskrivet i felrapporten i Wine [w1]) och kopiera några extra bibliotek som
saknas till dist-katalogen (python25.dll och bibliotek från wxPython). Se
skript admin/make-relase vilket automatiserar detta kopierande.

Sedan kan du använda InnoSetup[6] för att bygga installeraren för Wammu:

    wine c:\\Program\ Files\\Inno\ Setup\ 5/\\ISCC.exe wammu.iss

[5]: http://www.py2exe.org/

[6]: http://www.jrsoftware.org/isinfo.php

[w1]: http://bugs.winehq.org/show_bug.cgi?id=3591
