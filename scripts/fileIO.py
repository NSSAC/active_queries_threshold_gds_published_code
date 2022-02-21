"""
fileIO.py:
Abhijin Adiga
tags: readGraph writeGraph pickle fileIO
purpose: this module contains functions for input/output of graphs and any
other variables. 
"""
try:
    import cPickle as pickle
except:
    import pickle
import networkx as nx

# for dumping variables; useful for debugging and storing intermediate
# variables
def DumpObject(filename,obj) :
    f = open(filename, 'w')
    u = pickle.Pickler(f)
    u.dump(obj)
    f.close()
    return 0;

# for loading variables; useful for debugging and storing intermediate
# variables
def LoadObject(filename) :
    f = file(filename, 'r')
    u = pickle.Unpickler(f)
    o = u.load()
    f.close()
    return o;

# reads graph from file:
# graph input format: usual edge list format of networkx, edge data will be
# ignored currently.
# graph output: nx.Graph() object
def readGraph(filename,delim=None):
   G=nx.read_edgelist(filename,delimiter=delim,nodetype=int,data=False);
   G=nx.convert_node_labels_to_integers(G,0,discard_old_labels=False);
   G.remove_edges_from(G.selfloop_edges());
   return G;

# writes graph into specified file:
# graph input: nx.Graph() object
# graph output format: usual edge list format of networkx, edge data will be
# ignored currently.
def writeGraph(graph,filename):
   nx.write_edgelist(graph,filename,data=False);

# ignore for now
def readHRGRankFile(filename):
   f=open(filename,'r');
   edgeList=dict();
   edgeList['data']=[];
   edgeList['exp']=0;
   while True:
      line=f.readline().split();
      if line==[]: break;
      prob=float(line[2]);
      if prob!=0: 
         edgeList['data'].append([int(line[0]),int(line[1]),prob]);
         edgeList['exp']+=prob;
   f.close();

   return edgeList;
