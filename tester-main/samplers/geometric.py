import math
import random
from math import log as _log, exp as _exp, pi as _pi, e as _e, ceil as _ceil
from math import sqrt as _sqrt
from math import floor as _floor, isfinite as _isfinite
from math import lgamma as _lgamma, fabs as _fabs, log2 as _log2
from operator import index as _index
import matplotlib.pyplot as plt  # Add this import for plotting


class GeometricDistribution:
    def __init__(self, p):
        if not (0 < p <= 1):
            raise ValueError("Probability p must be in (0, 1]")
        self.p = p

    def sample(self, u_low=-0.5, u_high=0.5):
        """Sample from the Geometric distribution."""
        uniform = random.uniform
        U = uniform(u_low, u_high) 
        return math.ceil(_log(0.5 - U) / _log(1 - self.p))

    def pmf(self, k):
        """Probability Mass Function for Geometric distribution."""
        if k < 1 or not isinstance(k, int):
            return 0.0
        return self.p * ((1 - self.p) ** (k - 1))

    def hat_cdf_inv(self, u):
        """Inverse CDF for Geometric distribution."""
        return math.ceil(_log(0.5 - u) / _log(1 - self.p))

    def _histogram(self, n_samp=100):
        """Generate a histogram of the Geometric distribution."""
        hist = {}
        for _ in range(n_samp):
            sample = self.sample()
            hist[sample] = hist.get(sample, 0) + 1
        total_samples = sum(hist.values())
        for k in hist:
            hist[k] /= total_samples
        return hist

    def __test__(self, n_samp=100):
        """Plot the histogram of the Geometric distribution."""
        hist = self._histogram(n_samp)
        keys = sorted(hist.keys())
        values = [hist[k] for k in keys]
        plt.bar(keys, values, width=0.8, color='purple', alpha=0.7)
        plt.title(f"Geometric Distribution (p={self.p})")
        plt.xlabel("k")
        plt.ylabel("Probability")
        plt.show()


if __name__ == "__main__":
    # Example usage for testing
    p = 0.4  # Set probability for Geometric distribution
    geometric = GeometricDistribution(p)
    geometric.__test__(n_samp=100000)  # Plot histogram with 100,000 samples


