#!/bin/bash
DB="../results/experiment_results.db";
#DOCS="../../full_report.d/figures/";
DOCS="../../aaai_2018.d/figures/";

cat << EOF > networksList.dat
#karate
ca-astroph.giant
ca-condmat.giant
ca-grqc.giant
ca-hepph.giant
ca-hepth.giant
wiki-vote
facebook-02
cit-hepph.giant
enron.giant
p2p-gnutella04
#dc
#epinion
#go.haswell.convert.graphs.qsub
#miami
#run.convert.epifast.to.standard
#seattle.epifast
#seattle
#slashdot0811
#slashdot0902
EOF

function progressAdaptive(){
   # interval random threshold for real-world graphs: varying intervals
   rm -f progress_*dat;
   fileList=""
   for net in `cat networksList.dat | awk '/^#/{next}{print $1}'`
   do
      datFile=progress_${net}.dat;
      fileList="$fileList $datFile";
      echo "$net" | sed -e 's/.giant$//' > $datFile;
      sqlite3 $DB <<! >> $datFile
.separator ","
SELECT (query_number+.0)/(SELECT
max(query_number) FROM interval_threshold_stats
WHERE network LIKE "$net"
AND interval=0.0
AND iteration=0),
(range_sum+.0)/(SELECT
range_sum FROM interval_threshold_stats
WHERE network LIKE "$net"
AND interval=0.0
AND iteration=0
AND query_number=1)
FROM interval_threshold_stats
WHERE network LIKE "$net" 
AND interval=0.0
AND iteration=0
ORDER BY query_number;
!
   done
   
   ../scripts/plot.sh -o progress \
   -f "all:20" \
   -y "Relative \$\\\sum_vt_H(v)-t_L(v)\$" \
   -x "query\\\#/(query set size)" \
   -a "set key t r width 9; set notitle; set xlabel offset 0,0" \
   -i "$fileList" 2> log;
}

function randomizedTable(){
# For main table used the following query
## query=$(
## cat << EOF
## select network,
## min(number_of_queries_after_compaction),
## printf("%.2f",((number_of_queries-number_of_queries_after_compaction)/(number_of_queries+.0)*100))
## from randomized
## where number_of_queries_after_compaction>0
## group by network;
## EOF
## )

tableFile="random_query_set.tex";

   cat << EOF > $tableFile
\small
\begin{tabular}{|l|c|c|c|c|}
\hline
\multirow{3}{*}{Network} & \multicolumn{4}{c|}{Query set size} \\\\\\cline{2-5}
& \multicolumn{2}{c|}{\$5\Delta+2\$} & \multicolumn{2}{c|}{\$10\Delta+2\$} \\\\\\cline{2-5}
& prob. & comp. & prob. & comp. \\\\
\hline
\hline
EOF
   for net in `cat networksList.dat | awk '/^#/{next}{print $1}'`
   do
      widthList=$(
cat << EOF
5
10
EOF
)
      row=`echo $net | sed -e 's/.giant$//'`" & ";
      for width in $widthList
      do
         query=$(
cat << EOF
SELECT printf("%.2f",(count(*)/50.0))
FROM randomized
WHERE network='$net' AND width=$width AND number_of_queries>0;
EOF
)
         row="$row"`sqlite3 $DB "$query" | sed -e 's/0\.00/--/g'`" & ";

         query=$(
cat << EOF
SELECT
printf("%.2f",(number_of_queries/avg(number_of_queries_after_compaction)))
FROM randomized
WHERE network='$net' AND width=$width AND number_of_queries>0
AND number_of_queries_after_compaction>0;
EOF
)
## cat << EOF
## SELECT
## printf("%.2f",((number_of_queries-number_of_queries_after_compaction)/(number_of_queries+.0)*100))
## FROM randomized
## WHERE network='$net' AND width=$width AND number_of_queries>0
## AND number_of_queries_after_compaction>0;
## EOF
## )
         row="$row"`sqlite3 $DB "$query" | sed -e 's/0\.00/--/g'`" & ";
      done
      row="$row"
      echo "$row" | sed -e 's/\& $/\\\\/' >> $tableFile
   done
   
   cat << EOF >> $tableFile
\hline
\end{tabular}
\normalsize
EOF
}

