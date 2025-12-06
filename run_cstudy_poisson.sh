#!/bin/bash

filespos="benchmarks/poisson_benchmarks_cstudy.csv"

mkdir -p out-cspoisson/tester

ulimit -t unlimited
shopt -s nullglob

EPS=0.01
ETA=0.5
DELTA=0.05
SEED="66"
tlimit="5000"

# cstudy benchmarks Poisson
opts_arr=(
"python tester.py poisson --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
"python tester.py poisson_spoofed_1 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
"python tester.py poisson_spoofed_2 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
"python tester.py poisson_spoofed_3 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
"python tester.py poisson_spoofed_4 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
"python tester.py poisson_spoofed_5 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
"python tester.py poisson_spoofed_6 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
)

# Loop over each configuration
for opts in "${opts_arr[@]}"; do
    outdir="out-cspoisson/tester"
    
    # Safe tag for file names
    opt_tag=$(echo "$opts" | tr -s ' ' '_' | tr '/' '_')

    tail -n +2 "$filespos" | while IFS=',' read -r l1 l2; do
        filename="${l1}_${l2}"
        params="${l1} ${l2}"
        baseout="${outdir}/${filename}"
        
        echo "Running: $filename"
        ${opts} --params ${params} > "${baseout}.out" 2>&1
    done
done
