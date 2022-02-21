#!/usr/bin/env python
# tags: code python thresholdAlgorithm threshold

import argparse
import random
import networkx as nx
import numpy as np
import pdb
import logging
import itertools

MAX_QUERIES=10000
DESC="""The adaptive algorithm for discovering thresholds in a threshold
system. The main program runs a simple example.
-----
Assumption(s):
   * Node labels are from 0 to n-1, where n is the size of the graph.
   * Undirected graph (for now)
-----
"""

COMPACTION_CONFIG_TEMPLATE="""[
  {
      "is_specified_seed": "0",
      "fixed_seed": "114",

      "graph_file_uel": "$network",

      "configurations_file": "$queryFile",
      "configuration_format": "node_state_pairs",

      "output_file_configurations": "compaction_${outFilePrefix}.que",
      "output_file_configuration_ids": "compaction_${outFilePrefix}.ids",
      "output_file_iter_details": "compaction_${outFilePrefix}.det"
}
]
"""

def outputQueriesForCompaction(outfile,queries,nodeIds):
   numNodes=queries[0].size
   qWithNodeIds=np.empty(2*numNodes,dtype=int)
   qWithNodeIds[0::2]=nodeIds

   with open(outfile,'w') as f:
      for q in queries:
         qWithNodeIds[1::2]=q
         qWithNodeIds.tofile(f,sep=" ",format="%d")
         f.write("\n")

def hammingWeight(nodeIter,q):
   numOnes=0
   for u in nodeIter:
      numOnes+=q[u]
   return numOnes

def successorStandardThreshold(G,T,q,q_):
   for v in G.nodes():
      hammWt=hammingWeight(itertools.chain([v],G.neighbors_iter(v)),q) 
      if hammWt>=T[v]:
         q_[v]=1
      else:
         q_[v]=0
   return

def greedyDistanceTwo(G,T,successor,stats,Gsqr=False):

   # G^2
   if not Gsqr:
      logging.debug("Constructing G^2 ...")
      Gsqr=nx.power(G,2)

   # Initializing vectors
   nodesToConsider=np.ones((G.number_of_nodes(),),dtype=bool)
   q=np.zeros((G.number_of_nodes(),),dtype=bool)      # state vector
   s=np.zeros((G.number_of_nodes(),),dtype=bool)      # successor state vector
   tHigh=np.zeros((G.number_of_nodes(),),dtype=int)   # upper bound on threshold
   tLow=np.zeros((G.number_of_nodes(),),dtype=int)    # lower bound on threshold
   querySet=[]

   for v in G.nodes():
      tHigh[v]=G.degree(v)+2

   # start iterations
   logging.debug("Algorithm begins ...")
   allThresholdsDiscovered=False
   numQueries=0
   totalRange=np.sum(tHigh-tLow)
   totalNodesToConsider=np.sum(nodesToConsider)

   while True:
      # construct query
      while sum(nodesToConsider):

         # find the node with max threshold interval
         vmax=np.argmax(np.multiply(nodesToConsider,tHigh-tLow))

         nodesToConsider[vmax]=False
         reqHammWt=(tHigh[vmax]+tLow[vmax])/2
         if reqHammWt:
            q[vmax]=True
            currHammWt=1
         else:
            q[vmax]=False
            currHammWt=0

         for v in G.neighbors_iter(vmax):
            if currHammWt<reqHammWt:
               currHammWt+=1
               q[v]=True
            else:
               q[v]=False

         for v in itertools.chain([vmax],Gsqr.neighbors_iter(vmax)):
            nodesToConsider[v]=False

         logging.debug("query=%d; vmax=%d; required hamming Weight=%d" \
               %(numQueries+1,vmax,reqHammWt))

      # book keeping
      querySet.append(np.copy(q))
      print "INSERT OR REPLACE INTO interval_threshold_stats \
      (network,interval,iteration,query_number,nodes_to_resolve,range_sum) VALUES \
      ('%s',%.1f,%d,%d,%d,%d);" \
      %(stats['network'],stats['interval'],stats['itr'],numQueries+1,totalNodesToConsider,totalRange)

      # Query is constructed. Find the successor.
      successor(G,T,q,s)   # find the successor of q

      # Update threshold intervals
      for v in G.nodes():
         if tHigh[v]==tLow[v]:
            continue
         hammWt=hammingWeight(itertools.chain([v],G.neighbors_iter(v)),q) 
         if s[v] and tHigh[v]>hammWt:
            tHigh[v]=hammWt
         elif not s[v] and tLow[v]<=hammWt:
            tLow[v]=min(tHigh[v],hammWt+1)
      
      # reset nodes to consider
      nodesToConsider=tHigh!=tLow
      totalRange=np.sum(tHigh-tLow)
      totalNodesToConsider=np.sum(nodesToConsider)

      # check if all thresholds discovered
      if not totalNodesToConsider:
         break
      
      numQueries+=1
      if numQueries>MAX_QUERIES:
         logging.error("Number of queries exceeded %d. exiting" %MAX_QUERIES)
         break

      # while np.sum(nodesToConsider): ends here
   # while True: end here

   logging.debug("Comparing discovered thresholds with actual thresholds ...")
   if np.array_equal(T,tHigh):
      logging.debug("They match!")
      # queryCompaction()
      return True,numQueries,querySet,tHigh
   else:
      logging.debug("They don't match!")
      return False,numQueries,querySet,tHigh

