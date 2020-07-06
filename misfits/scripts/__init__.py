import os

from importlib import import_module

SCRIPTS = {}

for script_file in os.listdir(__file__.rsplit('/',1)[0]):

  try: script_name, file_ext = script_file.rsplit('.',1)
  except: continue

  if script_name[:2] == '__' or file_ext != 'py': continue

  script = import_module('.' + script_name, 'misfits.scripts')

  if hasattr(script, 'main'):
    SCRIPTS[script_name] = script.main
    globals()[script_name] = script.main
