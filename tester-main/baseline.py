import argparse
import numpy as np
import math
import random
import logging
from samplers.binomial import BinomialDistribution
from math import sqrt as _sqrt, log2 as _log2, log as _log
from tester import intcond
import gmpy2 as gp

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def getBias(unknown, k_low, k_high, maxHeads, pivot, is_pivot_smalleq):
    head = 0
    tot = 0
    _ncalls = 0
    while head < maxHeads:
        sample = intcond(unknown, k_low, k_high)
        if pivot <= sample and is_pivot_smalleq:
            head += 1
        elif sample < pivot and not is_pivot_smalleq:
            head += 1
        tot += random.expovariate(1)
        _ncalls += 1
    bias = (head - 1) / tot
    return bias, _ncalls

def Est(unknown, x, zeta, delta_Est):
    n = unknown.n
    k_low = 0
    k_high = n
    prob = gp.mpfr(1)
    _ncalls = 0

    maxHeads = 3 * _log(n) / zeta**2 * math.log(2 * _log(n) / delta_Est)

    while k_low < k_high -1 :
        pivot = k_high - (k_high - k_low) // 2
        bias, _calls = getBias(unknown, k_low, k_high, maxHeads, pivot, pivot <= x)
        prob *= gp.mpfr(bias)
        if pivot <= x:
            k_low = pivot
        else:
            k_high = pivot -1
        _ncalls += _calls

    return prob, _ncalls

def baseline(unknown_sampler, known_sampler, eps, eta, delta, w):
    zeta = (eta - eps) / 2
    gamma = zeta / (1.11 * (2 + zeta))
    t = int((2 / (zeta ** 2)) * np.log(4 / delta))
    # t = 10
    logger.info(f"Number of samples (t): {t}")
    u_low = -0.5
    u_high = 0.5
    _ncalls = 0

    samples = [unknown_sampler.sample(u_low, u_high) for _ in range(t)]
    pest_values = []

    for i in range(t):
        logger.info(f"Processing Sample {i}: {samples[i]}")
        x_i = samples[i]
        known_prob = known_sampler.pmf(x_i)
        if known_prob == 0:
            logger.error(f"Sample {i}: known_prob is 0 for x_i = {x_i}. Rejecting the sampler.")
            return "reject", _ncalls

        pest, _calls = Est(unknown_sampler, x_i, gamma, delta / (2 * t))
        _ncalls += _calls

        logger.info(f"Sample {i}: x_i = {x_i}, known_prob = {known_prob}, Estimated Mass = {pest}")

        if pest is None:
            return "reject", _ncalls

        pest_values.append((x_i, pest))

    dest = sum(max(0, 1 - known_sampler.pmf(x_i) / pest) for x_i, pest in pest_values) / t
    dest = float(dest)
    logger.info(f"Estimated TV distance: {dest}")

    if dest > (eta + eps) / 2:
        return "reject", _ncalls
    else:
        return "accept", _ncalls


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Infident algorithm with a specified distribution.")
    parser.add_argument("distribution", choices=["binomial", "poisson", "geometric"], help="Type of distribution to use.")
    parser.add_argument("--params", nargs="+", type=float, required=True, help="Parameters for the chosen distribution.")
    parser.add_argument("--eps", type=float, default=0.01, help="Epsilon value for Infident.")
    parser.add_argument("--eta", type=float, default=0.5, help="Eta value for Infident.")
    parser.add_argument("--delta", type=float, default=0.05, help="Delta value for Infident.")
    parser.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    args = parser.parse_args()

    distribution = args.distribution
    params = args.params
    eps = args.eps
    eta = args.eta
    delta = args.delta
    seed = args.seed

    if seed is not None:
        random.seed(seed)

    file_handler = logging.FileHandler(f"{distribution}_{'_'.join(str(p) for p in params)}.log")
    logger.addHandler(file_handler)

    if distribution == "binomial":
        if len(params) != 4:
            raise ValueError("Binomial distribution requires 4 parameters: n_unknown, p_unknown, n_known, p_known.")
        n_unk, p_unk, n_kn, p_kn = params
        n_unk, p_unk, n_kn, p_kn = int(n_unk), float(p_unk), int(n_kn), float(p_kn)
        w = n_kn * (1 - p_kn) / p_kn
        unknown_sampler = BinomialDistribution(n_unk, p_unk)
        known_sampler = BinomialDistribution(n_kn, p_kn)
    else:
        raise ValueError("Only Binomial distribution is currently supported.")

    logger.info("Running Infident with the following parameters:")
    logger.info(f"Parameters: {params}")
    logger.info(f"eps: {eps}, eta: {eta}, delta: {delta}, w: {w}")

    result, _ncalls = baseline(unknown_sampler, known_sampler, eps, eta, delta, w)
    logger.info(f"Decision: {result}, Number of calls: {_ncalls}")