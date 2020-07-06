from setuptools import setup, find_packages

from misfits import __version__
from misfits.scripts import SCRIPTS

import time # XXX
setup(
    name = 'MISFITS',
    author = 'Simon Holmbo',
    description = 'Measure Intricate Spectral Features In Transient Spectra',
    version = '%d%s' % (int(time.time()), __version__), # XXX
    packages = find_packages(),
    entry_points = {
        'console_scripts' :
            ['{0} = misfits.scripts:{0}'.format(script) for script in SCRIPTS],
    },
    include_package_data = True,
)
