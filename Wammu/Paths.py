import os
import os.path
import sys

datapath = os.path.join(sys.exec_prefix, 'share', 'Wammu')
if not os.path.exists(os.path.join(datapath, 'images')):
    if not os.path.exists('images'):
        print 'Could not find images, you will not see them, check your installation!'
    else:
        datapath = os.getcwd()

def IconPath(*args):
    return ImagePath('icons', *args)       

def MiscPath(*args):
    return ImagePath('misc', *args)       

def ImagePath(*args):
    return os.path.join(datapath, 'images', *args) + os.extsep + 'png'
