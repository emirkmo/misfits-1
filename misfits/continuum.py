import numpy as np

class Continuum (object) :

    def __init__(self, x, y, e, deg):

        assert len(x) > deg, 'too may parameters'
        assert all(e > 0), 'bad errors'

        F = np.array([[xi**i for xi in x] for i in np.arange(deg+1)])
        C = np.diag(1/e**2)

        self.a = y @ C @ F.T @ np.linalg.inv(F @ C @ F.T)
        self.cov = np.linalg.inv(F @ C @ F.T)

        self.p = np.poly1d(self.a[::-1])
        self.pe = lambda x: np.sqrt(np.sum([
            x**i * x**j * self.cov[i,j]
                for i in np.arange(deg+1)
                for j in np.arange(deg+1)
        ], axis=0))

    def __call__(self, x):

        return self.p(x), self.pe(x)
