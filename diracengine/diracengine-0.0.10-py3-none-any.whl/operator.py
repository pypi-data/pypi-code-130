import diracengine.constant as constant

class Operator:
    
    def __init__(self, operator = []):
        
        if isinstance(operator, str):
            
            self.isMatrix = False
            self.isComposed = False
            self.matrix = None
            self.composition = []
            self.factor = None
            self.type = operator
        
        elif isinstance(operator, ComplexMatrix):
    
            self.isMatrix = True
            self.isComposed = False
            self.matrix = operator
            self.composition = []
            self.factor = None
            self.type = 'matrix'
        
        elif isinstance(operator, Complex):
            
            self.isMatrix = False
            self.isComposed = False
            self.matrix = None
            self.composition = []
            self.factor = operator
            self.type = 'factor'
        
        elif isinstance(operator, list):
            
            if all(isinstance(element, Operator) for element in operator):
                self.isMatrix = False
                self.isComposed = True
                self.matrix = None
                self.composition = operator
                self.factor = None
                self.type = 'composed'
            else: raise TypeError()
            
        else: raise AttributeError()
        
    def scale(self, factor: Complex):
        
        if self.isMatrix: return Operator(self.matrix.scale(factor))
        else: raise TypeError()
        
    def specialize(self, type):
        
        self.type = type
        return self

pauliXMatrix = ComplexMatrix([ [complex.zero, complex.one], [complex.one, complex.zero] ])
pauliYMatrix = ComplexMatrix([ [complex.zero, complex.i], [-complex.i, complex.zero] ])
pauliZMatrix = ComplexMatrix([ [complex.one, complex.zero], [complex.zero, -complex.one] ])

pauliX = Operator(pauliXMatrix)
pauliY = Operator(pauliYMatrix)
pauliZ = Operator(pauliZMatrix)

spinX = pauliX.scale(constant.halfhbar)
spinY = pauliY.scale(constant.halfhbar)
spinZ = pauliZ.scale(constant.halfhbar)

hadamardMatrix = ComplexMatrix([ [complex.one, complex.one], [complex.one, -complex.one] ]).scale(complex.roothalf)
hadamard = Operator(hadamardMatrix)

position = Operator('position')

xDerivative = Operator('d/dx')
xSecondDerivative = Operator('d2/dx2')

def momentum():
    
    operator = Operator([xDerivative, Operator(-constant.ihbar)])
    operator.specialize('momentum')
    return operator

def momentumSquared():
    
    operator = Operator([xSecondDerivative, Operator(-constant.hbarSquared)])
    operator.specialize('momentum squared')
    return operator

def kinetic(mass: float):
    
    operator = Operator([momentum(), momentum(), Operator(complex.half / complex.ToComplex(mass))])
    operator.specialize('kenetic')
    return operator

def potential(potentialField: list):
    
    potentialField = [ complex.ToComplex(potentialValue) for potentialValue in potentialField ]
    potentialField = complexmatrix.diagonal(potentialField)
    operator = Operator(potentialField)
    operator.specialize('potential')
    return operator

def comutator(leftOperator: Operator, rightOperator: Operator):
    
    if leftOperator.isMatrix and rightOperator.isMatrix:
        
        comutatorMatrix = (leftOperator.matrix @ rightOperator.matrix) - (rightOperator.matrix @ leftOperator.matrix)
        return Operator(comutatorMatrix)
    
    elif leftOperator.type == 'position' and rightOperator.type == 'momentum': return complex.i * constant.hbar
    
    elif leftOperator.type == 'momentum' and rightOperator.type == 'position': return -complex.i * constant.hbar
    
    else: raise AttributeError()
    
def anticomutator(leftOperator: Operator, rightOperator: Operator):
    
    if leftOperator.isMatrix and rightOperator.isMatrix:
        
        comutatorMatrix = (leftOperator.matrix @ rightOperator.matrix) + (rightOperator.matrix @ leftOperator.matrix)
        return Operator(comutatorMatrix)
    
    else: raise AttributeError()