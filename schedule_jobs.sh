#!/bin/bash

# Define the Python script paths
TESTER_SCRIPT="/Users/uddalok/Documents/PHD/projects/intCondTester/tester.py"
BASELINE_SCRIPT="/Users/uddalok/Documents/PHD/projects/intCondTester/baseline.py"
COMPUTE_TV_SCRIPT="/Users/uddalok/Documents/PHD/projects/intCondTester/utils/computeTV.py"

# Define the parameters for each sampler
BINOMIAL_PARAMS=(
    "10 0.3 10 0.7"
    "20 0.5 20 0.6"
)
POISSON_PARAMS=(
    "5 10"
    "15 20"
)
GEOMETRIC_PARAMS=(
    "0.3 0.5"
    "0.4 0.6"
)

# Define common arguments
EPS=0.01
ETA=0.5
DELTA=0.05

# Schedule jobs for Binomial sampler
for PARAMS in "${BINOMIAL_PARAMS[@]}"; do
    echo "Running Binomial sampler with params: $PARAMS"
    python "$TESTER_SCRIPT" binomial --params $PARAMS --eps $EPS --eta $ETA --delta $DELTA
    python "$BASELINE_SCRIPT" binomial --params $PARAMS --eps $EPS --eta $ETA --delta $DELTA
    python "$COMPUTE_TV_SCRIPT" binomial --params $PARAMS
done

# Schedule jobs for Poisson sampler
for PARAMS in "${POISSON_PARAMS[@]}"; do
    echo "Running Poisson sampler with params: $PARAMS"
    python "$TESTER_SCRIPT" poisson --params $PARAMS --eps $EPS --eta $ETA --delta $DELTA
    python "$BASELINE_SCRIPT" poisson --params $PARAMS --eps $EPS --eta $ETA --delta $DELTA
    python "$COMPUTE_TV_SCRIPT" poisson --params $PARAMS
done

# Schedule jobs for Geometric sampler
for PARAMS in "${GEOMETRIC_PARAMS[@]}"; do
    echo "Running Geometric sampler with params: $PARAMS"
    python "$TESTER_SCRIPT" geometric --params $PARAMS --eps $EPS --eta $ETA --delta $DELTA
    python "$BASELINE_SCRIPT" geometric --params $PARAMS --eps $EPS --eta $ETA --delta $DELTA
    python "$COMPUTE_TV_SCRIPT" geometric --params $PARAMS
done

echo "All jobs scheduled."
