#!/bin/bash
DB="../results/experiment_results.db";
netFolder="../../data";

function transfer(){
    mv n_vs_time.pdf ../../revised_version.d/figures/
    mv theta_vs_time.pdf ../../revised_version.d/figures/
}

function collect_results(){
cat log* | grep INSERT > to_db.sqlite
}

function timing(){
rm -f run.sh
count=0
for n in 250 750
do
    for p in 0.1 0.2 0.3
    do
        for i in 0.1 0.5 0.9
        do
            for k in `seq 0 9`
            do
                echo n=$n p=$p i=$i k=$k
cmd=$(cat << EOF
python ../scripts/timing_greedy.py -n $n -p $p -i $i -k $k
EOF
)
((count+=1))
echo "echo $count; sbatch -n 1 -o log.$n.$p.$i.$k -n 1 --export=command=\"$cmd\" ../scripts/run_proc.sbatch; qreg 1000;" >> run.sh
            done
        done
    done
done
}

function table(){
sqlite3 ../results/results.db << EOF
CREATE TABLE "greedy_timing" (
    nodes INT,
    probability FLOAT,
    interval FLOAT,
    instance INT,
    queries INT,
    gsqrd_time FLOAT,
    greedy_time FLOAT,
    PRIMARY KEY(nodes,probability,interval,instance));
EOF
}

function gsqrd(){
for file in `ls -1 ../../data/colorings/*node.coloring`
do
   logFile="gsqrd_"`basename $file`.log;
   if [ -a $logFile ]; then
      continue
   fi
   echo "qsub $qsubScript -v command=\"python ../scripts/gsquared_query_set.py $file\",Log=\"$logFile\" -N "$logFile";"
   echo "qreg.bash"
done
}

function compaction(){
#for file in `ls -1 gsqrd_comp_*.que`
for file in `ls -1 comp_*.que`
do
   # check if compaction done
   prefix=`echo $file | sed -e 's/.que$//'`;
   compqueFile=${prefix}.compque;
   if [ -a $compqueFile ]; then
      >&2 echo "$prefix: Compaction done. Do update_db.sh. Skipping ...";
      continue;
   fi
   config=${prefix}.cfg;
   logFile=${prefix}.log;

   echo "qsub $qsubScript -v command=\"python /home/abhijin/query-compaction/version-01/driver-01.py $config\",Log=\"$logFile\";"
   echo "qreg.bash"
done
}

function checkStatus(){
   network=`basename $file | sed -e 's/.uel//'`;
   query=$(
cat << EOF
SELECT network FROM greedy WHERE 
network='$network' AND experiment LIKE '${key}_${interval}_%';
EOF
)
   checkIfDone=`sqlite3 $DB "$query" | wc -l`;
}


function randomized(){
cat << EOF > networksList.dat
K1000
## slashdot0811.uel
## slashdot0902.uel
## enron.giant.uel
## epinion.uel
## random.regular.n.80000.k.10.i.1.uel
## random.regular.n.80000.k.10.i.2.uel
## random.regular.n.80000.k.10.i.3.uel
## random.regular.n.80000.k.12.i.1.uel
## random.regular.n.80000.k.12.i.2.uel
## random.regular.n.80000.k.12.i.3.uel
EOF

for file in `cat networksList.dat | awk '/^#/{next}{print $1}'`
do
   widthList=$(
cat << EOF
10
EOF
)
   for width in $widthList
   do
      # checkStatus
      # checkIfDone=0
      # if [ $checkIfDone != 0 ]; then
      #    >&2 echo "skipping $file ..."
      #    continue;
      # fi

      logFile="randomized_"`basename $file`_"$width".log;
      echo "qsub $qsubScript -v command=\"python ../scripts/random_query_set.py $netFolder/$file $width\",Log=\"$logFile\";"
      echo "qreg.bash"
   done
done
}

function interval_random_threshold(){
cat << EOF > networksList.dat
#slashdot0811.uel
#slashdot0902.uel
#enron.giant.uel
#epinion.uel
#random.regular.n.80000.k.10.i.1.uel
#random.regular.n.80000.k.10.i.2.uel
#random.regular.n.80000.k.10.i.3.uel
er.n.80000.p.0.000125.i.1.uel
#er.n.80000.p.0.000125.i.2.uel
#er.n.80000.p.0.000125.i.3.uel
#er.n.80000.p.0.000150.i.1.uel
#er.n.80000.p.0.000150.i.2.uel
#er.n.80000.p.0.000150.i.3.uel
#random.regular.n.80000.k.10.i.10.uel
#random.regular.n.80000.k.10.i.4.uel
#random.regular.n.80000.k.10.i.5.uel
#random.regular.n.80000.k.10.i.6.uel
#random.regular.n.80000.k.10.i.7.uel
#random.regular.n.80000.k.10.i.8.uel
#random.regular.n.80000.k.10.i.9.uel
#random.regular.n.80000.k.12.i.10.uel
#random.regular.n.80000.k.12.i.1.uel
#random.regular.n.80000.k.12.i.2.uel
#random.regular.n.80000.k.12.i.3.uel
#random.regular.n.80000.k.12.i.4.uel
#random.regular.n.80000.k.12.i.5.uel
#random.regular.n.80000.k.12.i.6.uel
#random.regular.n.80000.k.12.i.7.uel
#random.regular.n.80000.k.12.i.8.uel
#random.regular.n.80000.k.12.i.9.uel
EOF

for file in `cat networksList.dat | awk '/^#/{next}{print $1}'`
do
   key="interval_random_threshold";
   #for interval in `seq 0 0.2 1 | awk '{printf("%.1f\n",$1)}'`
   for interval in `seq 0 0 | awk '{printf("%.1f\n",$1)}'`
   do
      checkStatus
      checkIfDone=0
      if [ $checkIfDone != 0 ]; then
         >&2 echo "skipping $file ..."
         continue;
      fi
      logFile="log_interval_random_threshold_"`basename $file`_"$interval";
      echo "qsub $qsubScript -v command=\"python ../scripts/interval_random_threshold.py $netFolder/$file $interval\",Log=\"$logFile\";"
      echo "qreg.bash"
   done
done
}

