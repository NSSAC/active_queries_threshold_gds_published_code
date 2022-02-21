#!/usr/bin/env python
# tags: code python thresholdAlgorithm threshold

import argparse
import random
import networkx as nx
import numpy as np
import pdb
import logging
import os

import threshold_algorithm_greedy

DB="../results/experiment_results.db"
DESC="""Fixed threshold experiments
"""

if __name__=='__main__':
   # parser
   parser = argparse.ArgumentParser(description=DESC,formatter_class=argparse.RawTextHelpFormatter)
   parser.add_argument("network", action="store")
   parser.add_argument("-d","--delimiter", action="store", default=None,help="delimiter")
   parser.add_argument("-v", "--verbose", action="store_true")
   args = parser.parse_args()

   # read graph
   G=nx.read_edgelist(args.network,delimiter=args.delimiter,nodetype=int) 
   filename=os.path.basename(args.network).rstrip('.uel').rstrip('.txt')
   D=max(G.degree().values())

   # construct G squared
   Gsqr=nx.power(G,2)

   for threshold_fraction in np.arange(0,1.1,0.2):
      threshold=int(threshold_fraction*D)

      # set threshold
      T=np.empty((G.number_of_nodes(),),dtype=int)
      T.fill(threshold)

      # run greedy threshold
      [success,queries,T_]=threshold_algorithm_greedy.greedyDistanceTwo(G,T,threshold_algorithm_greedy.successorStandardThreshold,Gsqr)
      if success:
         print "INSERT OR REPLACE INTO greedy (network,experiment,queries) VALUES ('%s','fixed_threshold_%d',%d);" %(filename,threshold,queries)
      else:
         print "filename=%s; experiment=fixed_threshold_%d; Thresholds did not match." %(filename,threshold)
      
