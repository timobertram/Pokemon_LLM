import numpy as np
from numpy import full, copyto
from numpy.random import Generator, PCG64


class DeterministicGenerator(Generator):
    def __init__(self, config_value):
        super().__init__(PCG64())
        self.config_value = config_value
        if self.config_value >= 1:
            self.config_value = 1 - np.finfo(float).eps

    def __str__(self):
        return "DeterministicGenerator(" + str(self.config_value) + ")"

    def random(self, size=None, dtype=float, out=None):
        result = full(size, self.config_value, dtype=dtype)
        if out is not None:
            copyto(out, result)
            return out
        return result


# Generator that always returns 0
ZERO_RNG = DeterministicGenerator(config_value=0)
# Generator that always returns 0.99999...
ONE_RNG = DeterministicGenerator(config_value=1)
