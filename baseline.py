import argparse
import numpy as np
import math
import random
from samplers.binomial import BinomialDistribution
from math import sqrt as _sqrt, log2 as _log2, log as _log
from tester import intcond


def getBias(unknown, k_low, k_high, maxHeads, pivot, is_pivot_smaller):
    
    head = 0
    tot = 0
    _ncalls = 0
    # print(f"Total heads for bias estimation: {maxHeads}")
    while head < maxHeads:
        sample = intcond(unknown, k_low, k_high)
        if sample > pivot and is_pivot_smaller:
            head += 1
        elif sample < pivot and not is_pivot_smaller:
            head += 1
        tot += random.expovariate(1)
        _ncalls += 1
    bias = (head-1) / tot
    return bias, _ncalls

def Est(unknown, x, zeta, delta_Est):
    
    n = unknown.n
    k_low = 0
    k_high = n
    prob = 1
    _ncalls = 0

    maxHeads = 3 * _log(n) / zeta**2 * math.log(2 * _log(n) / delta_Est)

    while k_low != x and k_high != x:
        # print(k_high, k_low, x)
        pivot = k_low + (k_high - k_low) // 2
        bias, _calls = getBias(unknown, k_low, k_high, maxHeads, pivot, pivot<x)
        prob *= bias
        if pivot < x:
            k_low = pivot
        else:
            k_high = pivot
        _ncalls += _calls

    return prob, _ncalls


def baseline(unknown_sampler, known_sampler, eps, eta, delta, w):
    
    zeta = (eta - eps) / 2
    gamma  = zeta / (1.11 * (2 + zeta))
    t = int((2 / (zeta ** 2)) * np.log(4 / delta))
    # t = 100 # For testing purposes, set t to a small value
    print(f"Number of samples (t): {t}")
    u_low = -0.5; u_high = 0.5
    _ncalls = 0
    
    samples = [unknown_sampler.sample(u_low, u_high) for _ in range(t)]
    pest_values = []

    for i in range(t):
        print(f"Doing Sample {i}: {samples[i]}")
        x_i = samples[i]
        known_prob = known_sampler.pmf(x_i)
        if known_prob == 0:
            # Avoid log(0) issues
            return "reject"
        
        pest, _calls = Est(unknown_sampler, x_i, gamma, delta / (2 * t))

        print(f"Sample {i}: x_i = {x_i}, known_prob = {known_prob}, Estimated Mass = {pest}")
        
        if pest is None:
            return "reject"
        
        pest_values.append((x_i, pest))
        _ncalls += _calls

    dest = sum(max(0, 1 - known_sampler.pmf(x_i) / pest) for x_i, pest in pest_values) / t

    print(f"Estimated TV distance: {dest}")

    if dest > (eta + eps) / 2:
        return "reject", _ncalls
    else:
        return "accept", _ncalls


if __name__=='__main__':

    parser = argparse.ArgumentParser(description="Run the Infident algorithm with a specified distribution.")
    parser.add_argument("distribution", choices=["binomial", "poisson", "geometric"], help="Type of distribution to use.")
    parser.add_argument("--params", nargs="+", type=float, required=True, help="Parameters for the chosen distribution.")
    parser.add_argument("--eps", type=float, default=0.01, help="Epsilon value for Infident.")
    parser.add_argument("--eta", type=float, default=0.5, help="Eta value for Infident.")
    parser.add_argument("--delta", type=float, default=0.05, help="Delta value for Infident.")
    args = parser.parse_args()

    distribution = args.distribution
    params = args.params
    eps = args.eps
    eta = args.eta
    delta = args.delta

    if distribution == "binomial":
        if len(params) != 4:
            raise ValueError("Binomial distribution requires 4 parameters: n_unknown, p_unknown, n_known, p_known.")
        n_unk, p_unk, n_kn, p_kn = params
        w = n_kn * (1 - p_kn) / p_kn
        unknown_sampler = BinomialDistribution(int(n_unk), p_unk)
        known_sampler = BinomialDistribution(int(n_kn), p_kn)
    else:
        raise ValueError("Only Binomial distribution is currently supported.")


    print("Running Infident with the following parameters:")
    print(f"Parameters: {params}")
    print(f"eps: {eps}, eta: {eta}, delta: {delta}, w: {w}")

    unknown_sampler = BinomialDistribution(n_unk, p_unk)
    known_sampler = BinomialDistribution(n_kn, p_kn)

    result, _ncalls = baseline(unknown_sampler, known_sampler, eps, eta, delta, w)
    print("Result:", result, "Number of calls:", _ncalls)