from setuptools import setup, find_packages

from misfits import __version__
from misfits.scripts import SCRIPTS

setup(
    name = 'MISFITS',
    author = 'Simon Holmbo',
    description = 'Measure Intricate Spectral Features In Transient Spectra',
    version = __version__,
    packages = find_packages(),
    entry_points = {
        'console_scripts' :
            ['{0} = misfits.scripts:{0}'.format(script) for script in SCRIPTS],
    },
    include_package_data = True,
)
