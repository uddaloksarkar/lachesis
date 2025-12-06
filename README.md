# Artifact README

## 🌟 Introduction

This artifact provides a prototype implementation of the proposed tool, **Lachesis**, a sampler tester that certifies the correctness of a black-box sampler with rigorous statistical guarantees. Lachesis operates in two modes: `'toltest'` and `'ERtoltest'`. This artifact demonstrates how to use Lachesis and reproduce the experimental results presented in the paper, including **Figure 3** and **Table 1**.

## ⚙️ Artifact Requirements

Running the full benchmark suite may take several hours on a standard laptop with 1 core and 4 GB RAM. If you are unable to run the experiments yourself, we provide all raw data and logs under the `logs/` directory. These logs can be used to regenerate plots and tables using `results.ipynb`.

## 📁 Directory Structure

```
/artifact/
├── tester.py                   # Main script: Lachesis tool
├── baseline.py                 # Baseline tool: CubeProbe
├── samplers/                   # Samplers under test (e.g., binomial, poisson)
├── results.ipynb               # Jupyter Notebook to generate plots/tables
├── run_cstudy_binomial.sh      #run case study on Binomial
├── run_cstudy_poisson.sh       #run case study on Poisson
├── run_performance.sh          #run performance evaluation on benchmarks
├── benchmarks/                 # Benchmark inputs used in evaluation
└── logs/                       # Collected logs of all runs
```


## 📊 Experimental Reproduction

### Setup

Ensure you have Python 3.9+ installed. To install the required packages, run:

```bash
pip install -r requirements.txt
```

### Running Lachesis

To run Lachesis on a single instance:

```bash
python tester.py binomial --params 100 0.1 101 0.2 --eps 0.01 --eta 0.5 --delta 0.1 --seed 66 --er
```
- The first argument is the name of the sampler under test. Available samplers include `binomial`, `poisson`, `binomial_spoofed_i`, etc. (see the `samplers/` directory).
- `--params` supplies parameters to the sampler (these vary depending on the sampler type).
- `--eps` sets the tolerance threshold.
- `--delta` sets the confidence level.
- `--eta` controls sample complexity.
- `--er` enables the enhanced mode `ERtoltest`. If omitted, Lachesis runs in standard `toltest` mode.

(Refer to the paper for a detailed explanation of these parameters.)

### Running Lachesis on Two Instances

Below are step-by-step commands to run **Lachesis** on `binomial` and `poisson` samplers with varying parameters.

#### ✅ Case 1: Binomial sampler vs. Binomial(1002, 0.2)

- **Tested Sampler:** `binomial(1000, 0.1)`
- **Reference Distribution:** `binomial(1002, 0.2)`
- **Command:**
```bash
python tester.py binomial --params 1000 0.1 1002 0.2 --eps 0.01 --eta 0.5 --delta 0.1 --seed 66 --er
```
- **Expected output:**
```
... ...
... INFO - Decision: reject, Number of calls: 655437
```

#### ✅ Case 2: Binomial sampler vs. Binomial(1001, 0.1)

- **Tested Sampler:** `binomial(1000, 0.1)`
- **Reference Distribution:** `binomial(1001, 0.1)`
- **Command:**
```bash
python tester.py binomial --params 1000 0.1 1001 0.1 --eps 0.01 --eta 0.5 --delta 0.1 --seed 66 --er
```
- **Expected output:**
```
... ...
... INFO - Decision: accept, Number of calls: 655437
```

#### ✅ Case: Poisson sampler vs. Poisson(3002)

- **Tested Sampler:** `poisson(3000)`
- **Reference Distribution:** `poisson(3002)`
- **Command:**
```bash
python tester.py poisson --params 3000 3002 --eps 0.01 --eta 0.5 --delta 0.1 --seed 66 --er
```
- **Expected output:**
```
... ...
... Decision: accept, Number of calls: 867842
```


## 🧩 Reproducing the Experiments

### Resource Requirements

- RAM: 4 GB  
- CPU: 1 core @ 2.60 GHz  

### Estimated Runtime

~8 hours for the complete benchmark suite.

### Full Benchmark Evaluation

To run performance experiment on Lachesis and CubeProbe across the entire benchmark:

```bash
./run_performance.sh
```

Results will be stored in the `out-perf/` directory.

To run case study on Binomial use:

```bash
./run_cstudy_binomial.sh
```

Results will be stored in the `out-csbinomial/` directory.

To run case study on Poisson use:

```bash
./run_cstudy_poisson.sh
```

Results will be stored in the `out-cspoisson/` directory.


## 🧬 Figure Generation Using Provided Logs

If you cannot run the full experiments due to limited resources, you can still reproduce all plots using pre-generated logs in the `logs/` directory.

Open the Jupyter notebook:

``` bash
jupyter notebook results.ipynb
```
This notebook regenerates **Figure 3** and **Table 1** using the saved logs.
