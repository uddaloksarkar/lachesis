import argparse
import math
import sys
sys.path.append('/Users/uddalok/Documents/PHD/projects/intCondTester/samplers')

from binomial import BinomialDistribution
from poisson import PoissonDistribution
from geometric import GeometricDistribution

def total_variation(distribution, params):
    """
    Compute the Total Variation Distance (TVD) between two distributions.

    Args:
        distribution (str): The type of distribution ("binomial", "poisson", "geometric").
        params (list): Parameters for the distributions.

    Returns:
        float: The Total Variation Distance.
    """
    if distribution == "binomial":
        n1, p1, n2, p2 = params
        dist1 = BinomialDistribution(int(n1), p1)
        dist2 = BinomialDistribution(int(n2), p2)
        max_k = max(int(n1), int(n2))
    elif distribution == "poisson":
        lambd1, lambd2 = params
        dist1 = PoissonDistribution(lambd1)
        dist2 = PoissonDistribution(lambd2)
        max_k = int(max(lambd1, lambd2) * 5)  # Approximation for Poisson
    elif distribution == "geometric":
        p1, p2 = params
        dist1 = GeometricDistribution(p1)
        dist2 = GeometricDistribution(p2)
        max_k = 100  # Limit for geometric distribution
    else:
        raise ValueError("Unsupported distribution type.")

    tv = 0.0
    for k in range(max_k + 1):
        pk1 = dist1.pmf(k)
        pk2 = dist2.pmf(k)
        tv += abs(pk1 - pk2)
    return 0.5 * tv


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute Total Variation Distance for Distributions.")
    parser.add_argument("distribution", choices=["binomial", "poisson", "geometric"], help="Type of distribution.")
    parser.add_argument("--params", nargs="+", type=float, required=True, help="Parameters for the chosen distribution.")
    args = parser.parse_args()

    distribution = args.distribution
    params = args.params

    if distribution == "binomial" and len(params) != 4:
        raise ValueError("Binomial distribution requires 4 parameters: n1, p1, n2, p2.")
    elif distribution == "poisson" and len(params) != 2:
        raise ValueError("Poisson distribution requires 2 parameters: lambda1, lambda2.")
    elif distribution == "geometric" and len(params) != 2:
        raise ValueError("Geometric distribution requires 2 parameters: p1, p2.")

    tv = total_variation(distribution, params)
    print(f"Total Variation Distance ({distribution}): {tv}")

