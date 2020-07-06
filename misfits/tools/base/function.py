from .basetool import BaseTool

import numpy as np

from scipy.optimize import minimize, curve_fit

class BaseToolFunction (BaseTool) :

    def __init__(self, spectrum):

        super(BaseToolFunction, self).__init__(spectrum)

        self.fit = self.curvefit

    def param_ravel(self, inputs):

        structure, outputs = dict(), list()
        for k,v in sorted(inputs.items()):
            structure[k] = len(v)
            outputs += v

        return outputs, structure

    def param_unravel(self, inputs, structure):

        i, outputs = 0, dict()
        for k,v in sorted(structure.items()):
            outputs[k] = list(inputs[i:i+v])
            i += v

        return outputs

    def minimize(self, f, x, y, e=None, jac=None, **kw0):

        a0, structure = self.param_ravel(kw0)

        def chi2(a):
            kw = self.param_unravel(a, structure)
            return np.sum( np.power( f(x, **kw) - y , 2 ) )
        def chi2_der(a):
            kw = self.param_unravel(a, structure)
            return np.sum( 2 * ( f(x, **kw) - y ) * jac(x, **kw) , axis=1 )

        if not jac:
            options = dict(maxiter=1000*(1+len(a0)), maxfev=1000*(1+len(a0)))
            res = minimize(chi2, a0, method='Nelder-Mead', options=options)
        else:
            res = minimize(chi2, a0, method='Newton-CG', jac=chi2_der) #FIXME
        a = res.x if res.success else len(res.x) * [None]

        return self.param_unravel(a, structure), None, chi2(a)

    def curvefit(self, f, x, y, e, jac=None, fixed=(), **kw0):

        #def _(d): return {**d, **{p:kw0[p] for p in fixed}} # python3
        def _(d): _d = d.copy(); _d.update({p:kw0[p] for p in fixed}); return _d #FIXME with python3

        a0, structure = self.param_ravel({p:v for p,v in kw0.items() if not p in fixed})

        wrap = lambda f: lambda x, *a: f(x, **_(self.param_unravel(a, structure)))
        try:
            a, cov = curve_fit(wrap(f), x, y, a0, sigma=e, absolute_sigma=True, maxfev=1000*(1+len(a0)))
        except (ValueError, RuntimeError, TypeError):
            a, std, chi2 = len(a0) * [None], len(a0) * [None], None
        else:
            std = np.sqrt(np.diag(cov))
            chi2 = np.sum((wrap(f)(x, *a) - y)**2 / e**2) / (len(x) - len(a))

        a = _(self.param_unravel(a, structure))
        std = _(self.param_unravel(std, structure))

        return a, std, chi2
