import numpy as np
import math
import random
from samplers.binomial import BinomialDistribution
from samplers.poisson import PoissonDistribution
from samplers.geometric import GeometricDistribution

#sampler requirements

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
    r1 = random.uniform(-1, 1)  # Sample from [-1, 1]
    r2 = random.uniform(-1, 1)  # Sample from [-1, 1]
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
        print(f"Invalid range: u_low={u_low}, u_high={u_high} for u={u}, v={v}")
        return None  # Invalid range
    return unknown.sample(u_low, u_high)

def cintcond(unknown, u, v, delta_intcond, w):
    T = int((2 * w + 1) * math.log(1 / delta_intcond))
    
    for _ in range(T):
        x = intcond(unknown, u, v)  # Sample from unknown | [u, v]
        r = sample_triangle()      # Sample from tri_w
        
        z = x + r
        if u <= z <= v:
            return z

    print(f"Failed to sample in range [{u}, {v}] after {T} attempts.")
    return None  # ⊥ if rejection fails

def tpa(cunknown_tri, x, r, Thresh, delta_tpa, w):

    k = 0
    beta_c = 0.5
    scaling = 1

    for i in range(r//scaling):
        lam = 0
        beta = math.inf  # Initialize beta to maximum range

        # print(f"Starting TPA iteration {i} with x={x}, r={r}, Thresh={Thresh}, delta_tpa={delta_tpa}, w={w}")

        while beta > beta_c:
            lam += 1
            u = max(0, x - beta)
            v = min(math.inf, x + beta)

            # print(f"Iteration {lam}: u={u}, v={v}, beta={beta}")

            sample = cintcond(cunknown_tri, u, v, delta_tpa / (r * Thresh), w)

            if sample is None or lam >= Thresh:
                print(f"TPA iteration {lam} failed: sample={sample}, beta={beta}")
                return None

            beta = abs(sample - x)

        k += (lam - 1)

        # print(f"TPA iteration {lam} completed: k={k}, beta={beta}")

    return k / r * scaling

def Est(unknown, x, zeta, delta_Est, B, w):
    
    r1 = int(2 *  math.log(8 / delta_Est)) + 1
    log_term = math.log((2 * r1) / delta_Est)    
    Thresh = B + log_term + math.sqrt(log_term ** 2 + 2 * B * log_term)

    lambda_ = tpa(unknown, x, r1, Thresh, delta_Est / 4, w)
    if lambda_ is None:
        print("r1: TPA failed to return a valid lambda.")
        return None
    
    logz = math.log(1 + zeta)
    r2 = int(
        2 * (lambda_ + math.sqrt(lambda_) + 2 + logz)
        * (1 / (logz ** 2))
        * math.log(16 / delta_Est)
    ) + 1
    
    log_term = math.log((2 * r2) / delta_Est)   
    Thresh = B + log_term + math.sqrt(log_term ** 2 + 2 * B * log_term)
    lambda_ = tpa(unknown, x, r2, Thresh, delta_Est / 4, w)
    if lambda_ is None:
        print("r2: TPA failed to return a valid lambda.")
        return None
    
    return math.exp(-lambda_)

def infident(unknown_sampler, known_sampler, eps, eta, delta, w):
    
    zeta = (eta - eps) / (eta - eps + 2)
    w_prime = ((1 + 2 * eps) / (1 - 2 * eps)) * w
    t = int((8 / ((eta - eps) ** 2)) * np.log(4 / delta))
    t = 100 # For testing purposes, set t to a small value
    u_low = -1; u_high = 1
    
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
        
        pest = Est(unknown_sampler, x_i, zeta, delta / (4 * t), B, w_prime)

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

    # Example usage for testing

    # # Binomial
    # p_unk = 0.4
    # p_known = 0.4
    # n = 100
    # w = n * (1 - p_known) / p_known  # maximum ratio for Binomial
    # print("w:", w)
    # unknown_sampler = BinomialDistribution(n, p_unk)
    # known_sampler = BinomialDistribution(n, p_known)

    # Poisson
    # lambd_unk = 40
    # lambd_known = 40
    # w = lambd_known
    # print("w:", w)
    # unknown_sampler = PoissonDistribution(lambd_unk)
    # known_sampler = PoissonDistribution(lambd_known)

    # Geometric
    p_unk = 0.4
    p_known = 0.4
    w = 1 / (1- p_known)  # maximum ratio for Geometric
    print("w:", w)
    unknown_sampler = GeometricDistribution(p_unk)
    known_sampler = GeometricDistribution(p_known)


    # Run the Infident algorithm
    eps = 0.01
    eta = 0.5
    delta = 0.05
    result = infident(unknown_sampler, known_sampler, eps, eta, delta, w)
    print("Result:", result)
