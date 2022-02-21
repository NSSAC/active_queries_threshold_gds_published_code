#!/bin/bash
function gsqrd(){
   echo "===================="
   echo "gsqrd"
   echo "===================="
   for cfgFile in `ls -1 gsqrd_comp_*.cfg`
   do
      echo "Processing $cfgFile ...";
      # check if compaction done
      prefix=`echo $cfgFile | sed -e 's/.cfg$//'`;
      queFile=${prefix}.que;
      compqueFile=${prefix}.compque;
      logFile=${prefix}.log;

      # check if compaction done
      if ! [ -a $compqueFile ]; then
         echo "Compaction not done yet. Skipping ...";
         continue;
      fi

      network=`echo $prefix | sed -e "s/gsqrd_comp_//"`;
      queries=`wc -l $queFile | awk '{print $1}'`;
   
      # check if good termination
      checkIfClean=`grep "good termination" $logFile | wc -l`
      if [ $checkIfClean == 1 ]; then
         echo "Compaction successful. Files moved to logs.";
         queriesAfterCompaction=`head -q -n-1 $compqueFile | wc -l`;
         mv ${prefix}* ../results/logs/;
      else
         echo "Compaction did not go through. Config files will be retained in the current folder. que files will be removed.";
         queriesAfterCompaction=-1;
      fi
         
      queryDB=$(
cat << EOF
INSERT OR REPLACE INTO gsqrd 
(network,number_of_queries,number_of_queries_after_compaction)
VALUES ('$network',$queries,$queriesAfterCompaction);
EOF
)
      sqlite3 ../results/experiment_results.db "$queryDB";
   done
}

function randomized(){
   echo "===================="
   echo "randomized"
   echo "===================="
   for cfgFile in `ls -1 comp_*.cfg`
   do
      echo "Processing $cfgFile ...";
      # check if compaction done
      prefix=`echo $cfgFile | sed -e 's/.cfg$//'`;
      queFile=${prefix}.que;
      compqueFile=${prefix}.compque;
      logFile=${prefix}.log;

      # check if compaction done
      if ! [ -a $compqueFile ]; then
         echo "Compaction not done yet. Skipping ...";
         continue;
      fi

      itr=`echo $cfgFile | sed -e 's/.*_//' -e 's/.cfg//'`;
      width=`echo $cfgFile | sed -e "s/_${itr}.cfg//" -e 's/.*_//'`;
      network=`echo $cfgFile | sed -e "s/comp_//" -e "s/_${width}_${itr}.cfg//"`;
      queries=`wc -l $queFile | awk '{print $1}'`;
   
      # check if good termination
      checkIfClean=`grep "good termination" $logFile | wc -l`
      if [ $checkIfClean == 1 ]; then
         echo "Compaction successful. Files moved to logs.";
         queriesAfterCompaction=`head -q -n-1 $compqueFile | wc -l`;
         mv ${prefix}* ../results/logs/;
      else
         echo "Compaction did not go through. Files will be retained in the current folder.";
         rm ${prefix}*log ${prefix}*compque;
         queriesAfterCompaction=-1;
      fi
         
      queryDB=$(
cat << EOF
INSERT OR REPLACE INTO randomized 
(network,width,iteration,number_of_queries,number_of_queries_after_compaction)
VALUES ('$network',$width,$itr,$queries,$queriesAfterCompaction);
EOF
)
      sqlite3 ../results/experiment_results.db "$queryDB";
   done
}

gsqrd
randomized
exit

fileList=`ls -1 log_interval_random_threshold_* log_randomized_*`;
for file in $fileList
do
   checkIfClean=`grep -v "^INSERT" $file | wc -l`;
   if [ $checkIfClean != 0 ]; then
      >&2 echo "ERROR: skipping $file ..."
      mv $file ../results/error/
      continue;
   fi
   echo "Processing $file ...";
   sqlite3 ../results/experiment_results.db < $file;
   mv $file ../results/logs/;
done
