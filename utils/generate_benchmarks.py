import numpy as np
from math import log10 as _log10

def generate_binomial_benchmarks(output_file, n_samples=100, n_min=1000, n_max=600000, p_min=0.01, p_max=0.5):
    """
    Generate benchmarks for binomial parameters with significant differences between n_unk/p_unk and n_kn/p_kn.

    Args:
        output_file (str): Path to the output file to save benchmarks.
        n_samples (int): Number of benchmarks to generate.
        n_min (int): Minimum value for n_unk.
        n_max (int): Maximum value for n_unk.
        p_min (float): Minimum value for p_unk.
        p_max (float): Maximum value for p_unk.
    """
    n_unk_values = np.linspace(n_min, n_max, n_samples, dtype=int)
    p_unk_values = np.linspace(p_min, p_max, n_samples)

    with open(output_file, "w") as f:
        f.write("n_unk,p_unk,n_kn,p_kn\n")
        
        # far benchmarks
        for n_unk, p_unk in zip(n_unk_values, p_unk_values):
            # Generate significantly different n_kn and p_kn
            n_kn = n_unk + np.random.randint(-n_unk // 5, n_unk // 5)  # Vary n_kn by up to ±20% of n_unk
            p_kn = p_unk + np.random.uniform(-0.2, 0.2)  # Vary p_kn by up to ±0.2
            p_kn = max(0.01, min(0.99, p_kn))  # Ensure p_kn stays within [0.01, 0.99]
            f.write(f"{n_unk},{p_unk:.4f},{n_kn},{p_kn:.4f}\n")
        
        # Close benchmarks
        for n_unk, p_unk in zip(n_unk_values, p_unk_values):
            # Generate significantly different n_kn and p_kn
            n_kn = n_unk # no change here
            getlog = _log10(n_unk) # amount of change in p depending on n_unk
            p_kn = p_unk + np.random.uniform(- 2 * 10 ** (-getlog + 2), 2 * 10 ** (-getlog + 2))  # Vary p_kn by up to ±0.02
            p_kn = max(0.01, min(0.99, p_kn))  # Ensure p_kn stays within [0.01, 0.99]
            f.write(f"{n_unk},{p_unk:.4f},{n_kn},{p_kn:.4f}\n")


def generate_binomial_benchmarks_for_bugs(output_file, n_samples=100, n_min=1000, n_max=600000, p_min=0.01, p_max=0.5):
    """
    Generate benchmarks for binomial parameters with significant differences between n_unk/p_unk and n_kn/p_kn.

    Args:
        output_file (str): Path to the output file to save benchmarks.
        n_samples (int): Number of benchmarks to generate.
        n_min (int): Minimum value for n_unk.
        n_max (int): Maximum value for n_unk.
        p_min (float): Minimum value for p_unk.
        p_max (float): Maximum value for p_unk.
    """
    n_unk_values = np.linspace(n_min, n_max, n_samples, dtype=int)
    p_unk_values = np.linspace(p_min, p_max, n_samples)

    with open(output_file, "w") as f:
        f.write("n_unk,p_unk,n_kn,p_kn\n")
        
        for n_unk, p_unk in zip(n_unk_values, p_unk_values):
            # Generate significantly different n_kn and p_kn
            n_kn = n_unk  # n_kn = n_unk
            p_kn = p_unk # p_kn = p_unk
            p_kn = max(0.01, min(0.99, p_kn))  # Ensure p_kn stays within [0.01, 0.99]
            f.write(f"{n_unk},{p_unk:.4f},{n_kn},{p_kn:.4f}\n")
        

def generate_poisson_benchmarks_for_bugs(output_file, n_samples=100, mu_min=1000, mu_max=600000):
    """
    Generate benchmarks for Poisson parameters.

    Args:
        output_file (str): Path to the output file to save benchmarks.
        n_samples (int): Number of benchmarks to generate.
        mu_min (int): Minimum value for mu_unk.
        mu_max (int): Maximum value for mu_unk.
    """
    mu_unk_values = np.linspace(mu_min, mu_max, n_samples, dtype=int)
    
    with open(output_file, "w") as f:
        f.write("mu_unk,mu_kn\n")
        
        for mu_unk in mu_unk_values:
            # Generate significantly different mu_kn 
            mu_kn = mu_unk  # n_kn = n_unk
            f.write(f"{mu_unk},{mu_kn}\n")


if __name__ == "__main__":

    '''Benchmarks for performance experiments with binomial distributions'''
    output_file = "/Users/uddalok/Documents/PHD/projects/intCondTester/benchmarks/binomial_benchmarks.csv"
    generate_binomial_benchmarks(output_file, n_samples=100, n_min=100, n_max=60000, p_min=0.01, p_max=0.5)
    print(f"Benchmarks saved to {output_file}")
    
    '''Benchmarks for bugs in binomial distributions'''
    # output_file = "./benchmarks/binomial_benchmarks_cstudy.csv"
    # generate_binomial_benchmarks_for_bugs(output_file, n_samples=50, n_min=1000, n_max=100000, p_min=0.01, p_max=0.5)
    # print(f"Benchmarks saved to {output_file}")
    
    '''Benchmarks for bugs in poisson distributions'''
    # output_file = "./benchmarks/poisson_benchmarks_cstudy.csv"
    # generate_poisson_benchmarks_for_bugs(output_file, n_samples=50, mu_min=1000, mu_max=100000)
    # print(f"Benchmarks saved to {output_file}")
    