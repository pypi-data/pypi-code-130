def program_code(number):
    
    if number==1:
        return('''
        import numpy as np 
        import pandas as pd

        def astartalgo(start_node,stop_node):
                open_set = set(start_node) 
                closed_set = set()
                g = {} 
                parents = {}# parents contains an adjacency map of all nodes
        
                #ditance of starting node from itself is zero
                g[start_node] = 0
                #start_node is root node i.e it has no parent nodes
                #so start_node is set to its own parent node
                parents[start_node] = start_node
                
                
                while len(open_set) > 0:
                    n = None
        
                    #node with lowest f() is found
                    for v in open_set:
                        if n == None or g[v] + heuristic(v) < g[n] + heuristic(n):
                            n = v
                    
                            
                    if n == stop_node or Graph_nodes[n] == None:
                        pass
                    else:
                        for (m, weight) in get_neighbors(n):
                        #nodes 'm' not in first and last set are added to first
                            #n is set its parent
                            if m not in open_set and m not in closed_set:
                                open_set.add(m)
                                parents[m] = n
                                g[m] = g[n] + weight
                                
            
                            #for each node m,compare its distance from start i.e g(m) to the
                            #from start through n node
                            else:
                                if g[m] > g[n] + weight:
                                    #update g(m)
                                    g[m] = g[n] + weight
                                    #change parent of m to n
                                    parents[m] = n
                                    
                                    #if m in closed set,remove and add to open
                                    if m in closed_set:
                                        closed_set.remove(m)
                                        open_set.add(m)
        
                    if n == None:
                        print('Path does not exist!')
                        return None
        
                    # if the current node is the stop_node
                    # then we begin reconstructin the path from it to the start_node
                    if n == stop_node:
                        path = []
        
                        while parents[n] != n:
                            path.append(n)
                            n = parents[n]
        
                        path.append(start_node)
        
                        path.reverse()
        
                        print('Path found: {}'.format(path))
                        return path
        
        
                    # remove n from the open_list, and add it to closed_list
                    # because all of his neighbors were inspected
                    open_set.remove(n)
                    closed_set.add(n)
        
                print('Path does not exist!')
                return None
                
        #define fuction to return neighbor and its distance
        #from the passed node
        def get_neighbors(v):
            if v in Graph_nodes:
                return Graph_nodes[v]
            else:
                return None
        #for simplicity we ll consider heuristic distances given
        #and this function returns heuristic distance for all nodes
        def heuristic(n):
                H_dist = {
                    'A': 11,
                    'B': 6,
                    'C': 99,
                    'D': 1,
                    'E': 7,
                    'G':0
                    
                }
        
                return H_dist[n]
        
        #Describe your graph here  
        Graph_nodes = {
            'A': [('B', 2), ('E', 3)],
            'B': [('C', 99),('G',9)],
            'C':[None],
            'D': [('G', 1)],
            'E': [('D', 6)],
        
        }
        astartalgo('A', 'C')''')
    
    elif number==2:
        return('''class Graph:
    def __init__(self, graph, heuristicNodeList, startNode): #instantiate graph object with graph topology, heuristic values, start node

        self.graph = graph
        self.H=heuristicNodeList
        self.start=startNode
        self.parent={}
        self.status={}
        self.solutionGraph={}

    def applyAOStar(self): # starts a recursive AO* algorithm
        self.aoStar(self.start, False)

    def getNeighbors(self, v): # gets the Neighbors of a given node
        return self.graph.get(v,'')

    def getStatus(self,v): # return the status of a given node
        return self.status.get(v,0)

    def setStatus(self,v, val): # set the status of a given node
        self.status[v]=val

    def getHeuristicNodeValue(self, n):
        return self.H.get(n,0) # always return the heuristic value of a given node

    def setHeuristicNodeValue(self, n, value):
        self.H[n]=value # set the revised heuristic value of a given node


    def printSolution(self):
        print("FOR GRAPH SOLUTION, TRAVERSE THE GRAPH FROM THE STARTNODE:",self.start)
        print("------------------------------------------------------------")
        print(self.solutionGraph)
        print("------------------------------------------------------------")

    def computeMinimumCostChildNodes(self, v): # Computes the Minimum Cost of child nodes of a given node v
        minimumCost=0
        costToChildNodeListDict={}
        costToChildNodeListDict[minimumCost]=[]
        flag=True
        for nodeInfoTupleList in self.getNeighbors(v): # iterate over all the set of child node/s
            cost=0
            nodeList=[]
            for c, weight in nodeInfoTupleList:
                cost=cost+self.getHeuristicNodeValue(c)+weight
                nodeList.append(c)
        
            if flag==True: # initialize Minimum Cost with the cost of first set of child node/s
                minimumCost=cost
                costToChildNodeListDict[minimumCost]=nodeList # set the Minimum Cost child node/s
                flag=False
            else: # checking the Minimum Cost nodes with the current Minimum Cost
                if minimumCost>cost:
                    minimumCost=cost
                    costToChildNodeListDict[minimumCost]=nodeList # set the Minimum Cost child node/s


        return minimumCost, costToChildNodeListDict[minimumCost] # return Minimum Cost and Minimum Cost child node/s


    def aoStar(self, v, backTracking): # AO* algorithm for a start node and backTracking status flag

        print("HEURISTIC VALUES :", self.H)
        print("SOLUTION GRAPH :", self.solutionGraph)
        print("PROCESSING NODE :", v)

        print("-----------------------------------------------------------------------------------------")
    
        if self.getStatus(v) >= 0: # if status node v >= 0, compute Minimum Cost nodes of v
            minimumCost, childNodeList = self.computeMinimumCostChildNodes(v)
            self.setHeuristicNodeValue(v, minimumCost)
            self.setStatus(v,len(childNodeList))

            solved=True # check the Minimum Cost nodes of v are solved
        
            for childNode in childNodeList:
                self.parent[childNode]=v
                if self.getStatus(childNode)!=-1:
                    solved=solved & False

            if solved==True: # if the Minimum Cost nodes of v are solved, set the current node status as solved(-1)
                self.setStatus(v,-1)
                self.solutionGraph[v]=childNodeList # update the solution graph with the solved nodes which may be a part of solution


            if v!=self.start: # check the current node is the start node for backtracking the current node value
                self.aoStar(self.parent[v], True) # backtracking the current node value with backtracking status set to true

            if backTracking==False: # check the current call is not for backtracking
                for childNode in childNodeList: # for each Minimum Cost child node
                    self.setStatus(childNode,0) # set the status of child node to 0(needs exploration)
                    self.aoStar(childNode, False) # Minimum Cost child node is further explored with backtracking status as false



h1 = {'A': 1, 'B': 6, 'C': 2, 'D': 12, 'E': 2, 'F': 1, 'G': 5, 'H': 7, 'I': 7, 'J':1, 'T': 3}
graph1 = {
    'A': [[('B', 1), ('C', 1)], [('D', 1)]],
    'B': [[('G', 1)], [('H', 1)]],
    'C': [[('J', 1)]],
    'D': [[('E', 1), ('F', 1)]],
    'G': [[('I', 1)]]
}
G1= Graph(graph1, h1, 'A')
G1.applyAOStar()
G1.printSolution()

h2 = {'A': 1, 'B': 6, 'C': 12, 'D': 10, 'E': 4, 'F': 4, 'G': 5, 'H': 7} # Heuristic values of Nodes
graph2 = { # Graph of Nodes and Edges
    'A': [[('B', 1), ('C', 1)], [('D', 1)]], # Neighbors of Node 'A', B, C & D with repective weights
    'B': [[('G', 1)], [('H', 1)]], # Neighbors are included in a list of lists
    'D': [[('E', 1), ('F', 1)]] # Each sublist indicate a "OR" node or "AND" nodes
}

G2 = Graph(graph2, h2, 'A') # Instantiate Graph object with graph, heuristic values and start Node
G2.applyAOStar() # Run the AO* algorithm
G2.printSolution() # print the solution graph as AO* Algorithm search''')
    
    elif number==3:
        return('''
        import numpy as np 
        import pandas as pd

        data = pd.read_csv('enjoysport.csv')
        concepts = np.array(data.iloc[:,0:-1])
        print(concepts) 
        target = np.array(data.iloc[:,-1])  
        print(target)
        def learn(concepts, target): 
            specific_h = concepts[0].copy()     
            print("initialization of specific_h and general_h")     
            print(specific_h)  
            general_h = [["?" for i in range(len(specific_h))] for i in range(len(specific_h))]     
            print(general_h)  

            for i, h in enumerate(concepts):
                print("For Loop Starts")
                if target[i] == "yes":
                    print("If instance is Positive ")
                    for x in range(len(specific_h)): 
                        if h[x]!= specific_h[x]:                    
                            specific_h[x] ='?'                     
                            general_h[x][x] ='?'
                        
                if target[i] == "no":            
                    print("If instance is Negative ")
                    for x in range(len(specific_h)): 
                        if h[x]!= specific_h[x]:                    
                            general_h[x][x] = specific_h[x]                
                        else:                    
                            general_h[x][x] = '?'        

                print(" steps of Candidate Elimination Algorithm",i+1)        
                print(specific_h)         
                print(general_h)
                print("\n")
                print("\n")

            indices = [i for i, val in enumerate(general_h) if val == ['?', '?', '?', '?', '?', '?']]    
            for i in indices:   
                general_h.remove(['?', '?', '?', '?', '?', '?']) 
            return specific_h, general_h 

        s_final, g_final = learn(concepts, target)

        print("Final Specific_h:", s_final, sep="\n")
        print("Final General_h:", g_final, sep="\n")
        
        ''')

    elif number==4:
        return('''import pandas as pd
import math
import numpy as np

data = pd.read_csv("3-dataset.csv")
features = [feat for feat in data]
features.remove("answer")

class Node:
    def __init__(self):
        self.children = []
        self.value = ""
        self.isLeaf = False
        self.pred = ""

def entropy(examples):
    pos = 0.0
    neg = 0.0
    for _, row in examples.iterrows():
        if row["answer"] == "yes":
            pos += 1
        else:
            neg += 1
    if pos == 0.0 or neg == 0.0:
        return 0.0
    else:
        p = pos / (pos + neg)
        n = neg / (pos + neg)
        return -(p * math.log(p, 2) + n * math.log(n, 2))

def info_gain(examples, attr):
    uniq = np.unique(examples[attr])
    #print ("\n",uniq)
    gain = entropy(examples)
    #print ("\n",gain)
    for u in uniq:
        subdata = examples[examples[attr] == u]
        #print ("\n",subdata)
        sub_e = entropy(subdata)
        gain -= (float(len(subdata)) / float(len(examples))) * sub_e
        #print ("\n",gain)
    return gain

def ID3(examples, attrs):
    root = Node()

    max_gain = 0
    max_feat = ""
    for feature in attrs:
        #print ("\n",examples)
        gain = info_gain(examples, feature)
        if gain > max_gain:
            max_gain = gain
            max_feat = feature
    root.value = max_feat
    #print ("\nMax feature attr",max_feat)
    uniq = np.unique(examples[max_feat])
    #print ("\n",uniq)
    for u in uniq:
        #print ("\n",u)
        subdata = examples[examples[max_feat] == u]
        #print ("\n",subdata)
        if entropy(subdata) == 0.0:
            newNode = Node()
            newNode.isLeaf = True
            newNode.value = u
            newNode.pred = np.unique(subdata["answer"])
            root.children.append(newNode)
        else:
            dummyNode = Node()
            dummyNode.value = u
            new_attrs = attrs.copy()
            new_attrs.remove(max_feat)
            child = ID3(subdata, new_attrs)
            dummyNode.children.append(child)
            root.children.append(dummyNode)
    return root

def printTree(root: Node, depth=0):
    for i in range(depth):
        print("\t", end="")
    print(root.value, end="")
    if root.isLeaf:
        print(" -> ", root.pred)
    print()
    for child in root.children:
        printTree(child, depth + 1)

root = ID3(data, features)
printTree(root)
''')

    elif number==5:
        return('''
        X = np.array(([2, 9], [1, 5], [3, 6]), dtype=float)
        y = np.array(([92], [86], [89]), dtype=float)
        X = X/np.amax(X,axis=0) # maximum of X array longitudinally
        y = y/100

        #Sigmoid Function
        def sigmoid (x):
            return 1/(1 + np.exp(-x))

        #Derivative of Sigmoid Function
        def derivatives_sigmoid(x):
            return x * (1 - x)

        #Variable initialization
        epoch=5000 	#Setting training iterations
        lr=0.1 		#Setting learning rate
        inputlayer_neurons = 2 		#number of features in data set
        hiddenlayer_neurons = 3 	#number of hidden layers neurons
        output_neurons = 1 		#number of neurons at output layer

        #weight and bias initialization
        wh=np.random.uniform(size=(inputlayer_neurons,hiddenlayer_neurons))
        bh=np.random.uniform(size=(1,hiddenlayer_neurons))
        wout=np.random.uniform(size=(hiddenlayer_neurons,output_neurons))
        bout=np.random.uniform(size=(1,output_neurons))


        #draws a random range of numbers uniformly of dim x*y
        for i in range(epoch):

        #Forward Propogation
            hinp1=np.dot(X,wh)
            hinp=hinp1 + bh
            hlayer_act = sigmoid(hinp)
            outinp1=np.dot(hlayer_act,wout)
            outinp= outinp1+ bout
            output = sigmoid(outinp)

        #Backpropagation
            EO = y-output
            outgrad = derivatives_sigmoid(output)
            d_output = EO* outgrad
            EH = d_output.dot(wout.T)

        #how much hidden layer wts contributed to error
            hiddengrad = derivatives_sigmoid(hlayer_act)
            d_hiddenlayer = EH * hiddengrad

        # dotproduct of nextlayererror and currentlayerop
        wout += hlayer_act.T.dot(d_output) *lr
        wh += X.T.dot(d_hiddenlayer) *lr

        print("Input: \n" + str(X)) 
        print("Actual Output: \n" + str(y))
        print("Predicted Output: \n" ,output)
        ''')

    elif number==6:
        return('''
        import pandas as pd

        PlayTennis = pd.read_csv("4.csv")
        print("Given dataset:\n", PlayTennis,"\n")

        from sklearn.preprocessing import LabelEncoder
        Le = LabelEncoder()

        PlayTennis['outlook'] = Le.fit_transform(PlayTennis['outlook'])
        PlayTennis['temp'] = Le.fit_transform(PlayTennis['temp'])
        PlayTennis['humidity'] = Le.fit_transform(PlayTennis['humidity'])
        PlayTennis['wind'] = Le.fit_transform(PlayTennis['wind'])
        PlayTennis['play'] = Le.fit_transform(PlayTennis['play'])

        print("the encoded dataset is:\n",PlayTennis)

        X = PlayTennis.drop(['play'],axis=1) 
        y = PlayTennis['play']              

        from sklearn.model_selection import train_test_split
        from sklearn.naive_bayes import GaussianNB
        from sklearn.metrics import accuracy_score

        X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.20)
        print("\n X_train:\n",X_train)
        print("\n y_train:\n",y_train)
        print("\n X_test:\n",X_test)
        print("\n y_test:\n",y_test)

        classifier = GaussianNB()
        classifier.fit(X_train,y_train)

        accuracy = accuracy_score(classifier.predict(X_test),y_test)
        print("\n Accuracy is:",accuracy)
        ''')
    
    elif number==7:
        return('''
        import matplotlib.pyplot as plt
        from sklearn import datasets
        from sklearn.cluster import KMeans
        import sklearn.metrics as sm

        from sklearn import preprocessing 
        from sklearn.mixture import GaussianMixture

        import pandas as pd
        import numpy as np

        iris = datasets.load_iris()

        X = pd.DataFrame(iris.data)
        X.columns = ['Sepal_Length','Sepal_Width','Petal_Length','Petal_Width']

        y = pd.DataFrame(iris.target)
        y.columns = ['Targets']


        model = KMeans(n_clusters=3)
        model.fit(X) 
        score1=sm.accuracy_score(y, model.labels_)
        print("Accuracy of KMeans=",score1)

        plt.figure(figsize=(7,7))
        colormap = np.array(['red', 'lime', 'black'])
        plt.subplot(1, 2, 1) 
        plt.scatter(X.Petal_Length, X.Petal_Width, c=colormap[model.labels_], s=40)
        plt.title('K Mean Classification')

        scaler = preprocessing.StandardScaler()
        scaler.fit(X)
        xsa = scaler.transform(X)
        xs = pd.DataFrame(xsa, columns = X.columns)
        gmm = GaussianMixture(n_components=3)
        gmm.fit(xs)                   
        y_cluster_gmm = gmm.predict(xs)     
        score2=sm.accuracy_score(y, y_cluster_gmm)
        print("Accuracy of EM=",score2)
        plt.subplot(1, 2, 2)
        plt.scatter(X.Petal_Length, X.Petal_Width, c=colormap[y_cluster_gmm], s=40)
        plt.title('EM Classification')
        ''')

    elif number==8:
        return('''
        from sklearn.model_selection import train_test_split
        from sklearn.neighbors import KNeighborsClassifier
        from sklearn.metrics import classification_report, confusion_matrix
        from sklearn import datasets

        """
        Iris Plants Dataset, dataset contains 150 (50 in each of three classes)
        Number of Attributes: 4 numeric, predictive attributes and the Class
        """
        iris=datasets.load_iris()

        """ 
        The x variable contains the first four columns of the dataset 
        (i.e. attributes) while y contains the labels.
        """
        x = iris.data
        y = iris.target
        print ('sepal-length', 'sepal-width', 'petal-length', 'petal-width')
        print(x)
        print('class: 0-Iris-Setosa, 1- Iris-Versicolour, 2- Iris-Virginica')
        print(y)

        """ splits the dataset into 70% train data and 30% test data. This means that 
        out of total 150 records,the training set will contain 105 records and 
        the test set contains 45 of those records """
        x_train, x_test, y_train, y_test = train_test_split(x,y,test_size=0.3)

        #to Training the model and Nearest nighbors K=5
        classifier = KNeighborsClassifier(n_neighbors=5)
        classifier.fit(x_train, y_train)

        #to make predictions on our test data
        y_pred=classifier.predict(x_test)

        """ For evaluating an algorithm, confusion matrix, precision, recall and 
        f1 score are the most commonly used metrics."""
        print('Confusion Matrix')
        print(confusion_matrix(y_test,y_pred))
        print('Accuracy Metrics')
        print(classification_report(y_test,y_pred))
        ''')

    elif number==9:
        return('''
        import matplotlib.pyplot as plt

        from scipy.interpolate import interp1d

        import statsmodels.api as sm

        x=[i/5.0 for i in range(30)]

        y = [1,2,1,2,1,1,3,4,5,4,5,6,5,6,7,8,9,10,11,11,12,11,11,10,12,11,11,10,9,13]

        lowess = sm.nonparametric.lowess(y, x)
        lowess_x = list(zip(*lowess))[0]

        lowess_y= list(zip(*lowess))[1]
        f = interp1d(lowess_x, lowess_y, bounds_error=False)

        xnew = [i/10.0 for i in range(100)]

        ynew = f(xnew)

        plt.plot(x,y,'o')

        plt.plot(lowess_x, lowess_y, '+')

        plt.plot(xnew, ynew, '-')

        plt.show()
        ''')
    else:
        return("INVALID")