#!/usr/bin/env python
# tags: code python thresholdAlgorithm threshold class
#

import argparse
import networkx as nx
from random import randint
from random import random
from random import seed
import os
import sys
import argparse
import pdb
import logging
import time

DESC="""This code implements the algorithm for discovering thresholds. It
also implements various experiments in order to evaluate the algorithm.
"""

WAIT_PERIOD=2

class NodeAttrib:
   
   def __init__(self, degree, tHigh, tLow, chargeRange):
      self.degree = degree
      self.thresholdDiscovered = True
      self.update(tHigh,tLow,chargeRange)

   def update(self, tHigh, tLow,chargeRange):
      self.tHigh = tHigh
      self.tLow = min(tHigh,tLow)
      if not self.thresholdDiscovered:
         if tHigh==tLow:
      avgHammWt=(self.tHigh+self.tLow)/2.0/(self.degree+1)
      if tHigh==tLow or (avgHammWt<chargeRange[0] or avgHammWt>chargeRange[1]):
         self.avgHammWt = 0  # no contribution to charge 
         self.influence = 0
      else:
         self.avgHammWt = avgHammWt
         self.influence = 1
      self.accumulatedCharge=self.avgHammWt
      self.neighborsToResolve=self.influence + .0

   def disp(self):
      return "tHigh=%d,tLow=%d,degree=%d,avgHammWt=%g,accumulated charge=%g" \
         %(self.tHigh,self.tLow,self.degree,self.avgHammWt,self.accumulatedCharge)

def stateOneNeighbors(v,neighbors,q):
   numOnes=q[v]
   for u in neighbors:
      numOnes+=q[u]
   return numOnes

def successorStandardThreshold(G,T,q):
   q_={}
   for v in G.nodes():
      numOnes=stateOneNeighbors(v,G.neighbors(v),q)
      if numOnes>=T[v]:
         q_[v]=1
      else:
         q_[v]=0
   return q_

def thresholdAlgorithm(G,T,successor,cRange=[0,1],waitPeriod=WAIT_PERIOD):

   # set state vector and node attributes required by the algorithm
   logging.debug("Initializing state and node attributes vectors ...")
   q={}  # state vector
   nodeProp={} # node attributes for the algorithm

   for v in G.nodes():
      # set initial state uniformly at random (shouldn't be zero vector)
      allZeroInd=True
      while allZeroInd:
         if random()>=.5:
            q[v]=1
            allZeroInd=False
         else:
            q[v]=0
      nodeProp[v]=NodeAttrib(G.degree(v),G.degree(v)+1,0,cRange)
   
   # start iterations
   logging.debug("Algorithm begins ...")
   numQueries=1
   noProgressCount=0

   while True:
      progressInd=False    # true if tHigh or tLow changes for some node
      s=successor(G,T,q)   # find the successor of q

      if logging.getLogger().getEffectiveLevel()==10: # if set to DEBUG
         logging.debug("*****Query %d*****" %numQueries)
         for v in G.nodes():
            logging.debug("%d,%d,%s" %(v,q[v],nodeProp[v].disp()))
         logging.debug("*****")

      # set threshold
      for v in G.nodes():
         # determine threshold interval
         if nodeProp[v].tHigh==nodeProp[v].tLow:
            nodeProp[v].update(nodeProp[v].tHigh,nodeProp[v].tLow,cRange)
            continue
         numOnes=stateOneNeighbors(v,G.neighbors(v),q) 
         if s[v] and nodeProp[v].tHigh>numOnes:
            progressInd=True
            nodeProp[v].update(numOnes,nodeProp[v].tLow,cRange)
         elif not s[v] and nodeProp[v].tLow<=numOnes:
            progressInd=True
            nodeProp[v].update(nodeProp[v].tHigh,numOnes+1,cRange)
         else:
            nodeProp[v].update(nodeProp[v].tHigh,nodeProp[v].tLow,cRange)

      # terminate loop if no progress and wait period exceeded
      if not progressInd:
         if noProgressCount>waitPeriod:
            break
         else:
            noProgressCount+=1

      # update accumulated avgHammWt vector based on closed neighborhood
      for e in G.edges():
         u=e[0]
         v=e[1]
         nodeProp[v].accumulatedCharge+=nodeProp[u].avgHammWt
         nodeProp[u].accumulatedCharge+=nodeProp[v].avgHammWt
         nodeProp[v].neighborsToResolve+=nodeProp[u].influence
         nodeProp[u].neighborsToResolve+=nodeProp[v].influence

      # set new state vector
      numQueries+=1
      for v in G.nodes():
         if nodeProp[v].neighborsToResolve:
            avgCharge=nodeProp[v].accumulatedCharge/nodeProp[v].neighborsToResolve
         else:
            avgCharge=0.5  # this node has no use now; can be set to any state
         if avgCharge>=random():
            q[v]=1
         else:
            q[v]=0

      # while ends here

   # check if converged, and if yes, then, extract threshold
   logging.debug("Comparing discovered thresholds with actual thresholds.")
   for v in G.nodes():
      if nodeProp[v].tLow!=T[v]:
         logging.error("Incorrect threshold estimate for '%d': actual t=%d; est t=%d" \
               %(v,T[v],nodeProp[v].tLow))
         return False,numQueries

   return True,numQueries

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
   # parser
   parser = argparse.ArgumentParser()
   parser.add_argument("-v", "--verbose", action="store_true")
   args = parser.parse_args()

   # set logger
   if args.verbose:
      logging.basicConfig(level=logging.DEBUG)
   else:
      logging.basicConfig(level=logging.INFO)

   # run example 1
   # cliqueOneThreshold()

   # run example 2
   cliqueRandomThreshold()
   
