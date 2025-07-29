import math
import random
from math import log as _log, exp as _exp, pi as _pi, e as _e, ceil as _ceil
from math import sqrt as _sqrt
from math import floor as _floor, isfinite as _isfinite
from math import lgamma as _lgamma, fabs as _fabs, log2 as _log2
from operator import index as _index
import matplotlib.pyplot as plt  # Add this import for plotting


class PoissonDistribution:
    def __init__(self, lambd):
        if lambd < 0:
            raise ValueError("Lambda must be non-negative")
        self.lambd = lambd
        self._setup_complete = False

    def sample(self, u_low=-0.5, u_high=0.5):
        """PTRS
        """
        lambd = self.lambd
        uniform = random.uniform

        if lambd < 10 :
            exlam = _exp(-lambd)
            k = 0
            prod = 1
            while True:
                U = uniform(0,1)
                prod *= U
                if prod > exlam:
                    k += 1
                else:
                    return k
        else:
            lnlam = _log(lambd)
            b = 1.931 + 4.53 * _sqrt(lambd)
            a = - 0.559 + 0.14483 * b
            vr = 0.9277 - 3.6224 / (b - 2)
            invalpha = 1.1239 + 1.1328 / (b - 3.4)
            
            while True:
                U = uniform(u_low, u_high)
                V = uniform(0, 1)
                lv = _log(V)
                us = 0.5 - _fabs(U)
                k = math.floor((2 * a / us + b) * U + lambd + 0.445)
                if (us >= 0.07) and (V <= vr):
                    return k
                if (k <= 0) or (us < 0.013 and V > us):
                    continue
                if (lv + _log(invalpha) - _log(a/us**2 + b)) <= k*lnlam -lambd - _lgamma(k):
                    return k 
                
    def pmf(self, k):
        """Probability Mass Function for Poisson distribution."""
        if k < 0 or not isinstance(k, int):
            return 0.0
        mass = k * math.log(self.lambd) - self.lambd - math.lgamma(k + 1)
        return math.exp(mass)
    
    def hat_cdf_inv(self, u):
        """Inverse CDF for Poisson distribution."""
        b = 1.931 + 4.53 * _sqrt(self.lambd)
        a = - 0.559 + 1.02483 * b
        return (2 * a / (0.5 - abs(u)) + b) * u + self.lambd + 0.445
    
    def _histogram(self, n_samp=100):
        """Generate a histogram of the Poisson distribution."""    
        hist = {}
        for i in range(n_samp):
            sample = self.sample()
            hist[sample] = hist.get(sample, 0) + 1
        total_samples = sum(hist.values())
        for k in hist:
            hist[k] /= total_samples
        return hist
    
    def __test__(self, n_samp=100):
        """Plot the histogram of the Poisson distribution."""
        hist = self._histogram(n_samp)
        keys = sorted(hist.keys())
        values = [hist[k] for k in keys]
        plt.bar(keys, values, width=0.8, color='blue', alpha=0.7)
        plt.title(f"Poisson Distribution (λ={self.lambd})")
        plt.xlabel("k")
        plt.ylabel("Probability")
        plt.show()


if __name__ == "__main__":
    # Example usage for testing
    lambd = 1  # Set lambda value for Poisson distribution
    poisson = PoissonDistribution(lambd)
    poisson.__test__(n_samp=100000)  # Plot histogram with 1000 samples


