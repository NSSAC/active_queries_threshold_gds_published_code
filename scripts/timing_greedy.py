#!/usr/bin/env python
# tags: code python thresholdAlgorithm threshold

import argparse
import random
import networkx as nx
import numpy as np
from pdb import set_trace
import logging
import itertools
import os
from time import time

import threshold_algorithm_greedy

DESC="""Random threshold experiments
"""

def assignRandomIntervalThreshold(G,T,interval):
   for v in G.nodes():
      D=G.degree(v)

      # set threshold
      if interval:
         leftmost=int((D+2)/2*(1-interval))
         rightmost=int((D+2)/2*(1+interval))
         T[v]=np.random.randint(leftmost,high=rightmost+1,size=1)
      else:
         T[v]=(D+2)/2

if __name__=='__main__':
   # parser
   parser = argparse.ArgumentParser(description=DESC,formatter_class=argparse.RawTextHelpFormatter)
   parser.add_argument("-n", "--nodes", required = True, type = int)
   parser.add_argument("-p", "--probability", required = True, type = float)
   parser.add_argument("-i", "--interval", required = True, type=float)
   parser.add_argument("-k", "--count", required = True, type = int)
   parser.add_argument("-v", "--verbose", action="store_true")
   args = parser.parse_args()

   # read graph
   G = nx.fast_gnp_random_graph(args.nodes,args.probability)
   D=max([d for i,d in G.degree])

   start=time()

   # construct G squared
   Gsqr=nx.power(G,2)

   gsqrd_time = time() - start,

   itr_time = time()

   # set threshold
   T=np.empty((G.number_of_nodes(),),dtype=int) # initialize thresholds vector
   assignRandomIntervalThreshold(G,T,args.interval)

   # run greedy threshold
   [success,queries,T_]=threshold_algorithm_greedy.greedyDistanceTwo(G,T,threshold_algorithm_greedy.successorStandardThreshold,Gsqr)
   if success:
      print(f"INSERT OR REPLACE INTO greedy_timing (nodes,probability,interval,instance,queries,gsqrd_time,greedy_time) VALUES ({args.nodes},{args.probability},{args.interval},{args.count},{queries},{gsqrd_time[0]},{time()-itr_time});")
   else:
      print("Thresholds did not match.")

   itr_time = time()

