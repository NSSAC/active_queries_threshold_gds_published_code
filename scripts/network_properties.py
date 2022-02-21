#!/usr/bin/env python
# tags: code python kcore coloringNumber inductiveColoring graphSquare
# squareOfGraph greedyColoring
#

import argparse
import networkx as nx
import random
import os
import sys
import argparse
import pdb
import logging

DESC="""This code generates network specific bounds for adaptive and
non-adaptive querying"""

def insert2db(filename,attribute,value):
   print "INSERT OR IGNORE INTO properties (filename,attribute,value) VALUES (\"%s\",\"%s\",\"%s\");" %(filename,attribute,str(value))
   return
   
def basicProps(G,filename):
   insert2db(filename,'number_of_nodes',G.number_of_nodes())
   insert2db(filename,'number_of_edges',G.number_of_edges())
   insert2db(filename,'max_degree',max(nx.degree(G).values()))
   return

def maxCoreSquare(G):
   #col=nx.coloring.greedy_color(nx.power(G,2),strategy=nx.coloring.strategy_smallest_last)
   Gsqr=nx.power(G,2)
   return max(nx.core_number(Gsqr).values())

if __name__=='__main__':
   # parser
   parser = argparse.ArgumentParser()
   parser.add_argument("network", action="store", help="network file")
   parser.add_argument("-d","--delimiter", action="store", default=None,help="delimiter")
   parser.add_argument("-v", "--verbose", action="store_true")
   args = parser.parse_args()

   # set logger
   if args.verbose:
      logging.basicConfig(level=logging.DEBUG)
   else:
      logging.basicConfig(level=logging.INFO)

   # read graph
   G=nx.read_edgelist(args.network,delimiter=args.delimiter) 
   filename=os.path.basename(args.network)

   # checking for selfloops
   sle=G.selfloop_edges()
   if sle:
      logging.warning("Found at least one selfloop. Removing ...")
      G.remove_edges_from(sle)

   basicProps(G,filename)

   # max core number of square of graph
   insert2db(filename,'square_kmax',maxCoreSquare(G))
