import os.path

def IconPath(*args):
    return ImagePath('icons', *args)       

def MiscPath(*args):
    return ImagePath('misc', *args)       

def ImagePath(*args):
    return os.path.join('images', *args) + os.extsep + 'png'
