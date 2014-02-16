Instalación de Wammu
====================

Paquetes para Linux
===================

Muchas distribuciones ya vienen con binarios de Wammu, si puede usarlos
definitivamente representan lo más fácil. También hay paquetes binarios de
la última versión disponibles desde el sitio web de Wammu
<http://wammu.eu/download/wammu/>.


Compilando desde código fuente
==============================

Utiliza distutils estándar, por lo que:

    python setup.py build
    sudo python setup.py install

Necesitas tener instalado python-gammy y wxPython [1] (compilación con
soporte Unicode) para poder ejecutar e instalar este programa. Si quieres
soporte para escanear dispositivos Bluetooth necesitas PyBluez [2]. Para
notificación de eventos entrantes necesitas dbus-python [3].

Para Windows también debe instalar Pywin32 [4].

Si quieres obedecer el chequeo de dependencias en tiempo de compilación por
alguna razón, puedes utilizar la opción --skip-deps.

[1]: http://wxpython.org/

[2]: http://code.google.com/p/pybluez/

[3]: http://www.freedesktop.org/wiki/Software/DBusBindings

[4]: https://sourceforge.net/projects/pywin32/


Compilación cruzada para Windows en Linux
=========================================

Necesita Wine con todas las dependencias instaladas (vea la sección anterior
donde obtenerlas).

Compilar el instalador para wammu para Python es fácil:

    wine c:\\python25\\python setup.py build --skip-deps bdist_wininst

De esta forma sin embargo, el usuario también necesita instalar todas las
dependencias; lo que no es realmente muy cómodo. Esto se resolvería
utilizando py2exe [5]:

    wine c:\\python25\\python setup.py build --skip-deps py2exe

Excepto por esto, necesitas realizar un poco de refinamiento manual. Para
hacer funcionar py2exe con Wine necesitas corregir el binario utilizando PE
Tools (descripto en el reporte de error en Wine [w1]) y copiar algunas
bibliotecas extras faltantes al directorio dist (python25.dll y bibliotecas
de wxPython). Revisa el script admin/make-release que automatiza este
copiado.

Entonces puede usar InnoSetup[6] para compilar el instalador para Wammu:

    wine c:\\Program\ Files\\Inno\ Setup\ 5/\\ISCC.exe wammu.iss

[5]: http://www.py2exe.org/

[6]: http://www.jrsoftware.org/isinfo.php

[w1]: http://bugs.winehq.org/show_bug.cgi?id=3591
