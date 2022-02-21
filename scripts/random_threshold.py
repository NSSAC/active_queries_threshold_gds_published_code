#!/usr/bin/env python
# tags: code python thresholdAlgorithm threshold

import argparse
import random
import networkx as nx
import numpy as np
import pdb
import logging
import itertools
import os
from time import time

import threshold_algorithm_greedy

DESC="""Random threshold experiments
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

   start=time()

   # construct G squared
   Gsqr=nx.power(G,2)

   gsqrd_time = time() - start

   itr_time = time()
   for itr in xrange(10):
      # set threshold
      T=np.random.randint(0,high=D+1,size=G.number_of_nodes())

      # run greedy threshold
      [success,queries,T_]=threshold_algorithm_greedy.greedyDistanceTwo(G,T,threshold_algorithm_greedy.successorStandardThreshold,Gsqr)
      if success:
         print "INSERT OR REPLACE INTO greedy (network,experiment,queries,gsqrd_time,greedy_time) VALUES ('%s','random_threshold_%d',%d,%f,%f);" %(filename,itr+1,queries,gsqrd_time,time()-itr_time)
      else:
         print "filename=%s; experiment=random_threshold_%d; Thresholds did not match." %(filename,threshold)

      itr_time = time()
      
      
