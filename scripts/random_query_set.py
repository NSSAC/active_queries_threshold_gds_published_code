#!/usr/bin/env python
# tags: code python thresholdAlgorithm threshold

import argparse
import random
import networkx as nx
import numpy as np
import pdb
import re
import os
import logging
import itertools
from string import Template

DESC="""The randomized algorithm for constructing complete sets. The main
program runs a simple example.
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

      "output_file_configurations": "${outFilePrefix}.compque",
      "output_file_configuration_ids": "${outFilePrefix}.ids",
      "output_file_iter_details": "${outFilePrefix}.det"
}
]
"""

def outputQueriesForCompaction(outfile,queries,nodeIds):
   querySize=queries.shape
   numNodes=querySize[0]
   numQueries=querySize[1]
   qWithNodeIds=np.empty(2*numNodes,dtype=int)
   qWithNodeIds[0::2]=nodeIds

   with open(outfile,'w') as f:
      for i in xrange(numQueries):
         qWithNodeIds[1::2]=queries[:,i]
         qWithNodeIds.tofile(f,sep=" ",format="%d")
         f.write("\n")

def randBit(p):
   return np.random.choice(a=[True,False],size=(1,1),p=[p,1-p])

def randomQuerySet(G,segmentWidth=1):
   maxDegree=max(G.degree().values())
   numNodes=G.number_of_nodes()

   querySet=np.empty((numNodes,maxDegree*segmentWidth+2),dtype=bool)
   querySet[:,0]=np.zeros((numNodes,),dtype=bool)
   querySet[:,1:2]=np.ones((numNodes,1),dtype=bool)

   start=2
   for i in np.arange(1,maxDegree+1):
      querySet[:,start:start+segmentWidth]=np.random.rand(numNodes,segmentWidth)<i/(maxDegree+1.0)
      start+=segmentWidth
   return querySet

def checkIfCompleteSet(G,querySet):
   for v in G.nodes():
      neighborhood=G.neighbors(v)
      scoreInd=np.zeros((len(neighborhood)+2,),dtype=int)
      for i in np.arange(0,querySet.shape[1]):
         score=int(querySet[v,i])
         for u in neighborhood:
            score+=querySet[u,i]
         scoreInd[score]=i+1
      if np.sum(scoreInd==0):
         return False,v,np.argmin(scoreInd)
   return True,None,None

if __name__=='__main__':
   # parser
   parser = argparse.ArgumentParser(description=DESC,formatter_class=argparse.RawTextHelpFormatter)
   parser.add_argument("network", action="store")
   parser.add_argument("width", action="store", type=int)
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
   config=Template(COMPACTION_CONFIG_TEMPLATE)

   # generate queries
   for i in xrange(5):
      querySet=randomQuerySet(G,args.width)
      [success,node,score]=checkIfCompleteSet(G,querySet)
      if success:
         # output queries to file for compaction
         prefix="comp_%s_%d_%d" %(filename,args.width,i+1)
         configFile=prefix+".cfg"
         queryFile=prefix+".que"
         outputQueriesForCompaction(queryFile,querySet,nodeIds)
         with open(configFile,'w') as f:
            f.write(config.substitute(network=args.network,queryFile=queryFile,outFilePrefix=prefix))
         # no need to insert to database here. It is handled by update_db.sh
         # print "INSERT OR REPLACE INTO randomized (network,width,iteration,number_of_queries) VALUES ('%s',%d,%d,%d);" %(filename,args.width,i+1,querySet.shape[1])
      # else:
      #    print "Not complete set: '%s',%d,%d,%d);" %(filename,args.width,i+1,node)


