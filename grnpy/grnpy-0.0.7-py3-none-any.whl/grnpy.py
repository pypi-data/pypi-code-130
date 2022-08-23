import sys
import math
import random
import numpy as np
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from networkx.algorithms import tree
from itertools import combinations, groupby
from networkx import is_connected, connected_components
"""
定义一个玻尔兹曼机基因调控网络的类
Define a Boltzmann Gene Regulatory Network Class

待开发
  - 定义不同的基因树，以及不同搭造基因树的方法
    - 现有方法：(Generate Gene Tree)
    - 从一个连通图删除边缘直到形成一个树(在保证每个节点连接性的条件下无边缘可删除)
    - 搭建有向树
    - 不同的更新基因状态策略

To be Implemented
  - Different ways of generating a GRN
    - Current Method (Generate Gene Tree Function)
    - While ensuring connectivity, delete edges until no more
        edges can be deleted
    - Define a directed Graph
    - Different update rules
"""
class BoltzmannGRN():
  def __init__(self, size, on_p, weight, sparsity, directed, type_state):
    """
    模型初始化
    1. 定义模型大小（基因数量）
    2. 定义基因关系矩阵
    3. 随概率计算基因的开关状态

    Model Initialization
    1. Define the model size (number of Genes)
    2. Define Gene Relation Matrix (Weight of Edges)
    3. Define the state of the gene based on probability
    """
    self.size = size
    self.type_state = type_state
    self.weight = weight
    self.graph = self.Generate_Gene_Network(size, sparsity, on_p, directed)
    self.matrix = self.make_wmatrix(self.graph, self.size, weight)
    self.sparsity = sparsity

  def conversion(self, G_o):
    """
    在两种模型结构中转换

    Convert Between the two types of Gene State Systems
    """
    G_n = G_o
    if self.type_state == 'binary':
      self.type_state = 'spin' #Set type of network system to spin
      for node in G_o.nodes:
        if G_o.nodes[node]["state"] == 0: #Set the 0 states to -1
          G_n.nodes[node]["state"] = -1

    elif self.type_state == 'spin':
      self.type_state = 'binary' #Set type of network system to binary
      for node in G_o.nodes:
        if G_o.nodes[node]["state"] == -1: #Set the -1 states to 0
          G_n.nodes[node]["state"] = 0
    else:
      exit('Something went wrong, type_state is supposed to be "spin" or "binary"') #Exit with Error message if type_state is anything else
    return G_n

  def Generate_Gene_Network(self, n, sparsity, on_p, directed):
    """
    1. 定义一个有n个节点，0边缘的图
    2. 第m个节点有相同概率连接到任意一个(m-1)的节点

    1. Define a graph of n nodes, w/o edges
    2. node m will have equal probablity to connect to any node with m-1
    """
    print(type(sparsity))
    if type(directed) == bool and (type(sparsity) == float or type(sparsity) == int) and type(n) == int and n > 0 and (self.type_state == "spin" or self.type_state == "binary"):
      if sparsity >= 0 and sparsity <= 1:
        """
        Return Error Message if:
          - directed is not boolean
          - sparsity is not an integer or float
          - sparsity is less than 0 and greater than 1
          - number of nodes is less than 0
          - type of Gene State system is not binary or spin
        """
        if directed == True: #Set a directed graph if directed graph option is set to be true
          M = nx.complete_graph(n, nx.DiGraph()) #Complete Graph to subtract from
          G = nx.DiGraph() #Tree to be built
        else: #Set an undirected graph if directed graph option is set to be false
          M = nx.complete_graph(n)
          G = nx.Graph()

        G.add_node(0) #Add a single node
        for i in range(1, n): #Iterate through number of nodes to generate a spanning Tree
          num = G.number_of_nodes()
          G.add_node(i)
          toConnect = random.randint(0, num-1) #Connect to a random node before it at equal probability
          G.add_edge(toConnect, i) #Connect

        D = nx.difference(M, G) #Get the difference bewtween the complete graph and spanning tree
        num_remove = math.ceil(len(D.edges) * sparsity) #Get the number of nodes to remove
        edgeSet = list(D.edges) #Get the edges that we can remove
        rmlist = [] #Define an empty list of edges to remove
        for i in range(0, num_remove):
          chosen = random.choice(edgeSet) #Randomly choose from nodes that we can remove
          a = chosen[0]
          b = chosen[1]
          M.remove_edge(a,b) #Remove Edge
          edgeSet.remove(chosen) #Remove Edge from the Edge set

        if self.type_state == 'binary': #Set the states depending on graph Type
          state0 = 0 #Binary - 0
        elif self.type_state == 'spins':
          state0 = -1 #Spin - -1
        state1 = 1 #Both states have 1
        for node in M.nodes: #Iterate through nodes and set state depending on initial Probability
          chance = random.random() #Random Chance
          if chance < on_p:
            M.nodes[node]["state"] = state1
          else:
            M.nodes[node]["state"] = state0
        if directed == True:
          d = 'directed'
        else:
          d = 'undirected'
        print("================================================================")
        print(f"Graph created with ", n, " nodes. The graph is", d)
        print(f"Model Sparsity is set to", sparsity)
        print(f"Model Update Weight is set to", self.weight)
        print("================================================================")
        return M
      else:
        errorMessage = "Error in parameters: "
        errorMessage += "'sparsity' expected to be between 0 and 1, but got " + str(sparsity) + " instead. "
        sys.exit(errorMessage)


    else: #Error Messages
      errorMessage = "Error in parameters: "
      if type(directed) != bool:
        typeD = type(directed)
        errorMessage += "'directed' expected bool, but got " + str(typeD) + " instead. "
      if type(sparsity) != float and type(sparsity) != int:
        typeS = type(sparsity)
        errorMessage += "'sparsity' expected float or int, but got " + str(typeS) + " instead. "
      elif sparsity > 1 or sparsity < 0:
        errorMessage += "'sparsity' expected to be between 0 and 1, but got " + str(sparsity) + " instead. "
      if type(n) != int:
        typeN = type(n)
        errorMessage += "'n' expected int, but got " + str(typeN) + " instead. "
      elif n < 0:
        errorMessage += "'n' expected to be greater than 0, but got " + str(n) + " instead. "
      if self.type_state != 'binary' and self.type_state != 'spin':
        errorMessage += "'type_state' expected to be 'binary' or 'spin', but got " + self.type_state + " instead. "
      sys.exit(errorMessage)

  def make_wmatrix(self, G, size, weight):
    """
    定义一个定义基因关系矩阵，大小为(n*n) n是基因数量

    Make a weight matrix for the graph of size n*n n being the
      number of genes in the network
    """
    wmatrix = np.zeros((size, size)) #Create a weight matrix
    for node in G.nodes(): #Iterate through all nodes
      for neighbour in G.neighbors(node): #Iterate through all its neighbours
        negC = random.random() #Create some weight, the random is for random weights
        if negC <= 0.7:
          wmatrix[node][neighbour] = weight
        else:
          wmatrix[node][neighbour] = (weight)
    return wmatrix #Return weight matrix

  def getHit(self, G, gene_i, field):
    """
    计算基因在t时间点的H值
    i - 基因编号
    t - 时间点

    Calculate the H value for gene i at time t
    i - Gene number
    t - timestep
    """
    hit = 0 #set the H_{i,t} variable (h for node i at time t)
    for neighbour in G.neighbors(gene_i): #Iterate through all neighbours of gene i
      phit = self.matrix[gene_i][neighbour] * self.state(G, neighbour) #The hit value to plus at this point in time is the weight times the state of the neighbour
      hit += phit #hit it the sum of these values
    hit += field #add a field constant
    return hit #return hit for node i at time t

  def probability(self, G, gene, hit, field):
    """
    计算基因开关状态概率
    gene - 基因编号
    hit - 计算出来的H值(H_{i,t})

    Get the probability of a specific gene being on
    gene - gene number
    hit - the calculated H value (H_{i,t})
    """
    p = (1/(1+math.exp(-(self.getHit(G, gene, field))))) #The probability of a gene being on
    return p

  def change_state(self, G, field):
    """
    更新基因状态
    G - 基因图

    Update Gene state
    G - Graph
    """
    for node in G: #iterate through all nodes to update them all
      hit = self.getHit(G, node, field) #Get the hit value for a node
      p = self.probability(G, node, hit, field) #get the probability of a node being on
      chance = random.random()
      if chance <= p: #change the node state if the random value is less than the proposed probability
        G.nodes[node]["state"] = 1
      elif self.type_state == 'binary': #If the system is in Binary, the node is off at 0
        G.nodes[node]["state"] = 0
      else:
        G.nodes[node]["state"] = -1 #If the system is in Spins, the node is off at -1

  def state(self, G, node): #Return the state of a node
    state = G.nodes[node]["state"]
    return state

  def update(self, size, G, timesteps, field):
    """
    更新timesteps次模型
    size - 模型大小
    G - 模型图
    timesteps - 更新模型次数

    Update the model 'timesteps' times
    size - model size
    G - Model Graph
    """
    print("================================================================")
    print(f"Received Input graph of size", size)
    print(f"Running update for ", timesteps)
    print("================================================================")
    time = [] #timesteps - x axis of the state progression plot
    states_mean = []
    list_states = []
    print("Starting timestep 0")
    for t in range(0, timesteps+1): #While below the set timestep
      if t%1000 == 0:
        print(f"Timestep", t)
      time.append(t) #add timestep to list to plot later
      states = [] #add a temp list to store the list of states
      for node in G.nodes: #iterate through the nodes
        s = self.state(G, node) #get the state of current node
        states.append(s) #add the state to the list
      list_states.append(states) #add the states to the list of states
      sums = sum(states) #get the sum of all states
      sum_index = sums/size #Get the mean state (sum of states/number of nodes)
      states_mean.append(sum_index) #add this value to a list to plot with time
      self.change_state(G, field) #Update state
    return time, states_mean, list_states #return timestep, and the list of states

  def show_plot(self, time, states_mean):
    """
    画出模型平均值

    Plot the mean state of the model
    """
    print("================================================================")
    print("Generating Plot")
    print("================================================================")
    if self.type_state == 'binary':
      plt.ylim([0, 1]) #Set y axis range
    else:
      plt.ylim([-1, 1]) #Set y axis range
    plt.xlim([0, len(time)]) #Set x axis range
    plt.rcParams["figure.figsize"] = [17.50, 5.50] #Set figure size (visually)
    plt.plot(time, states_mean, 'r*') #Plot
    plt.show() #Show
