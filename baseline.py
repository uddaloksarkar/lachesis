import numpy as np
import math
import random
from samplers.binomial import BinomialDistribution
from math import sqrt as _sqrt, log2 as _log2, log as _log
from tester import intcond

def getBias(unknown, k_low, k_high, maxHeads, pivot, is_pivot_smaller):
    
    head = 0
    tot = 0
    # print(f"Total heads for bias estimation: {maxHeads}")
    while head < maxHeads:
        sample = intcond(unknown, k_low, k_high)
        if sample > pivot and is_pivot_smaller:
            head += 1
        elif sample < pivot and not is_pivot_smaller:
            head += 1
        tot += random.expovariate(1)
    bias = (head-1) / tot
    return bias

def Est(unknown, x, zeta, delta_Est):
    
    n = unknown.n
    k_low = 0
    k_high = n
    prob = 1

    maxHeads = 3 * _log(n) / zeta**2 * math.log(2 * _log(n) / delta_Est)

    while k_low != x and k_high != x:
        # print(k_high, k_low, x)
        pivot = k_low + (k_high - k_low) // 2
        bias = getBias(unknown, k_low, k_high, maxHeads, pivot, pivot<x)
        prob *= bias
        if pivot < x:
            k_low = pivot
        else:
            k_high = pivot

    return prob


def baseline(unknown_sampler, known_sampler, eps, eta, delta, w):
    
    zeta = (eta - eps) / 2
    gamma  = zeta / (1.11 * (2 + zeta))
    t = int((2 / (zeta ** 2)) * np.log(4 / delta))
    t = 100 # For testing purposes, set t to a small value
    u_low = -0.5; u_high = 0.5
    
    samples = [unknown_sampler.sample(u_low, u_high) for _ in range(t)]
    pest_values = []

    for i in range(t):
        print(f"Doing Sample {i}: {samples[i]}")
        x_i = samples[i]
        known_prob = known_sampler.pmf(x_i)
        if known_prob == 0:
            # Avoid log(0) issues
            return "reject"
        
        pest = Est(unknown_sampler, x_i, gamma, delta / (2 * t))

        print(f"Sample {i}: x_i = {x_i}, known_prob = {known_prob}, Estimated Mass = {pest}")
        
        if pest is None:
            return "reject"
        
        pest_values.append((x_i, pest))

    dest = sum(max(0, 1 - known_sampler.pmf(x_i) / pest) for x_i, pest in pest_values) / t

    print(f"Estimated TV distance: {dest}")

    if dest > (eta + eps) / 2:
        return "reject"
    else:
        return "accept"


if __name__=='__main__':

    p_unk = 0.4
    p_known = 0.4
    n = 100
    w = 10
    eps = 0.01
    eta = 0.5
    delta = 0.05

    unknown_sampler = BinomialDistribution(n, p_unk)
    known_sampler = BinomialDistribution(n, p_known)

    result = baseline(unknown_sampler, known_sampler, eps, eta, delta, w)
    print("Result:", result)