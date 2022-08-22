import re
import abc
from sys import argv, platform
from os.path import exists, getmtime

default_targets = []
silent = False

# this is the suite of abstract recipies
recipies = [] 

def report_status(target, status):
  indicators = {
    "uptodate": "-",
    "building": "+",
    "static":   "s",
  }
  
  indicator = indicators[status] if status in indicators else "?"
  
  if status=="uptodate":
    print("STATUS %s %s" % (indicator, target))

class Recipe:
  pattern = re.compile("")
  
  def __init__ (self, target):
    self.target = target
    self.children = []
  
  def add_child (self, child):
    self.children.append(child)
  
  def build_linux(self):
    raise Exception("Recipe '%s' has not been defined for platform '%s'." % (str(__class__), platform))
  def build_windows(self):
    raise Exception("Recipe '%s' has not been defined for platform '%s'." % (str(__class__), platform))
  
  def uptodate (self):
    # guard: target does not exist
    if not exists(self.target): return False
    
    target_timestamp = getmtime(self.target)
    depends = list(map(lambda child: getmtime(child.target), self.children))
    depend_timestamp = max(depends) if len(depends)>0 else target_timestamp
    return target_timestamp > depend_timestamp
  
  def build (self):
    for child in self.children:
      status = child.build()
      if status=="error": return status
    
    if self.uptodate():
      report_status(self.target, "uptodate")
      return "old"
    
    report_status(self.target, "building")
    if platform=="linux":
      return self.build_linux()
    elif platform=="win32":
      return self.build_windows()
    else:
      raise Exception("Unknown platform '%s' in recipie '%s'." % (platform, str(__class__)))
    return "error"
  
  @abc.abstractmethod
  def extract_deps (self, mo):
    return []
  
  def print (self, indent=""):
    if not silent:
      print("%s- %s \"%s\"" % (indent, str(type(self)), self.target))
    for child in self.children:
      child.print(indent+"  ")

class RecipeFile(Recipe):
  pattern = re.compile("(.+)")
  
  def extract_deps (self, mo):
    return []
  
  def build (self):
    report_status(self.target, "static")

#################################################################################
######################################################################### helpers

def resolve (target, ttl=128):
  if ttl==0: return None
#  print("resolve(\"%s\")" % target)
  for recipe in recipies:
    mo = recipe.pattern.match(target)
    if mo==None: continue
    
    node = recipe(target)
    deps = node.extract_deps(mo)
    missing = False
    for dep in deps:
      child = resolve(dep, ttl-1)
      if child==None:
        missing = True
        break
      node.add_child(child)
    if missing: continue
    
    return node
  
  # guard: target is an existing file
  if exists(target):
    return RecipeFile(target)
  
  return None

def build (target):
  node = resolve(target)
  if node==None: return None
#  print("Node to build: "+str(node)+" '"+node.target+"' with children "+str(node.children[0].target))
  node.print()
  status = node.build()
  if status=="error":
    print("Error: Failed to build '%s'." % target)

#################################################################################
####################################################################### interface

def add_recipe (classdef):
  recipies.append(classdef)

def set_default (default):
  global default_targets
  if type(default)==str:
    default = [default]
  default_targets = default

def main ():
  targets = argv[1:] if len(argv)>1 else default_targets
  
  # guard
  if len(targets)==0:
    print("No targets to build")
    return
  
#  print(recipies)
  for target in targets:
    build(target)
  

