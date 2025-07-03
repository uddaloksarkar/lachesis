import argparse
import numpy as np
import math
import random
import logging
from samplers.binomial import BinomialDistribution
from samplers.poisson import PoissonDistribution
from samplers.geometric import GeometricDistribution

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

def compute_H_from_inverse(H_inv, k, lo=-0.5, hi=0.5, tol=1e-6):
    """
    Given H_inv (i.e., inverse of H), find H(x) such that H_inv(H(x)) ≈ x.

    Args:
        H_inv: the inverse function H^{-1}
        x: the input to H(x)
        lo, hi: bounds on search interval for y = H(x)
        tol: precision tolerance

    Returns:
        Approximate value of H(x)
    """
    while hi - lo > tol:
        mid = (lo + hi) / 2
        if H_inv(mid) < k:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

def sample_triangle():
    r1 = random.uniform(-0.5, 0.5)  # Sample from [-1, 1]
    r2 = random.uniform(-0.5, 0.5)  # Sample from [-1, 1]
    return r1 + r2

def intcond(unknown, u, v):
    """
    Sample from the unknown distribution conditioned on the range [u, v].
    This function assumes that `unknown` is a callable that returns a sample
    from the unknown distribution.
    """
    u_low = compute_H_from_inverse(unknown.hat_cdf_inv, u)
    u_high = compute_H_from_inverse(unknown.hat_cdf_inv, v)
    if u_low > u_high:
        logger.error(f"Invalid range: u_low={u_low}, u_high={u_high} for u={u}, v={v}")
        return None  # Invalid range
    return unknown.sample(u_low, u_high)

def cintcond(unknown, u, v, delta_intcond, w):
    T = int((2 * w + 1) * math.log(1 / delta_intcond)) * 2
    
    for i in range(T):
        x = intcond(unknown, u, v)  # Sample from unknown | [u, v]
        r = sample_triangle()      # Sample from tri_w
        
        z = x + r
        if u <= z <= v:
            return z, i

    logger.error(f"Failed to sample in range [{u}, {v}] after {T} attempts.")
    return None, T  # ⊥ if rejection fails

