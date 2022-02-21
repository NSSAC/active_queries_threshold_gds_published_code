#!/usr/bin/env python
# tags: code python completeGraph randomRegularGraph regular complete
#

import argparse
import networkx as nx
import random
import os
import sys
import argparse
import pdb
import logging

DESC="""Generating synthetic graphs
"""

def completeGraph(n):
   G=nx.complete_graph(n)
   nx.write_edgelist(G,'K%d.uel' %n,data=False)
   return

def randRegular(n,k,i):
   G=nx.random_regular_graph(k,n)
   nx.write_edgelist(G,'random_regular_%d_%d_%d.uel' %(n,k,i),data=False)
   return

if __name__=='__main__':
   ## nList=[10,50,100,500,1000]
   ## for n in nList:
   ##    completeGraph(n)

   nList=[1000]
   #DList=[0.01,0.1,0.25,0.5]
   #DList=[0.05,0.7,0.9]
   #DList=[0.2,0.4]
   DList=[0.8]
   for n in nList:
      for k in DList:
         for i in xrange(10):
            randRegular(n,int(n*k),i+1)

