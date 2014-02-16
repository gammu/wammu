Instalace Wammu
===============

Balíčky pro Linux
=================

Mnoho distribucí obsahuje balíčku pro Wammu, takže pokud je můžete použít,
je to určitě nejsnadnější cesta. Aktuální verzi zabalenou pro mnoho
distribucí naleznete na stránkách Wammu
<http://cs.wammu.eu/download/wammu/>.


Kompilace ze zdrojových kódů
============================

Wammu používá standardní distutils, takže instalace proběhne:

    python setup.py build
    sudo python setup.py install

Pro instalaci a spuštění tohoto programu potřebujete mít nainstalované
python-gammu a wxPython [1] (build s Unicode). Pokud chcete podporu pro
vyhledávání zařízení na Bluetooth, potřebujete PyBluez [2]. Pro upozorňování
na příchozí události potřebujete dbus-python [3].

Na Windows take budete muset nainstalovat Pywin32 [4].

Pokud chcete z jakéhokoliv důvodu přeskočit kontrolování závislostí, můžete
použít parametr --skip-deps.

[1]: http://wxpython.org/

[2]: http://code.google.com/p/pybluez/

[3]: http://www.freedesktop.org/wiki/Software/DBusBindings

[4]: https://sourceforge.net/projects/pywin32/


Křížová kompilace pro Windows na Linuxu
=======================================

Potřebujete mít nainstalovaný Wine a všechny závislosti Wammu (viz výše).

Vytvoření instalátoru balíčku wammu pro Python je snadné:

    wine c:\\python25\\python setup.py build --skip-deps bdist_wininst

Ale tímto způsobem si uživatel musí nainstalovat všechny závislosti sám, což
není moc pohodlné. Toto může být vyřešeno pomocí py2exe [5]:

    wine c:\\python25\\python setup.py build --skip-deps py2exe

Ale kromě tohoto musíte provést trochu ručních úprav. Pro fungování py2exe
ve Wine, potřebujete jeho binárky opravit pomocí programu PE Tools (jak je
popsáno v chybovém hlášené na Wine [w1]) a zkopírovat nějaké další knihovny,
které chybějí v adresáři dist (python25.dll a knihovny z wxPython). Ve
skriptu admin/make-release se toto všechno udělá automaticky.

Poté můžete použít InnoSetup[6] pro vytvoření instalátoru Wammu:

    wine c:\\Program\ Files\\Inno\ Setup\ 5/\\ISCC.exe wammu.iss

[5]: http://www.py2exe.org/

[6]: http://www.jrsoftware.org/isinfo.php

[w1]: http://bugs.winehq.org/show_bug.cgi?id=3591