def tpa(cunknown_tri, x, r, Thresh, delta_tpa, w):

    k = 0
    beta_c = 0.5
    scaling = 1
    _ncalls = 0

    for i in range(r//scaling):
        lam = 0
        beta = math.inf  # Initialize beta to maximum range

        while beta > beta_c:
            lam += 1
            u = max(0, x - beta)
            v = min(math.inf, x + beta)

            sample, _calls = cintcond(cunknown_tri, u, v, delta_tpa / (r * Thresh), w)
            _ncalls += _calls

            if sample is None or lam >= Thresh:
                logger.error(f"TPA iteration {lam} failed: sample={sample}, beta={beta}")
                return None, _ncalls

            beta = abs(sample - x)

        k += (lam - 1)

    return k / r * scaling, _ncalls

def Est(unknown, x, zeta, delta_Est, B, w):
    
    r1 = int(2 *  math.log(8 / delta_Est)) + 1
    log_term = math.log((2 * r1) / delta_Est)    
    Thresh = B + log_term + math.sqrt(log_term ** 2 + 2 * B * log_term)

    lambda_, _ncalls1 = tpa(unknown, x, r1, Thresh, delta_Est / 4, w)
    if lambda_ is None:
        logger.error("r1: TPA failed to return a valid lambda.")
        return None, _ncalls1
    
    logz = math.log(1 + zeta)
    r2 = int(
        2 * (lambda_ + math.sqrt(lambda_) + 2 + logz)
        * (1 / (logz ** 2))
        * math.log(16 / delta_Est)
    ) + 1
    
    log_term = math.log((2 * r2) / delta_Est)   
    Thresh = B + log_term + math.sqrt(log_term ** 2 + 2 * B * log_term)
    lambda_, _ncalls2 = tpa(unknown, x, r2, Thresh, delta_Est / 4, w)
    if lambda_ is None:
        logger.error("r2: TPA failed to return a valid lambda.")
        return None, _ncalls1 + _ncalls2
    
    return math.exp(-lambda_), _ncalls1 + _ncalls2

def infident(unknown_sampler, known_sampler, eps, eta, delta, w):
    
    zeta = (eta - eps) / (eta - eps + 2)
    w_prime = ((1 + 2 * eps) / (1 - 2 * eps)) * w
    t = int((8 / ((eta - eps) ** 2)) * np.log(4 / delta))
    logger.info(f"Number of samples (t): {t}")

    samples = [unknown_sampler.sample() for _ in range(t)]
    pest_values = []
    _ncalls = 0

    for i in range(t):
        logger.info(f"Doing Sample {i}: {samples[i]}")
        x_i = samples[i]
        known_prob = known_sampler.pmf(x_i)
        if known_prob == 0:
            logger.error(f"Sample {i}: known_prob is 0 for x_i = {x_i}. Something is off! Rejecting the Sampler.")
            return "reject", _ncalls

        B = math.log((1 + 2 * eps) / known_prob)
        
        pest, _calls = Est(unknown_sampler, x_i, zeta, delta / (4 * t), B, w_prime)
        _ncalls += _calls

        logger.info(f"Sample {i}: x_i = {x_i}, known_prob = {known_prob}, Estimated Mass = {pest}")
        
        if pest is None:
            return "reject", _ncalls
        
        pest_values.append((x_i, pest))

    dest = sum(max(0, 1 - known_sampler.pmf(x_i) / pest) for x_i, pest in pest_values) / t

    logger.info(f"Estimated TV distance: {dest}")

    if dest > (eta + eps) / 2:
        return "reject", _ncalls
    else:
        return "accept", _ncalls


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Infident algorithm with a specified distribution.")
    parser.add_argument("distribution", choices=["binomial", "poisson", "geometric"], help="Type of distribution to use.")
    parser.add_argument("--params", nargs="+", type=str, required=True, help="Parameters for the chosen distribution.")
    parser.add_argument("--eps", type=float, default=0.01, help="Epsilon value for Infident.")
    parser.add_argument("--eta", type=float, default=0.5, help="Eta value for Infident.")
    parser.add_argument("--delta", type=float, default=0.05, help="Delta value for Infident.")
    args = parser.parse_args()

    distribution = args.distribution
    params = args.params
    eps = args.eps
    eta = args.eta
    delta = args.delta

    file_handler = logging.FileHandler(f"{distribution}_{'_'.join(str(p) for p in params)}.log")
    logger.addHandler(file_handler)

    if distribution == "binomial":
        if len(params) != 4:
            raise ValueError("Binomial distribution requires 4 parameters: n_unknown, p_unknown, n_known, p_known.")
        n_unk, p_unk, n_kn, p_kn = params
        n_unk, p_unk, n_kn, p_kn = int(n_unk), float(p_unk), int(n_kn), float(p_kn)
        w = n_kn * (1 - p_kn) / p_kn
        unknown_sampler = BinomialDistribution(int(n_unk), p_unk)
        known_sampler = BinomialDistribution(int(n_kn), p_kn)
    elif distribution == "poisson":
        if len(params) != 2:
            raise ValueError("Poisson distribution requires 2 parameters: lambda_unknown, lambda_known.")
        lambd_unk, lambd_kn = params
        lambd_unk, lambd_kn = float(lambd_unk), float(lambd_kn)
        w = lambd_kn
        unknown_sampler = PoissonDistribution(lambd_unk)
        known_sampler = PoissonDistribution(lambd_kn)
    elif distribution == "geometric":
        if len(params) != 1:
            raise ValueError("Geometric distribution requires 2 parameters: p_unknown, p_known.")
        p_unknown, p_known = params
        p_unknown, p_known = float(p_unknown), float(p_known)
        w = 1 / (1 - p_known)
        unknown_sampler = GeometricDistribution(p_unknown)
        known_sampler = GeometricDistribution(p_known)
    else:
        raise ValueError("Unsupported distribution type.")

    logger.info("Running Infident with the following parameters:")
    logger.info(f"Distribution: {distribution}")
    logger.info(f"Parameters: {params}")
    logger.info(f"eps: {eps}, eta: {eta}, delta: {delta}, w: {w}")

    result, _ncalls = infident(unknown_sampler, known_sampler, eps, eta, delta, w)
    logger.info(f"Decision: {result}, Number of calls: {_ncalls}")

#514740
#28545592