import anytree
import pandas as pd
from anytree import RenderTree
pd.set_option('display.max_columns', None)

class Node(anytree.Node):
    '''
    THIS EXPANDS THE NODE CLASS IN THE ANYTREE LUBRARY WITH THE FOLLOWING FUNCTIONALITY:
    adding: node1 + node2 will calculate the union sets and return a tuple with the resulting (sensor_ids,sensor_names)
    subtracting: node1 - node2 will return a tuple of the (sensor_ids, sensor_names) in node1 so long as they dont appear in node2
    render: node.render() will perform a basic rendering of such node, all the way downwards
    '''
    def __add__(self,other):
        sensor_ids=self.sensor_ids.copy()
        sensor_names=self.sensor_names.copy()
        for sensor_id, sensor_name in zip(other.sensor_ids,other.sensor_names):
            if not(sensor_id in sensor_ids):
                sensor_ids+=[sensor_id]
                sensor_names+=[sensor_name]
        return sensor_ids,sensor_names

    def __sub__(self, other):
        sensor_ids=[]
        sensor_names=[]
        for sensor_id,sensor_name in zip(self.sensor_ids,self.sensor_names):
            #print(sensor_id,other.sensor_ids,~(sensor_id in other.sensor_ids))
            if not(sensor_id in other.sensor_ids):
                sensor_ids+=[sensor_id]
                sensor_names+=[sensor_name]

        return sensor_ids,sensor_names

    def render(self):
        for pre, _, node in RenderTree(self):
            print("%s%s" % (pre, node.name))



def create_tree(configuration_df,levels,initial_depth,add_sensor_names=False):
    '''
    :param configuration_df: a df containing sensor names and ids plus whatever fields we deem appropriate for accordion classification. Must have the columns sensor_name and asset_id
    :param levels: a list with the names of the grouping columns we want to generate the tree from, eg levels=["building","group","level_01","level_02","level_03"]
    :param initial_depth: the level we want to start the tree at (e.g. in the example above depth=0 starts with "building"
    :param add_sensor_names: if True, it will add sensor name and ID at the end of each node
    :return: a list of the root Nodes of the tree
    '''
    global id
    id = 0
    global return_nodes
    return_nodes=[]
    def __recursive_tree(df,levels,initial_depth,parent=None,add_sensor_names=False):
        global id
        depth=initial_depth
        level=levels[0:depth+1]
        idx = df.groupby(level,dropna=True).indices
        if (len(idx)==0) and (add_sensor_names==True):
            for sensor_name, sensor_id in zip(parent.sensor_names,parent.sensor_ids):
                id=id+1
                sensor_node = Node(name=sensor_name+" - "+str(sensor_id),parent=parent)
                exec("global ID"+str(id)+";ID"+str(id)+"=sensor_node")
            # print(parent.sensor_names)
            # print(id)

        for item in idx:
            if type(item)==str:
                new_node=item
            else:
                new_node=item[-1]
            new_df=df[df[levels[depth]]==new_node]
            node = Node(new_node,
                        parent=parent,
                        sensor_names=list(new_df["sensor_name"]),
                        sensor_ids=list(new_df["asset_id"]))
            exec("global ID"+str(id)+";ID"+str(id)+"=node")
            if parent==None:
                exec("global ID"+str(id)+";return_nodes+=[ID"+str(id)+"]")

            id=id+1
            if (depth+1)<len(levels):
                __recursive_tree(df=new_df,levels=levels,initial_depth=depth+1,parent=node,add_sensor_names=add_sensor_names)

    __recursive_tree(df=configuration_df,levels=levels,initial_depth=initial_depth,parent=None,add_sensor_names=add_sensor_names)
    return return_nodes

