
class treeRander(object):
	"""docstring for treeRander"""
	def __init__(self,printIt=False):
		super(treeRander, self).__init__()
		self.string = ""
		self.fullstring = ""
		self._display = None
		self.printIt = printIt
	def displayTree(self,tree, indent_width=4):
		def _display(parent, tree, indent=""):
			if parent.children == []:
				self._print(parent.name)
			else:
				tree = parent
				self._print(tree.name)
				for child in range(len(tree.children[:])):
					if len(tree.children)-1 != child:
						child = tree.children[child]
						self._print(indent + "├" + "─" * indent_width, end="")
						_display(child, tree, indent + "│" + " " * 4)
					else:
						child = tree.children[child]
						self._print(indent + "└" + "─" * indent_width, end="")
						_display(child, tree, indent + " " * 5)
			return
		parent = tree
		_display(parent, tree)
		if self._display is not None: self._display = _display
		return self.string

	def displayTree(self,tree, indent_width=4):
		def _display(parent, tree, indent=""):
			if parent.children == []:
				self._print(parent.name)
			else:
				tree = parent
				self._print(tree.name)
				for child in range(len(tree.children[:])):
					if len(tree.children)-1 != child:
						child = tree.children[child]
						self._print(indent + "├" + "─" * indent_width, end="")
						_display(child, tree, indent + "│" + " " * 4)
					else:
						child = tree.children[child]
						self._print(indent + "└" + "─" * indent_width, end="")
						_display(child, tree, indent + " " * 5)
			return
		parent = tree
		_display(parent, tree)
		if self._display is None: self._display = _display
		return self.string
	def displayTree_OBJ(self,tree, indent_width=4):
		def _display(parent, tree, indent=""):
			if parent.children == []:
				self._print(parent)
			else:
				tree = parent
				self._print(tree)
				for child in range(len(tree.children[:])):
					if len(tree.children)-1 != child:
						child = tree.children[child]
						self._print(indent + "├" + "─" * indent_width, end="")
						_display(child, tree, indent + "│" + " " * 4)
					else:
						child = tree.children[child]
						self._print(indent + "└" + "─" * indent_width, end="")
						_display(child, tree, indent + " " * 5)
			return
		parent = tree
		_display(parent, tree)
		return self.string
	def clear(self):
		self.string = ""
	def _print(self,string,end="\n"):
		if self.printIt: print(str(string),end=end)
		self.string += str(string)+end
		return string
	def PrintIT(root,indent=2):
		TR = treeRander(True)
		return TR.displayTree(root,2)

