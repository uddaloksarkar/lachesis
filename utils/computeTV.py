import argparse
import math
import sys
sys.path.append('/Users/uddalok/Documents/PHD/projects/intCondTester/samplers')

from binomial import BinomialDistribution

def total_variation_binomial(n1, p1, n2, p2):
    binom1 = BinomialDistribution(n1, p1)
    binom2 = BinomialDistribution(n2, p2)
    tv = 0.0
    for k in range(max(n1, n2) + 1):
        pk1 = binom1.pmf(k)
        pk2 = binom2.pmf(k)
        tv += abs(pk1 - pk2)
    return 0.5 * tv


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute Total Variation Distance for Binomial Distributions.")
    parser.add_argument("--params", nargs=4, type=float, required=True, help="Parameters: n1, p1, n2, p2.")
    args = parser.parse_args()

    n1, p1, n2, p2 = args.params

    tv = total_variation_binomial(int(n1), p1, int(n2), p2)
    print(f"Total Variation Distance: {tv}")

