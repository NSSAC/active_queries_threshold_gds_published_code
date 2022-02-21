# Experiments with synthetic graphs

import argparse
import networkx as nx
import numpy as np
import os
import sys
import pdb
import logging
import itertools
import threshold_algorithm_greedy

def cliqueOneThreshold():
   # This is a test case as well as example for thresholdAlgorithm.
   # All thresholds will be the same.
   seedVal=12345
   seed(seedVal)

   # generate graph
   numNodes=100
   G=nx.complete_graph(numNodes)

   for threshold in xrange(numNodes+1):
      T={}                 
      for v in G.nodes():
         T[v]=threshold

      # run threshold algorithm
      [state,numQueries]=thresholdAlgorithm(G,T,successorStandardThreshold,MAX_QUERIES) 
      if state==False:
         logging.error("Not all thresholds discovered.")
      else:
         logging.debug("All thresholds discovered")

      print "experiment=clique_fixed_threshold; clique size=%d; threshold=%d; seed=%d; queries: %d;" \
            %(G.number_of_nodes(),threshold,seedVal,numQueries)
   return

def cliqueRandomThreshold():
   # This is a test case as well as example for thresholdAlgorithm
   seedVal=12345
   seed(seedVal)

   # generate graph
   numNodes=100
   G=nx.complete_graph(numNodes)

   # set random thresholds
   T={};
   for node in G.nodes():
      T[node]=randint(0,numNodes+1)   

   # run threshold algorithm
   [state,numQueries]=thresholdAlgorithm(G,T,successorStandardThreshold,MAX_QUERIES) 
   if state==False:
      logging.error("Not all thresholds discovered.")
   else:
      logging.debug("All thresholds discovered")

   print "experiment=clique_random_threshold; clique size=%d; seed=%d; queries: %d" \
         %(G.number_of_nodes(),seedVal,numQueries)
   return

if __name__=='__main__':
