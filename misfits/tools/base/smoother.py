import numpy as np

from .basetool import BaseTool

class BaseSmoother (BaseTool) :

    def get_mask(self):

        mask = np.ones(self.spectrum.N, dtype=bool)
        if len(self.flagged):
            mask[np.array(self.flagged)] = False

        return mask
