import os.path

def IconPath(*args):
    return os.path.join('images','icons', *args) + os.extsep + 'png'

def MiscPath(*args):
    return os.path.join('images','misc', *args) + os.extsep + 'png'
