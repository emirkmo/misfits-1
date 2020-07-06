import json

import numpy as np

from scipy.stats import norm

from ... import FeatureError

class Covariance (object) :

    NAME = __name__.split('.',2)[2]
    DEPENDENCIES = 'feature.fit',

    def __init__(self, spectrum, feature, output_format=None):

        self.spectrum = spectrum
        self.feature = feature

        if not self.feature:
            raise FeatureError('no feature specified')

        self._output_format = output_format

        self.__call__()

    def __call__(self):

        if not hasattr(self.feature, 'fit'):
            raise FeatureError('feature doesn\'t support fitting')

        self.data = self.feature(**self.feature.get_parameters())[:2]

        self.data = [list(zip(*data)) for data in zip(*self.data)]

    def transform(self, i, j, f):

        if hasattr(self.feature, 'transform') and hasattr(self.feature, 'references'):

            data = [self.data[i][j][0], self.data[i][j][0] + self.data[i][j][1]]
            data, units = self.feature.transform(data, self.feature.references[i][j])
            data[1] -= data[0]

            return f(data), units

        return f(self.data[i][j]), ''

    def mean(self, i, j, transformed=False):

        if transformed:
            return self.transform(i, j, lambda d: d[0])

        return self.data[i][j][0]

    def median(self, i, j, transformed=False):

        if transformed:
            return self.transform(i, j, lambda d: d[0])

        return self.data[i][j][0]

    def std(self, i, j, transformed=False):

        if transformed:
            return self.transform(i, j, lambda d: d[1])

        return self.data[i][j][1]

    def pctile(self, i, j, pct, transformed=False):

        f = lambda d: norm.ppf(np.array(pct)/100, d[0], d[1])
        if transformed:
            return self.transform(i, j, f)

        return f(self.data[i][j])

    def ascii(self):

        output = list()

        for i in range(len(self.data)):

            output.append('# [%f.2, %f.2]' % self.feature.limits[i])

            for j in range(len(self.data[i])):

                output.append(' '.join(map(str, [self.mean(i,j), self.std(i,j)])))
            
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
                    location = self.mean(i, j), stddev = self.std(i, j)
                ))

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

        s  = 32 * '-' + '\n\n'

        mean, std = self.mean(i, j, True), self.std(i, j, True)
        sig1 = self.pctile(i, j, 31.7310507863, True), self.pctile(i, j, 68.2689492137, True)
        sig2 = self.pctile(i, j, 04.5500263896, True), self.pctile(i, j, 95.4499736104, True)
        sig3 = self.pctile(i, j, 00.2699796063, True), self.pctile(i, j, 99.7300203937, True)

        d = max(2, int(2 - np.log10(std[0])))

        s += '  Location: %%.%df %%s\n' % d % mean
        s += '  Stddev: %%.%df %%s\n\n' % d % std
        s += '  1s: %%.%df, %%.%df %%s\n' % (2*(d,)) % tuple([sig1[0][0]] + list(sig1[1]))
        s += '      ~ +/-%%.%df %%s\n' % d % (np.abs(np.diff(list(zip(*sig1))[0])), sig1[0][1])
        s += '  2s: %%.%df, %%.%df %%s\n' % (2*(d,)) % tuple([sig2[0][0]] + list(sig2[1]))
        s += '      ~ +/-%%.%df %%s\n' % d % (np.abs(np.diff(list(zip(*sig2))[0])), sig2[0][1])
        s += '  3s: %%.%df, %%.%df %%s\n' % (2*(d,)) % tuple([sig3[0][0]] + list(sig3[1]))
        s += '      ~ +/-%%.%df %%s\n\n' % d % (np.abs(np.diff(list(zip(*sig3))[0])), sig3[0][1])

        return s
