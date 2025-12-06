#!/bin/bash

filespos="benchmarks/binomial_benchmarks_cstudy.csv"

mkdir -p out-csbinomial/tester

ulimit -t unlimited
shopt -s nullglob

EPS=0.01
ETA=0.5
DELTA=0.05
SEED="66"
tlimit="5000"

# cstudy benchmarks Binomial
opts_arr=(
"python tester.py binomial --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
"python tester.py binomial_spoofed_1 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
"python tester.py binomial_spoofed_2 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
"python tester.py binomial_spoofed_3 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
"python tester.py binomial_spoofed_4 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
"python tester.py binomial_spoofed_5 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
"python tester.py binomial_spoofed_6 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
)

# Loop over each configuration
for opts in "${opts_arr[@]}"; do
    outdir="out-csbinomial/tester"
    
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
