#!/usr/bin/env python
# tags: code python thresholdAlgorithm threshold

import argparse
import re
import random
import numpy as np
import networkx as nx
import pdb
import logging
import itertools
import os
from string import Template

import threshold_algorithm_greedy

DESC="""Interval random threshold experiments
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
   parser.add_argument("network", action="store")
   parser.add_argument("interval", action="store", type=float)
   parser.add_argument("-d","--delimiter", action="store", default=None,help="delimiter")
   parser.add_argument("-v", "--verbose", action="store_true")
   args = parser.parse_args()

   # set logger
   if args.verbose:
      logging.basicConfig(level=logging.DEBUG)
   else:
      logging.basicConfig(level=logging.INFO)

   # read graph
   G=nx.convert_node_labels_to_integers(nx.read_edgelist(args.network,delimiter=args.delimiter,nodetype=int),label_attribute="label")
   nodeIds=np.empty(G.number_of_nodes(),dtype=int)
   for i in np.arange(G.number_of_nodes()):
      nodeIds[i]=G.node[i]['label']
   filename=re.sub('\.uel$','',os.path.basename(args.network))
   filename=re.sub('\.txt$','',filename)

   Gsqr=nx.power(G,2)   # construct G squared
   T=np.empty((G.number_of_nodes(),),dtype=int)    # initialize thresholds vector
   stats={}
   stats['network']=filename
   stats['interval']=args.interval
   config=Template(threshold_algorithm_greedy.COMPACTION_CONFIG_TEMPLATE)

   for itr in xrange(10):
      if itr and not args.interval:
         continue

      stats['itr']=itr

      assignRandomIntervalThreshold(G,T,args.interval)

      # run greedy threshold
      [success,queries,querySet,T_]=threshold_algorithm_greedy.greedyDistanceTwo(G,T,threshold_algorithm_greedy.successorStandardThreshold,stats,Gsqr)
      if success:
         print "INSERT OR REPLACE INTO greedy_v2 \
         (network,experiment,interval,iteration,queries) VALUES \
         ('%s','interval_random_threshold',%.1f,%d,%d);" \
         %(filename,args.interval,itr+1,queries)

         # output queries to file
         prefix="%s_%.1f_%d" %(filename,args.interval,itr+1)
         configFile=prefix+".cfg"
         queryFile=prefix+".que"
         threshold_algorithm_greedy.outputQueriesForCompaction(queryFile,querySet,nodeIds)
         with open(configFile,'w') as f:
            f.write(config.substitute(network=args.network,queryFile=queryFile,outFilePrefix=prefix))
      else:
         print "filename=%s; experiment=interval_random_threshold_%.1f_%d'; Thresholds did not match." %(filename,args.interval,itr+1)
