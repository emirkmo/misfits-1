from ast import literal_eval

import numpy as np
from astropy.io import fits

from .spectrum import Spectrum
from .errors import WavelengthError

def readfile(f):

    fd = f if hasattr(f, 'seek') else open(f, 'rb')

    if is_fits(fd):

        fd.seek(0)

        with fits.open(fd) as hdul:

            if len(hdul[0].data.shape) == 1:
                wave = get_wavelength(hdul)
                data = [wave, hdul[0].data]
            else:
                data = list(hdul[0].data)

        header = {}

    elif is_ascii(fd):

        fd.seek(0)
        data = np.loadtxt(fd, unpack=True)

        fd.seek(0)
        header = _get_header(fd)

    else:

        raise IOError('unknown fileformat')

    spectrum = Spectrum(*data)

    if not fd is f:

        fd.close()

    return spectrum, header

def _get_header(fd):

    line = fd.readline().decode('ascii')

    if line[0] != '#': return {}

    try:
        header = literal_eval(line[1:].strip())
    except:
        return {}

    if not type(header) is dict:
        return {}

    return header

def get_wavelength(hdul):

    head = hdul[0].header

    if 'naxis1' in head:
        n = head['naxis1']
    else:
        raise WavelengthError('can\'t find length in header')

    if 'crval1' in head:
        b = head['crval1']
    else:
        raise WavelengthError('can\'t find offset in header')

    if 'cdelt1' in head:
        a = head['cdelt1']
    elif 'cd1_1' in head:
        a = head['cd1_1']
    else:
        raise WavelengthError('can\'t find delta in header')

    return b + np.arange(n) * a

def is_fits(fd):

    fd.seek(0)

    try:
        hdul = fits.open(fd)
        hdul[0].data
    except:
        return False
    else:
        return True

def is_ascii(fd):

    fd.seek(0)

    try:
        np.loadtxt(fd, unpack=True)[1][1]
    except:
        return False
    else:
        return True
