import numpy as np
import math
import random
from samplers.binomial import BinomialDistribution
from math import sqrt as _sqrt, log2 as _log2
from tester import compute_H_from_inverse, intcond

def getBias(unknown, k_low, k_high, zeta_prime, pivot, which_side):
    
    head = 0
    tot = int(1/zeta_prime**2)
    for i in range(tot):
        sample = intcond(unknown, k_low, k_high)
        if sample > pivot and which_side:
            count += 1
        elif sample < pivot and not which_side:
            count += 1
    bias = count / tot
    return bias

def Est(unknown, x, zeta, delta_Est, B, w):
    
    n = unknown.n

    k_low = 0
    k_high = n
    prob = 1

    while k_low == x or k_high == x:
        pivot = k_low + (k_high - k_low) // 2
        bias = getBias(unknown, k_low, k_high, zeta/_sqrt(_log2(n)), pivot, pivot<x)
        prob *= bias
        if pivot < x:
            k_low = pivot
        else:
            k_high = pivot

    return prob


def baseline(unknown_sampler, known_sampler, eps, eta, delta, w):
    
    zeta = (eta - eps) / (eta - eps + 2)
    t = int((8 / ((eta - eps) ** 2)) * np.log(4 / delta))
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

        B = math.log((1 + 2 * eps) / known_prob)
        
        pest = Est(unknown_sampler, x_i, zeta, delta / (4 * t))

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

    p_unk = 0.42
    p_known = 0.4
    n = 40
    w = 10
    eps = 0.01
    eta = 0.5
    delta = 0.05

    unknown_sampler = BinomialDistribution(n, p_unk)
    known_sampler = BinomialDistribution(n, p_known)

    result = baseline(unknown_sampler, known_sampler, eps, eta, delta, w)
    print("Result:", result)