eval $1

###########################################################################

exit

for file in `ls -1 ../../data/random_regular_1000_*uel ../../data/K1000.uel`
do
   key="fixed_threshold";
   checkStatus
   if [ $checkIfDone != 0 ]; then
      >&2 echo "skipping $file ..."
      continue;
   fi
   logFile="log_fixed_threshold_"`basename $file`
   echo "qsub $qsubScript -v command=\"python ../scripts/fixed_threshold.py $file\",Log=\"$logFile\";"
   echo "qreg.bash"
done

#for file in `ls -1 ../../data/random_regular_1000_50_*uel ../../data/random_regular_1000_[2,4,7]00_*uel`
for file in `ls -1 ../../data/random_regular_1000_*uel ../../data/K1000.uel`
do
   key="random_threshold";
   checkStatus
   if [ $checkIfDone != 0 ]; then
      >&2 echo "skipping $file ..."
      continue;
   fi
   logFile="log_random_threshold_"`basename $file`
   echo "qsub $qsubScript -v command=\"python ../scripts/random_threshold.py $file\",Log=\"$logFile\";"
   echo "qreg.bash"
done

#K1000.uel
#karate.uel
#ca-astroph.giant.uel
#ca-condmat.giant.uel
#ca-grqc.giant.uel
#ca-hepph.giant.uel
#ca-hepth.giant.uel
#wiki-vote.uel
#cit-hepph.giant.uel
#p2p-gnutella04.uel
#facebook-02.uel
#random_regular_1000_10_1.uel
#random_regular_1000_50_1.uel
#random_regular_1000_100_1.uel
#random_regular_1000_200_1.uel
#random_regular_1000_250_1.uel
#slashdot0811.uel
#slashdot0902.uel
#enron.giant.uel
#epinion.uel
#random_regular_1000_10_10.uel
#random_regular_1000_10_2.uel
#random_regular_1000_10_3.uel
#random_regular_1000_10_4.uel
#random_regular_1000_10_5.uel
#random_regular_1000_10_6.uel
#random_regular_1000_10_7.uel
#random_regular_1000_10_8.uel
#random_regular_1000_10_9.uel
#random_regular_1000_50_10.uel
#random_regular_1000_50_2.uel
#random_regular_1000_50_3.uel
#random_regular_1000_50_4.uel
#random_regular_1000_50_5.uel
#random_regular_1000_50_6.uel
#random_regular_1000_50_7.uel
#random_regular_1000_50_8.uel
#random_regular_1000_50_9.uel
#random_regular_1000_100_10.uel
#random_regular_1000_100_2.uel
#random_regular_1000_100_3.uel
#random_regular_1000_100_4.uel
#random_regular_1000_100_5.uel
#random_regular_1000_100_6.uel
#random_regular_1000_100_7.uel
#random_regular_1000_100_8.uel
#random_regular_1000_100_9.uel
#random_regular_1000_200_10.uel
#random_regular_1000_200_2.uel
#random_regular_1000_200_3.uel
#random_regular_1000_200_4.uel
#random_regular_1000_200_5.uel
#random_regular_1000_200_6.uel
#random_regular_1000_200_7.uel
#random_regular_1000_200_8.uel
#random_regular_1000_200_9.uel
#random_regular_1000_250_10.uel
#random_regular_1000_250_2.uel
#random_regular_1000_250_3.uel
#random_regular_1000_250_4.uel
#random_regular_1000_250_5.uel
#random_regular_1000_250_6.uel
#random_regular_1000_250_7.uel
#random_regular_1000_250_8.uel
#random_regular_1000_250_9.uel
#random_regular_1000_400_10.uel
#random_regular_1000_400_1.uel
#random_regular_1000_400_2.uel
#random_regular_1000_400_3.uel
#random_regular_1000_400_4.uel
#random_regular_1000_400_5.uel
#random_regular_1000_400_6.uel
#random_regular_1000_400_7.uel
#random_regular_1000_400_8.uel
#random_regular_1000_400_9.uel
#random_regular_1000_500_10.uel
#random_regular_1000_500_1.uel
#random_regular_1000_500_2.uel
#random_regular_1000_500_3.uel
#random_regular_1000_500_4.uel
#random_regular_1000_500_5.uel
#random_regular_1000_500_6.uel
#random_regular_1000_500_7.uel
#random_regular_1000_500_8.uel
#random_regular_1000_500_9.uel
#random_regular_1000_700_10.uel
#random_regular_1000_700_1.uel
#random_regular_1000_700_2.uel
#random_regular_1000_700_3.uel
#random_regular_1000_700_4.uel
#random_regular_1000_700_5.uel
#random_regular_1000_700_6.uel
#random_regular_1000_700_7.uel
#random_regular_1000_700_8.uel
#random_regular_1000_700_9.uel
#random_regular_1000_800_10.uel
#random_regular_1000_800_1.uel
#random_regular_1000_800_2.uel
#random_regular_1000_800_3.uel
#random_regular_1000_800_4.uel
#random_regular_1000_800_5.uel
#random_regular_1000_800_6.uel
#random_regular_1000_800_7.uel
#random_regular_1000_800_8.uel
#random_regular_1000_800_9.uel
# dc.uel
# miami.uel
# seattle.epifast.uel
# seattle.uel
