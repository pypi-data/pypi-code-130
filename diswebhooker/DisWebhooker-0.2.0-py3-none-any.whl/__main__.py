#def find_func(name):
def decter(*args,**kw):
    def inner(func):
        return lambda: func(*args,**kw)
    return inner

@decter(name="test")
def foo(*args,**kw):
    print("Hello foo:"+kw.get("name","no name"))
foo()
# or
def decter(*args,**kw):
	print(kw)
	print(args)
	def inner(func):
		print("inner been called",func)
		def _():
			print("_ been called",(args,kw))
			return func(*args,**kw)
		return _
	return inner

@decter(name="test")
def foo(*args,**kw):
	print(args,kw)
	print("Hello foo:"+kw.get("name","no name"))
foo()
#(name="name")

#_vars_ = {"arg":stuff,"kw":stuff}



"""
from mkrTree import *
if __name__ == '__main__':


	root = Tree("root")
	left = Tree("left")
	middle = Tree("middle")
	right = Tree("right")
	trees = Tree("trees")
	tree0 = Tree("tree0",children=[Tree("1"),Tree("2"),Tree("3"),Tree("4"),Tree("5")])
	tree1 = Tree("tree1",children=[Tree("A",children=[Tree("a")]),Tree("B",children=[Tree("b")]),Tree("C",children=[Tree("c")])])
	tree2 = Tree("tree2",children=[Tree("T",True),Tree("F",False),Tree("N")])
	trees.children = [tree0,tree1,tree2]
	root.children = [trees,left, middle, right]
	print(" displayTree ".center(30,"#"))
	TR = treeRander(True).displayTree(root)
	print(" sorted ".center(30,"#"))
	r = Tree("r",children=[Tree("A",children=[Tree("a")]),Tree("C",children=[Tree("c")]),Tree("B",children=[Tree("b")])])
	TR = treeRander(True).displayTree(r)
	print(r.sorted(change=True))
	TR = treeRander(True).displayTree(r)
"""