import sys, time, json
from copy import deepcopy

import numpy as np

from ... import FeatureError, MethodError

from ..base import BaseIterator

class MonteCarlo (BaseIterator) :

    NAME = __name__.split('.',2)[2]
    DEPENDENCIES = 'spectrum.error',

    def __init__(self, spectrum, feature, output_format=None, N=1000, smooth=None):

        self.spectrum = spectrum
        self.sample = deepcopy(spectrum)

        self.feature = feature
        self.smooth = smooth

        if not self.feature:
            raise FeatureError('no feature specified')

        if 'method.smooth' in self.feature.DEPENDENCIES and not self.smooth:
            raise MethodError('no smoothing method specified')

        self.params = self.feature.get_parameters()

        self.N = N

        self._output_format = output_format

        self.__call__()

    def __call__(self):

        self.data = []

        t0, l = time.time(), 0
        for i in range(self.N):

            if i:

                t = time.time()
                s = 'Process: %d%% (t - %ds)' % (100*i/self.N, (self.N/i-1) * (t-t0))
                l = max(l, len(s))

                print(s.ljust(l)[:80], file=sys.stderr, end='\r')

            flux = self.spectrum.sample()
            self.sample.set_flux(flux)

            if 'method.smooth' in self.feature.DEPENDENCIES:

                self.smooth.set_spectrum(self.sample)
                self.sample.set_smooth(self.smooth(**self.smooth.get_parameters()))

            self.feature.set_spectrum(self.sample)

            res = self.feature(**deepcopy(self.params))
            self.data.append(res[0])

        print(''.ljust(l), file=sys.stderr, end='\r')

        self.feature.set_parameters(**self.params)

        self.data = [zip(*data) for data in zip(*self.data)]
        self.data = [[tuple(filter(None,data)) for data in section] for section in self.data]

    def transform(self, i, j, f):

        if hasattr(self.feature, 'transform') and hasattr(self.feature, 'references'):

            data, units = self.feature.transform(self.data[i][j], self.feature.references[i][j])

            return f(data), units

        return f(self.data[i][j]), ''

    def min(self, i, j, transformed=False):

        if transformed:
            return self.transform(i, j, np.min)

        return np.min(self.data[i][j])

    def max(self, i, j, transformed=False):

        if transformed:
            return self.transform(i, j, np.max)

        return np.max(self.data[i][j])

    def len(self, i, j=None):

        if j is None:
            return len(self.data[i])

        return len(self.data[i][j])

    def mean(self, i, j, transformed=False):

        if transformed:
            return self.transform(i, j, np.mean)

        return np.mean(self.data[i][j])

    def median(self, i, j, transformed=False):

        if transformed:
            return self.transform(i, j, np.median)

        return np.median(self.data[i][j])

    def std(self, i, j, transformed=False):

        if transformed:
            return self.transform(i, j, np.std)

        return np.std(self.data[i][j])

    def pctile(self, i, j, pct, transformed=False):

        if transformed:
            return self.transform(i, j, lambda d: np.percentile(d,pct))

        return np.percentile(self.data[i][j], pct)

    def ascii(self):

        output = list()

        for i in range(len(self.data)):

            output.append('# [%f.2, %f.2]' % self.feature.limits[i])

            for j in range(len(self.data[i])):

                if self.len(i, j):
                    output.append(' '.join(map(str, [self.mean(i, j), self.std(i, j)])))
                else:
                    output.append('')
            
            output.append('')

        return '\n'.join(output).strip()

    def json(self):

        output = dict(
            method = self.feature.NAME,
            limits = []
        )

        for i in range(len(self.data)):

            output['limits'].append(dict(
                lower = self.feature.limits[i][0],
                upper = self.feature.limits[i][1],
                results = []
            ))

            for j in range(len(self.data[i])):

                output['limits'][-1]['results'].append(dict(
                    success_rate = self.len(i, j) / self.N,
                    min = self.min(i, j), max = self.max(i, j),
                    mean = self.mean(i, j), median = self.median(i, j), stddev = self.std(i, j)
                ))

                if hasattr(self.feature, 'references'):
                    output['limits'][-1]['results'][-1]['reference'] = \
                        self.feature.references[i][j]

                output['limits'][-1]['results'][-1]['1-sigma'] = \
                    self.pctile(i, j, 31.7310507863), self.pctile(i, j, 68.2689492137)
                output['limits'][-1]['results'][-1]['2-sigma'] = \
                    self.pctile(i, j, 04.5500263896), self.pctile(i, j, 95.4499736104)
                output['limits'][-1]['results'][-1]['3-sigma'] = \
                    self.pctile(i, j, 00.2699796063), self.pctile(i, j, 99.7300203937)

        return str(json.dumps(output))

    def __str__(self):

        return {
            'ascii' : self.ascii,
            'json'  : self.json,
        }.get(self._output_format, lambda:None)()

    def summary(self, i, j):

        if not len(self.data[i]):
            return ''

        l = self.len(i, j)

        s  = 32 * '-' + '\n\n'
        s += '  Success rate:\n    %d/%d (%.2f%%)\n\n' % (l, self.N, 100.*l/self.N)

        if not l:
            return s

        _min, _max = self.min(i, j, True), self.max(i, j, True)
        mean, median, std = self.mean(i, j, True), self.median(i, j, True), self.std(i, j, True)
        sig1 = self.pctile(i, j, 31.7310507863, True), self.pctile(i, j, 68.2689492137, True)
        sig2 = self.pctile(i, j, 04.5500263896, True), self.pctile(i, j, 95.4499736104, True)
        sig3 = self.pctile(i, j, 00.2699796063, True), self.pctile(i, j, 99.7300203937, True)

        d = max(2, int(2 - np.log10(self.std(i, j))))

        s += '  Min: %%.%df %%s\n' % d % _min
        s += '  Max: %%.%df %%s\n\n' % d % _max
        s += '  Mean: %%.%df %%s\n' % d % mean
        s += '  Median: %%.%df %%s\n' % d % median
        s += '  Stddev: %%.%df %%s\n\n' % d % std
        s += '  1s: %%.%df, %%.%df %%s\n' % (2*(d,)) % tuple([sig1[0][0]] + list(sig1[1]))
        s += '      ~ +/-%%.%df %%s\n' % d % (np.abs(np.diff(list(zip(*sig1))[0])), sig1[0][1])
        s += '  2s: %%.%df, %%.%df %%s\n' % (2*(d,)) % tuple([sig2[0][0]] + list(sig2[1]))
        s += '      ~ +/-%%.%df %%s\n' % d % (np.abs(np.diff(list(zip(*sig2))[0])), sig2[0][1])
        s += '  3s: %%.%df, %%.%df %%s\n' % (2*(d,)) % tuple([sig3[0][0]] + list(sig3[1]))
        s += '      ~ +/-%%.%df %%s\n\n' % d % (np.abs(np.diff(list(zip(*sig3))[0])), sig3[0][1])

        return s
