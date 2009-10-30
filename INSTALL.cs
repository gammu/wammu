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

You need python-gammu and wxPython [1] (Unicode enabled build) installed to
run and install this program. If you want support for scanning Bluetooth
devices, you need PyBluez [2]. For incoming events notifications, you need
dbus-python [3].

Na Windows take budete muset nainstalovat Pywin32 [4].

Pokud chcete z jakéhokoliv důvodu přeskočit kontrolování závislostí, můžete
použít parametr --skip-deps.

[1]: http://wxpython.org/ [2]: http://code.google.com/p/pybluez/ [3]:
http://www.freedesktop.org/wiki/Software/DBusBindings [4]:
https://sourceforge.net/projects/pywin32/


Křížová kompilace pro Windows na Linuxu
=======================================

Potřebujete mít nainstalovaný Wine a všechny závislosti Wammu (viz výše).

Vytvoření instalátoru balíčku wammu pro Python je snadné:

    wine c:\\python25\\python setup.py build --skip-deps bdist_wininst

However this way user needs to also install all dependencies, what is really
not comfortable. This should be solved using py2exe [5]:

    wine c:\\python25\\python setup.py build --skip-deps py2exe

But except of this, you need to do a bit of manual tuning. To make py2exe
work in Wine, you need to fix it's binary using PE Tools (described in bug
report on Wine [w1]) and copy some extra libraries which are missing to dist
directory (python25.dll and libraries from wxPython). See script
admin/make-release which automates this copying.

Poté můžete použít InnoSetup[6] pro vytvoření instalátoru Wammu:

    wine c:\\Program\ Files\\Inno\ Setup\ 5/\\ISCC.exe wammu.iss

[5]: http://www.py2exe.org/ [6]: http://www.jrsoftware.org/isinfo.php

[w1]: http://bugs.winehq.org/show_bug.cgi?id=3591

# vim: et ts=4 sw=4 sts=4 tw=72 spell spelllang=en_us
