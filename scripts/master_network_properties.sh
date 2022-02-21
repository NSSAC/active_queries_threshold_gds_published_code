#!/bin/bash
cat << 'EOF' > .tmp.netList
cycle6.uel
ca-grqc.giant.uel
oregon1_010331.txt
ca-hepth.giant.uel
p2p-Gnutella09.txt
oregon2_010519.txt
tweet.uel
ca-condmat.giant.uel
regular-20.uel
wiki.giant.uel
ca-hepph.giant.uel
enron.giant.uel
ca-astroph.giant.uel
cit-hepph.giant.uel
epin.giant.uel
soc-Epinions1.txt
slashdot0811.uel
slashdot0902.uel
soc-Slashdot0902.txt
web-NotreDame.txt
gowalla.txt
web-Stanford.txt
roadNet-PA.txt
amazon0505.txt
amazon0601.txt
roadNet-TX.txt
web-Google.txt
roadNet-CA.txt
web-BerkStan.txt
EOF

for f in `cat .tmp.netList | sed -e '/^#/d'`
do
   qsub ../scripts/qsub.1c1n.sfx.bash -v command="python ../scripts/network_properties.py ../../data/$f",Log="log_$f";
   if [[ $? -ne 0 ]]; then
      echo "Error computing bounds for $f."
      exit 1;
   fi
done
