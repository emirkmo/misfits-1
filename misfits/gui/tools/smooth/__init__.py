import os

from importlib import import_module

METHODS = {}

for method_file in os.listdir(__file__.rsplit('/',1)[0]):

    try:
        method_name, file_ext = method_file.rsplit('.',1)
    except:
        continue

    if method_name[:2] == '__' or file_ext != 'py':
        continue

    method = import_module('.' + method_name, 'misfits.gui.tools.smooth')

    if hasattr(method, 'main'):

        METHODS[method_name] = method.main
        globals()[method_name] = method.main
