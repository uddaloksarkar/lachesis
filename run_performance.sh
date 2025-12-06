#!/bin/bash

filespos="benchmarks/binomial_benchmarks.csv"

mkdir -p out-perf/baseline
mkdir -p out-perf/tester

ulimit -t unlimited
shopt -s nullglob

EPS=0.01
ETA=0.5
DELTA=0.05
SEED="66"
tlimit="5000"

# Array of solvers/options
opts_arr=(
  "python baseline.py binomial --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
  "python tester.py binomial --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
)

# Loop over each configuration
for opts in "${opts_arr[@]}"; do
    # Determine which output subfolder to use
    if [[ "$opts" == *"baseline.py"* ]]; then
        outdir="out-perf/baseline"
    else
        outdir="out-perf/tester"
    fi

    # Safe tag for file names
    opt_tag=$(echo "$opts" | tr -s ' ' '_' | tr '/' '_')

    tail -n +2 "$filespos" | while IFS=',' read -r n1 p1 n2 p2; do
        filename="${n1}_${p1}_${n2}_${p2}"
        params="${n1} ${p1} ${n2} ${p2}"
        baseout="${outdir}/${filename}"
        
        echo "Running: $filename"
        ${opts} --params ${params} > "${baseout}.out" 2>&1
    done
done
