from .objs import Data


class Tree(object):
	def __init__(self, name,obj=None,children=None,parent=None):
		super(Tree, self).__init__()
		self.name  = name
		#self.obj = obj
		self.data = Data({"name":name,"obj":obj},name)
		if children:
			self.children = children
		else:
			self.children = []
		if parent:
			parent.children.append(self)
	def sorted(self,**kw):
		st = sorted(self.children,key = lambda x: x.name)
		if kw.get("change",True): self.children = st
		return self.children
	def append(self,item):
		self.children.append(item)
	def remove(self,item):
		self.children.remove(item)
	def __repr__(self):
		obj = ("\""+(self.data.data["obj"])+"\"" if isinstance(self.data.data["obj"],str) else (self.data.data["obj"]))
		return ("<Tree(data(name=\"%s\",obj=%s),children=%s)>" % (self.data.data["name"],obj,self.children))

class Remove(object):
	def __init__(self,tree,name):
		self.name = name
		self.tree = tree
	def removeIt(self):
		if self.tree.children == []:
			raise TypeError(f"can't reomve child with an empty tree : {self.tree}")
		children = self.tree.children
		for child_ind in range(len(children)):
			child = children[child_ind]
			if child.name == self.name:
				del children[child_ind]
				return
