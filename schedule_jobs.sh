#!/bin/bash

source=~/.venvs/udda/bin/activate

# filespos="benchmarks/binomial_benchmarks_cstudy.csv"
filespos="benchmarks/poisson_benchmarks_cstudy.csv"
# filespos="benchmarks/binomial_benchmarks.csv"

ulimit -t unlimited
shopt -s nullglob
rm -f todo
touch todo
solver="tester"

EPS=0.01
ETA=0.5
DELTA=0.05
SEED="66"
tlimit="5000"

# # cstudy benchmarks Binomial
# opts_arr=(
# "python tester.py binomial --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
# "python tester.py binomial_spoofed_1 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
# "python tester.py binomial_spoofed_2 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
# "python tester.py binomial_spoofed_3 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
# "python tester.py binomial_spoofed_4 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
# "python tester.py binomial_spoofed_5 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
# "python tester.py binomial_spoofed_6 --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
# )

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

# # performance baseline
# opts_arr=(
# "python baseline.py binomial --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
# "python tester.py binomial --eps ${EPS} --eta ${ETA} --delta ${DELTA} --seed ${SEED}"
# )

output="out"
#5GB mem limit
memlimit="5000000"
numthreads=$((OMPI_COMM_WORLD_SIZE))

################
# testing
################
#output="out-test"
#tlimit="20"
#filespos="dnf_test"
################


SERVER=$SLURM_SUBMIT_HOST
WORKDIR="$SCRATCH/scratch/${SLURM_JOB_ID}_${OMPI_COMM_WORLD_RANK}"
output="${output}-${SLURM_JOB_ID}"

# echo ------------------------------------------------------
# echo "Job is running on node ${PBS_NODEFILE}"
# echo ------------------------------------------------------
# echo "Rank is: ${OMPI_COMM_WORLD_RANK}"
# echo "PBS: qsub is running on $PBS_O_HOST"
# echo "PBS: originating queue is $PBS_O_QUEUE"
# echo "PBS: executing queue is $PBS_QUEUE"
# echo "PBS: working directory is $SLURM_SUBMIT_DIR"
# echo "PBS: execution mode is $PBS_ENVIRONMENT"
# echo "PBS: job identifier is ${PBS_JOBID}"
# echo "PBS: job name is $PBS_JOBNAME"
# echo "PBS: node file is $PBS_NODEFILE"
# echo "PBS: current home directory is $PBS_O_HOME"
# echo "PBS: PATH = $PBS_O_PATH"
# echo "server      is ${SERVER}"
# echo "workdir     is ${WORKDIR}"
# echo "permdir     is ${PERMDIR}"
# echo "servpermdir is ${SERVPERMDIR}"
# echo "Output dir  is ${output}"

mkdir -p "${WORKDIR}"
cd "${WORKDIR}" || exit

allbench=$(tail -n +2 "${SLURM_SUBMIT_DIR}/${filespos}" | shuf --random-source="${SLURM_SUBMIT_DIR}/myrnd")
outputdir="${SLURM_SUBMIT_DIR}/${solver}-main"
echo outputdir is ${outputdir}
cp -r ${outputdir}/tester.py .
cp -r ${outputdir}/timeout .
cp -r ${outputdir}/baseline.py .
cp -r ${outputdir}/samplers .
cp -r ${outputdir}/binomial_benchmarks.csv .

# create todo
rm -f todo
mkdir -p ${output}
numlines=0
at_opt=0
for opts in "${opts_arr[@]}"
do
    for bench in $allbench
    do
        mkdir -p "${output}-${at_opt}" || exit
        filename=$(echo "$bench" | tr ',' '_')
        params=$(echo "$bench" | tr ',' ' ')
    
        # run
        baseout="${output}-${at_opt}/${filename}"
        mytimeout="./timeout -k 2 -s SIGINT ${tlimit} "
        echo "/usr/bin/time --verbose -o ${baseout}.timeout ${mytimeout} ${opts} --seed $SEED --params ${params} > ${baseout}.out 2>&1" >> todo
    
        echo "mkdir -p  ${outputdir}/${output}-${at_opt}" >> todo
        echo "xz ${baseout}.out*" >> todo
        echo "xz ${baseout}.timeout*" >> todo
        echo "xz ${baseout}.log*" >> todo
        echo "rm -f core.*" >> todo

        echo "mv ${baseout}.out*      ${outputdir}/${output}-${at_opt}/" >> todo
        echo "mv ${baseout}.timeout*  ${outputdir}/${output}-${at_opt}/" >> todo
        echo "mv ${baseout}.log*      ${outputdir}/${output}-${at_opt}/" >> todo
        echo "mv core.* ${outputdir}/${output}/" >> todo

        # delete what's left
        echo "rm -f ${baseout}.timeout*" >> todo
        echo "rm -f ${baseout}.out*" >> todo
        echo "rm -f ${baseout}.log*" >> todo

        # todos: 1+5+4+3 = 13

        numlines=$((numlines+1))
    done
    at_opt=$((at_opt+1))
done
todomylines=13

# create per-core todos
numper=$((numlines/numthreads))
remain=$((numlines-numper*numthreads))
if [[ $remain -ge 1 ]]; then
    numper=$((numper+1))
fi
remain=$((numlines-numper*(numthreads-1)))

mystart=0
for ((myi=0; myi < numthreads ; myi++))
do
    rm -f todo_$myi.sh
    touch todo_$myi.sh
    echo "#!/bin/bash" > todo_$myi.sh
    echo "ulimit -v $memlimit" >> todo_$myi.sh
    echo "ulimit -c 0" >> todo_$myi.sh
    echo "set -x" >> todo_$myi.sh
    typeset -i myi
    typeset -i numper
    typeset -i mystart
    mystart=$((mystart + numper))
    if [[ $myi -lt $((numthreads-1)) ]]; then
        if [[ $mystart -gt $((numlines+numper)) ]]; then
            # echo "No need, over the limit by more than numper"
            sleep 0
        else
            if [[ $mystart -lt $numlines ]]; then
                myp=$((numper*todomylines))
                mys=$((mystart*todomylines))
                head -n $mys todo | tail -n $myp >> todo_$myi.sh
            else
                #we are at boundary, e.g. numlines is 100, numper is 3, mystart is 102
                #we must only print the last numper-(mystart-numlines) = 3-2 = 1
                mys=$((mystart*todomylines))
                p=$(( numper-mystart+numlines ))
                if [[ $p -gt 0 ]]; then
                    myp=$((p*todomylines))
                    head -n $mys todo | tail -n $myp >> todo_$myi.sh
                fi
            fi
        fi
    else
        if [[ $remain -gt 0 ]]; then
            mys=$((mystart*todomylines))
            mr=$((remain*todomylines))
            head -n $mys todo | tail -n $mr >> todo_$myi.sh
        fi
    fi
    echo "exit 0" >> todo_$myi.sh
    chmod +x todo_$myi.sh
done
# echo "Done."

# Execute todos
echo "This is MPI exec number $OMPI_COMM_WORLD_RANK"
rm -f ${output}/out_${OMPI_COMM_WORLD_RANK}
./todo_${OMPI_COMM_WORLD_RANK}.sh > ${output}/out_${OMPI_COMM_WORLD_RANK}
echo "Finished waiting rank $OMPI_COMM_WORLD_RANK"


rm -f dnfstream
rm -f DNFKLM
rm -f DNFDKL
rm -f DNFCUSP
rm -f timeout
exit 0