function realWorldIntervalRandomThreshold(){
   # interval random threshold for real-world graphs: varying intervals
   rm -f rw_interval_*dat;
   fileList=""
   for net in `cat networksList.dat | awk '/^#/{next}{print $1}'`
   do
      datFile=rw_interval_${net}.dat;
      fileList="$fileList $datFile";
      echo "$net" | sed -e 's/.giant$//' > $datFile;
      sqlite3 $DB <<! | awk -F',' '{print $1","$2","sqrt($3-$2*$2)}' >> $datFile
.separator ","
SELECT rtrim(replace(rtrim(greedy.experiment,'0123456789'),'interval_random_threshold_',''),'_') as interval,
(avg(queries)/(max_degree)) as a,
(avg(queries*queries)/(max_degree*max_degree))
FROM greedy
INNER JOIN network_props ON greedy.network=network_props.network 
WHERE greedy.network LIKE "$net" 
AND greedy.experiment LIKE "interval_random_threshold_${interval}_%"
GROUP BY interval
ORDER BY interval
!
   done
   
   ../scripts/plot.sh -o rw_interval_random_threshold \
   -t "Greedy heuristic on real-world networks" \
   -f "all:20" \
   -y "average \\\#queries\$/\\\Delta\$" \
   -x "threshold interval (fraction of \$d_v\$)" \
   -a "set nokey; set notitle; set xlabel offset 0,-.6; \
       set xtic offset 0,-.4; set ylabel offset 0,0" \
   -p "plot for [file in \"`echo $fileList`\"] file using 1:2:3 with linespoints ti columnheader(1)" 2> log;
}

function randomRegularIntervalRandomThreshold(){
   # interval random threshold for random regular graphs: varying intervals
   n=1000;
   rm -f rr_interval_*dat;
   fileList=""
   for interval in `seq 0 0.2 1 | awk '{printf("%.1f\n",$1)}'`
   do
      datFile=rr_interval_$interval.dat;
      fileList="$fileList $datFile";
      echo "\$$interval\$" > $datFile;
      sqlite3 $DB <<! | awk -F',' '{print $1","$3","sqrt($4-$3*$3)}' >> $datFile
.separator ","
SELECT (network_props.max_degree/(network_props.number_of_nodes+.0)) as df,
(network_props.max_degree+1),
avg(queries) as a,
avg(queries*queries)
FROM greedy
INNER JOIN network_props ON greedy.network=network_props.network 
WHERE (greedy.network LIKE "random_regular_${n}_%" 
OR greedy.network="K${n}")
AND greedy.experiment LIKE "interval_random_threshold_${interval}_%"
GROUP BY df
ORDER BY df
!
   done
   
   ../scripts/plot.sh -o rr_interval_random_threshold \
   -t "1000 node rand. \$k\$-reg. graph: varying threshold range \$\\\\theta\$" \
   -y "average \\\#queries" \
   -x "\$k/n\$" \
   -f "all:20" \
   -a "set key t l; set notitle; set xlabel offset 0,0" \
   -p "plot for [file in \"`echo $fileList`\"] file using 1:2:3 with linespoints ti columnheader(1)" 2> log;
}

function randomRegularRandomThreshold(){
   # random threshold for random regular graphs: effect of max degree
   n=1000;
   rm -f rr_random.dat;
   datFile=rr_random.dat;
   sqlite3 $DB <<! | awk -F',' '{print $1","$3","sqrt($4-$3*$3)}' >> $datFile
.separator ","
SELECT (network_props.max_degree/(network_props.number_of_nodes+.0)) as df,
(network_props.max_degree+1),
avg(queries) as a,
avg(queries*queries)
FROM greedy
INNER JOIN network_props ON greedy.network=network_props.network 
WHERE greedy.network LIKE "random_regular_${n}_%" AND
greedy.experiment LIKE "random_threshold%"
GROUP BY df
ORDER BY df
!
   ../scripts/plot.sh -o random_threshold \
   -t "1000 node random regular graph" \
   -y "average \\\#queries" \
   -x "\$\\\Delta/n\$" \
   -a "set key t l; set notitle" \
   -p "plot '$datFile' using 1:2:3 with yerrorbars noti" 2> log;
   ## ../scripts/plot.sh -o output \
   ## -t "Querying random regular graphs with fixed threshold \$t\$" \
   ## -y "average \\\#queries\$/\\\log\\\Delta\$" \
   ## -x "\$\\\Delta/n\$" \
   ## -p "plot for [file in \"`echo $fileList`\"] file using 1:2:3 with yerrorbars ti columnheader(1)" 2> log;
}

