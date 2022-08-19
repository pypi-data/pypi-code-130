import sys
sys.path.insert(0,r'.\src')
import powerfactorypy

class PFCaseStudy(powerfactorypy.PFBaseInterface):

  def __init__(self,app):
    super().__init__(app) 

