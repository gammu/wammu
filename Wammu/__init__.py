"""Wammu modules
"""

import sys
import gettext
__version__ = '0.1'

# First is used as default
Models = ['at', 'alcatel', 'nauto', 'obex', 'seobex']
Connections = ['at19200', 'at115200', 'fbus', 'fbusirda', 'fbusdlr3', 'fbusdku5', 'fbusblue', 'phonetblue', 'mrouterblue', 'mbus', 'irdaphonet', 'irdaat', 'irdaobex', 'bluephonet', 'bluefbus', 'blueat', 'blueobex']
if sys.platform == 'win32':
    Devices = ['com1:', 'com2:']
# FIXME: support more platforms?
else:
    Devices = ['/dev/ttyS0', '/dev/ttyS1', '/dev/ttyUSB0', '/dev/ircomm0']

gettext.install('wammu')