function randomRegularFixedThreshold(){
   # fixed threshold for random regular graphs: varying thresholds
   n=1000;
   rm -f rr_fixed_*dat;
   fileList=""
   for tf in `seq 0 0.2 1`
   do
      datFile=rr_fixed_$tf.dat;
      fileList="$fileList $datFile";
      if [[ $tf == 0 ]]; then
         echo "\$0\$" > $datFile;
      elif [[ $tf == 1 ]]; then
         echo "\$\\\Delta\$" > $datFile;
      else
         echo "\$$tf\\\Delta\$" > $datFile;
      fi
      sqlite3 $DB <<! | awk -F',' '{print $1","$3","sqrt($4-$3*$3)}' >> $datFile
.separator ","
SELECT (network_props.max_degree/(network_props.number_of_nodes+.0)) as df,
(network_props.max_degree+1),
avg(queries) as a,
"fixed_threshold_" || CAST((network_props.max_degree*$tf) AS INTEGER) as exp
FROM greedy
INNER JOIN network_props ON greedy.network=network_props.network 
WHERE (greedy.network LIKE "random_regular_${n}_%" 
OR greedy.network="K${n}")
AND greedy.experiment=exp
GROUP BY df
ORDER BY df
!
   done
   
   ../scripts/plot.sh -o fixed_threshold \
   -t "1000 node rand. \$k\$-reg. graphs: varying threshold values " \
   -f "all:20" \
   -y "average \\\#queries" \
   -x "\$k/n\$" \
   -a "set key t r; set notitle; set xlabel offset 0,0" \
   -p "plot for [file in \"`echo $fileList`\"] file using 1:2 with linespoints ti columnheader(1)" 2> log;
}

## function randomRegularFixedThresholdVaryingSize(){
##    # fixed threshold for random regular graphs: varying thresholds
##    nodesList="100 500 1000";
##    degreeFractionList="0.01 0.1 0.25 0.5";
##    for n in $nodesList
##    do
##       for df in $degreeFractionList
##       do
##          datFile=rr_${n}.dat
##          k=`awk -v "f=$df" -v "n=$n" 'BEGIN{printf "%d",f*n}'`;
## 
##          echo $n > $datFile;
##          sqlite3 $DB <<! | awk -F',' '{print $1","$3/log($2)","sqrt($4-$3*$3)/log($2)}' >> $datFile
## .separator ","
## SELECT (network_props.max_degree/(network_props.number_of_nodes+.0)) as df,
## (network_props.max_degree+1),
## avg(queries) as a,
## avg(queries*queries)
## FROM greedy
## INNER JOIN network_props ON greedy.network=network_props.network 
## WHERE greedy.network LIKE "random_regular_${n}_%" AND
## greedy.experiment LIKE "fixed_threshold%"
## GROUP BY df
## ORDER BY df
## !
##       done
##    done
## 
##    fileList=`ls -1 rr*dat | sort -t_ -k2 -n`;
##    
##    ../scripts/plot.sh -o output \
##    -t "Querying random regular graphs with fixed threshold \$t\$" \
##    -y "average \\\#queries\$/\\\log\\\Delta\$" \
##    -x "\$\\\Delta/n\$" \
##    -p "plot for [file in \"`echo $fileList`\"] file using 1:2:3 with yerrorbars ti columnheader(1)" 2> log;
## }

function cliques_fixed_threshold(){
   # fixed threshold for clique: varying thresholds for different cliques
   cliques=`sqlite3 $DB "SELECT network FROM network_props WHERE network LIKE 'K%'"`; 
   for net in `echo $cliques`
   do
      echo $net | sed -e 's/K//' > $net.dat
      sqlite3 $DB <<! | awk -F',' 'NR>1{print $1","$3/log($2)}' >> $net.dat
.separator ","
SELECT CAST(substr(experiment,17) AS FLOAT)/(network_props.max_degree+1) as q,
(network_props.max_degree+1),queries 
FROM greedy
INNER JOIN network_props ON greedy.network=network_props.network 
WHERE greedy.network="$net" AND
greedy.experiment LIKE "fixed_threshold%"
ORDER BY q;
!
   done
   fileList=`ls -1 K*dat | sort -tK -k2 -n`;
   
   ../scripts/plot.sh -o output \
   -t "Querying cliques with fixed threshold \$t\$" \
   -y "\\\#queries\$/\\\log(n)\$" \
   -x "\$t/\\\Delta\$" \
   -a "set yrange [0.5:1.5]; \
       set key b r;" \
   -i "$fileList" 2> log;
}

## gsqrdTable
## cp gsqrd_query_set.tex $DOCS;
## exit
## 
## randomizedTable
## cp random_query_set.tex $DOCS;

progressAdaptive
cp progress.pdf $DOCS;
cp progress.tex $DOCS;
cp progress.gp $DOCS;

realWorldIntervalRandomThreshold
cp rw_interval_random_threshold.pdf $DOCS;
cp rw_interval_random_threshold.tex $DOCS;
cp rw_interval_random_threshold.gp $DOCS;

randomRegularFixedThreshold
cp fixed_threshold.pdf $DOCS;
cp fixed_threshold.tex $DOCS;
cp fixed_threshold.gp $DOCS;

randomRegularIntervalRandomThreshold
cp rr_interval_random_threshold.pdf $DOCS;
cp rr_interval_random_threshold.tex $DOCS;
cp rr_interval_random_threshold.gp $DOCS;

#randomRegularRandomThreshold

