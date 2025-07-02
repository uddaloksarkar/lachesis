import math
import random
from math import log as _log, exp as _exp, pi as _pi, e as _e, ceil as _ceil
from math import sqrt as _sqrt
from math import tau as TWOPI, floor as _floor, isfinite as _isfinite
from math import lgamma as _lgamma, fabs as _fabs, log2 as _log2
from operator import index as _index


class BinomialDistribution:
    def __init__(self, n, p):
        if not (0 <= p <= 1):
            raise ValueError("Probability p must be in [0, 1]")
        if n < 0:
            raise ValueError("n must be non-negative")
        self.n = n
        self.p = p
        self._setup_complete = False

    def sample(self, u_low=-0.5, u_high=0.5):
        n, p = self.n, self.p
        uniform = random.uniform

        # Fast case for p = 0 or 1
        if p == 0.0:
            return 0
        if p == 1.0:
            return n
        if n == 1:
            return int(uniform(u_low, u_high) < p)

        spq = math.sqrt(n * p * (1.0 - p))
        b = 1.15 + 2.53 * spq
        a = -0.0873 + 0.0248 * b + 0.01 * p
        c = n * p + 0.5
        vr = 0.92 - 4.2 / b

        while True:
            u = uniform(u_low, u_high)
            us = 0.5 - abs(u)
            k = math.floor((2.0 * a / us + b) * u + c)
            if k < 0 or k > n:
                continue

            v = uniform(0, 1)
            if us >= 0.07 and v <= vr:
                return k

            if not self._setup_complete:
                self._alpha = (2.83 + 5.1 / b) * spq
                self._lpq = math.log(p / (1.0 - p))
                self._m = math.floor((n + 1) * p)
                self._h = math.lgamma(self._m + 1) + math.lgamma(n - self._m + 1)
                self._setup_complete = True

            v *= self._alpha / (a / (us * us) + b)
            lhs = math.log(v)
            rhs = (
                self._h
                - math.lgamma(k + 1)
                - math.lgamma(n - k + 1)
                + (k - self._m) * self._lpq
            )
            if lhs <= rhs:
                return k

    def pmf(self, k):
        if k < 0 or k > self.n:
            return 0.0
        coeff = math.comb(self.n, k)
        return coeff * (self.p ** k) * ((1 - self.p) ** (self.n - k))

    def hat_cdf_inv(self, u):
        """
        Inverse CDF of hat distribution for rejection sampling
        """
        spq = _sqrt(self.n * self.p * (1 - self.p))
        l1 = -0.05878 + 0.062744 * spq + 0.01 * self.p
        l2 = 1.15 + 2.53 * spq
        l3 = self.n * self.p + 0.5
        return (2 * l1 / (0.5 - abs(u)) + l2) * u + l3