def exampleWheelGraph():
   numNodes=10
   G=nx.wheel_graph(numNodes)
   T=np.zeros((numNodes,),dtype=int)
   T.fill(2)
   T[0]=5

   # run algorithm
   [success,queries,T_]=greedyDistanceTwo(G,T,successorStandardThreshold)

   if success:
      print "Number of queries=%d" %queries
   else:
      print "Thresholds did not match."
      print "Actual thresholds:", T
      print "Discovered thresholds:", T_

   return

def exampleCompleteGraphSameThresholds():
   numNodes=100
   G=nx.complete_graph(numNodes)
   T=np.empty((numNodes,),dtype=int)

   for threshold in xrange(numNodes):
      T.fill(threshold)

      # run algorithm
      [success,queries,T_]=greedyDistanceTwo(G,T,successorStandardThreshold)

      if success:
         print "%d-clique; t=%d; queries=%d" %(numNodes,threshold,queries)
      else:
         print "%d-clique; t=%d; Thresholds did not match." \
            %(numNodes,threshold)

def exampleCompleteGraphRandomThresholds():
   numNodes=100
   G=nx.complete_graph(numNodes)

   np.random.seed(12345)

   for i in xrange(10):
      T=np.random.randint(0,high=numNodes,size=numNodes)

      # run algorithm
      [success,queries,T_]=greedyDistanceTwo(G,T,successorStandardThreshold)

      if success:
         print "%d-clique; i=%d; queries=%d" %(numNodes,i,queries)
      else:
         print "%d-clique; i=%d; Thresholds did not match." \
            %(numNodes,i)

def exampleRandomRegularGraphRandomThresholds():
   numNodes=100
   np.random.seed(12345)
   random.seed(12345)

   for k in xrange(2,numNodes):
      G=nx.random_regular_graph(k,numNodes)
      for i in xrange(10):
         T=np.random.randint(0,high=k+1,size=numNodes)

         # run algorithm
         [success,queries,T_]=greedyDistanceTwo(G,T,successorStandardThreshold)

         if success:
            print "nodes=%d; k=%d; itr=%d; queries=%d" %(numNodes,k,i,queries)
         else:
            print "nodes=%d; k=%d; itr=%d; Thresholds did not match." \
               %(numNodes,k,i)
         exit

if __name__=='__main__':
   # parser
   parser = argparse.ArgumentParser(description=DESC,formatter_class=argparse.RawTextHelpFormatter)
   parser.add_argument("-v", "--verbose", action="store_true")
   args = parser.parse_args()

   # set logger
   if args.verbose:
      logging.basicConfig(level=logging.DEBUG)
   else:
      logging.basicConfig(level=logging.INFO)

   # run example
   # exampleWheelGraph()
   # exampleCompleteGraphSameThresholds()
   # exampleCompleteGraphRandomThresholds()
   # exampleRandomRegularGraphRandomThresholds()
   exampleRandomRegularGraphRandomThresholds()
   
