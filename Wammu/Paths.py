import os.path

def IconPath(*args):
    return os.path.join('icons', *args) + os.extsep + 'png'
