Установка Wammu
===============

Пакеты для Linux
================

Многие дистрибутивы включают в себя бинарные пакеты Wammu, это наиболее
легкий способ, чтобы использовать программу. Бинарные пакеты последнего
релиза для многих дистрибутивов доступны на сайте
<http://wammu.eu/download/wammu/>.


Сборка из исходных текстов
==========================

Она используется стандартные утилиты:

    python setup.py build
    sudo python setup.py install

Для установки и запуска этой программы Вам нужны python-gammu и wxPython [1]
(с поддержкой юникода). Если Вы хотите иметь поддержку сканирования
устройств Bluetooth, Вам нужен PyBluez [2]. Для уведомления о событиях -
dbus-python [3].

Для Windows нужно установить Pywin32 [4].

Если Вы не хотите проверять зависимости при сборке, используйте опцию
--skip-deps.

[1]: http://wxpython.org/

[2]: http://code.google.com/p/pybluez/

[3]: http://www.freedesktop.org/wiki/Software/DBusBindings

[4]: https://sourceforge.net/projects/pywin32/


Кросскомпиляция для Windows в Linux
===================================

Вам нужен Wine со всеми установленными зависимостями (смотрите раздел выше
чтобы получить их).

Собрать установщик wammu на Python легко:

    wine c:\\python25\\python setup.py build --skip-deps bdist_wininst

Однако в таком случае нужно установить все зависимости, что неудобно. Это
можно решить, используя py2exe [5]:

    wine c:\\python25\\python setup.py build --skip-deps py2exe

Но, несмотря на это, Вам нужно сделать некоторые настройки вручную. Чтобы
заставить работать py2exe в Wine, необходимо исправить исполняемый файл,
используя PE Tools (описано в отчете об ошибках Wine [w1]) и скопировать
несколько дополнительных библиотек, которых нет в директории установки
(python25.dll и библиотеки из wxPython). Смотрите скрипт admin/make-release,
который автоматизирует это.

Вы также можете использовать InnoSetup[6] для сборки установщика Wammu:

    wine c:\\Program\ Files\\Inno\ Setup\ 5/\\ISCC.exe wammu.iss

[5]: http://www.py2exe.org/

[6]: http://www.jrsoftware.org/isinfo.php

[w1]: http://bugs.winehq.org/show_bug.cgi?id=3591
