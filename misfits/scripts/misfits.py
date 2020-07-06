import argparse
from copy import deepcopy
from warnings import filterwarnings

import numpy as np

from .. import __version__, readfile, update_parameter_header
from ..gui import Simple, SimpleMultipage

from ..gui.tools import smooth
from ..gui.tools import error
from ..gui.tools import velocity
from ..gui.tools import width
from ..gui.tools import uncertainty

filterwarnings('ignore')

feature = type('',(object,),dict(METHODS={}))
for method, function in velocity.METHODS.items():
    feature.METHODS['velocity.' + method] = function
for method, function in width.METHODS.items():
    feature.METHODS['width.' + method] = function

def main():

    parser = argparse.ArgumentParser(
        description='Measure Intricate Spectral Features In Transient Spectra',
        formatter_class=lambda prog: argparse.RawTextHelpFormatter(prog,  max_help_position=30),
        epilog='example:\n  $ misfits lowpass rawsmooth velocity.gaussians montecarlo spectrum.fits -z 0.01'
    )
  
    methods = ''.join(['\n    %s - %s' % (k, v.__doc__.split('\n')[2]) for k, v in smooth.METHODS.items()])
    parser.add_argument('smooth', metavar='smooth', choices=list(smooth.METHODS.keys()) + ['-'], help='smoothing method' + methods)
    methods = ''.join(['\n    %s - %s' % (k, v.__doc__.split('\n')[2]) for k, v in error.METHODS.items()])
    parser.add_argument('error', metavar='error', choices=list(error.METHODS.keys()) + ['-'], help='error estimate method' + methods)
    methods = ''.join(['\n    %s - %s' % (k, v.__doc__.split('\n')[2]) for k, v in feature.METHODS.items()])
    parser.add_argument('feature', metavar='feature', choices=list(feature.METHODS.keys()) + ['-'], help='feature and measuring method' + methods)
    methods = ''.join(['\n    %s - %s' % (k, v.__doc__.split('\n')[2]) for k, v in uncertainty.METHODS.items()])
    parser.add_argument('uncertainty', metavar='uncertainty', choices=list(uncertainty.METHODS.keys()) + ['-'], help='uncertainty estimate method' + methods)

    options  = '\n    fits - 1D primary HDU with CRVAL1 and CDELT1 or CD1_1'
    options += '\n    ascii - Minimum wavelength and flux columns (optional error and smooth)'
    parser.add_argument('spectrum', help='spectrum file' + options)

    parser.add_argument('-z', metavar='redshift', default=0, type=float, help='object redshift (default: 0)')
    parser.add_argument('-N', metavar='iterations', default=1000, type=int, help='sampling iterations (default: 1000)')
    parser.add_argument('--continuum-error', metavar='fraction', default=0, type=float, help='fraction of flux as continuum error (default: 0)')
    parser.add_argument('--fix-continuum', action='store_true', default=False, help='don\'t fit the continuum')
    parser.add_argument('--headless', action='store_true', help='run automatically without gui')
    parser.add_argument('--inherit', metavar='filename', help='inherit metadata from spectrum')
    parser.add_argument('--output', metavar='format', default='ascii', choices=('ascii', 'json', 'none'), help='format of output (default: ascii)')
    parser.add_argument('--save', metavar='filename', help='save spectrum-data to file')
    parser.add_argument('--version', action='version', version=__version__,  help='print the current version of misfits')

    args = parser.parse_args()

    spectrum, header = readfile(args.spectrum)
    spectrum.set_redshift(args.z)
    spectrum.set_continuum_error(args.continuum_error)

    args.output = args.output if args.output != 'none' else None

    if not args.inherit is None:
        #header = {**readfile(args.inherit)[1], **header} # python3
        header, _header = readfile(args.inherit)[1], header #FIXME with python3
        header.update(_header)

    if not args.smooth == '-':
        gui = Simple() if not args.headless else None
        smooth_method = smooth.METHODS[args.smooth](gui, spectrum, header)
        if not args.headless:
            gui.mainloop()
        update_parameter_header(smooth_method, header)
    else:
        smooth_method = None

    if not args.error == '-':
        gui = Simple() if not args.headless else None
        error_method = error.METHODS[args.error](gui, spectrum, header)
        if not args.headless:
            gui.mainloop()
        update_parameter_header(error_method, header)
    else:
        error_method = None

    if not args.feature == '-':
        gui = Simple() if not args.headless else None
        params = args.fix_continuum,
        feature_method = feature.METHODS[args.feature](gui, spectrum, header, *params)
        if not args.headless:
            gui.mainloop()
        update_parameter_header(feature_method, header)
    else:
        feature_method = None

    if not args.uncertainty == '-':
        gui = SimpleMultipage() if not args.headless else None
        params = feature_method, args.output, args.N, smooth_method
        uncertainty_method = uncertainty.METHODS[args.uncertainty](gui, spectrum, *params)
        if args.output:
            print(uncertainty_method)
        if not args.headless:
            gui.mainloop()
    else:
        uncertainty_method = None

    if args.save:
        if args.save == '-':
            args.save = None
        spectrum.save(str(header), args.save)
