import numpy
from scipy.sparse.linalg import eigsh

import diracengine.constant as constant
from diracengine.state import QuantumState

class Operator:
    
    def __init__(self, operator: numpy.ndarray = numpy.ndarray([ ]), **kwargs):
        
        """
        Initiate a quantum operator
        """
        
        self.matrix = operator + 0j
        self.type = kwargs.get('type', 'matrix')
        self.meshbasis = kwargs.get('meshbasis', None)
    
    def __repr__(self): return f'< operator : {self.type} : {self.matrix} >'
    
    def __str__(self): return str(self.matrix)
    
    def __len__(self): return self.matrix.shape[0]
    
    def __add__(left, right):
        
        if isinstance(right, (complex, float, int)): return Operator(left.matrix + numpy.full(len(left), right))
        elif isinstance(right, Operator): return Operator(left.matrix + right.matrix)
        else: TypeError()
        
    def __radd__(right, left):
        
        if isinstance(left, (complex, float, int)): return Operator(right.matrix + numpy.full(len(right), left))
        elif isinstance(left, Operator): return Operator(left.matrix + right.matrix)
        else: TypeError()
    
    def __neg__(self): return -1 * self
    
    def __sub__(left, right): return left + -right
    
    def __rsub__(right, left): return left + -right
    
    def __mul__(left, right):
        
        if isinstance(right, (complex, float, int)): return left.scale(right)
        elif isinstance(right, Operator): return Operator(left.matrix * right.matrix)
        else: TypeError()
            
    def __rmul__(right, left):
        
        if isinstance(left, (complex, float, int)): return right.scale(left)
        elif isinstance(left, Operator): return Operator(left.matrix * right.matrix)
        else: TypeError()
        
    def __matmul__(left, right):
        
        if isinstance(right, Operator): return Operator(left.matrix @ right.matrix)
        elif isinstance(right, QuantumState): return left.act(right)
        else: TypeError()
    
    def __eq__(left, right):
        
        if isinstance(right, Operator): return (left.matrix == right.matrix).all()
        else: TypeError()
    
    def __neg__(self): return -1 * self
    
    def scale(self, scalar: complex, **kwargs): return Operator(scalar * self.matrix, type = kwargs.get('type', 'matrix'))
    
    def act(self, state: QuantumState):
        
        newStateKet = self.matrix @ state.ket()
        
        return QuantumState(newStateKet.reshape(state.N), state.meshbasis, normalize = False)
    
    def determinant(self): return numpy.linalg.det(self.matrix)
    
    def det(self): return self.determinant()
    
    def inverse(self): return Operator(numpy.linalg.inv(self.matrix), type = self.type)
    
    def inv(self): return self.inverse()
    
    def conjugate(self): return Operator(self.matrix.conjugate(), type = self.type)
    
    def transpose(self): return Operator(self.matrix.T, type = self.type)
    
    def conjugateTranspose(self):
        
        """
        Return the conjugated transpose of the operator. This is
        equivalent to hermitian() and dagger() methods.
        Example: H => H†
        """
        
        return self.conjugate().transpose()
    
    def hermitian(self): return self.conjugateTranspose()
    
    def dagger(self): return self.conjugateTranspose()
    
    def hermitianSquare(self):
        
        """
        Return the conjugated transpose of the operator
        applied to the opeartor.
        Example: H† H
        """
        
        return self.conjugateTranspose() @ self
    
    def inverseHermitianSquare(self):
        
        """
        Return the operator applied to its conjugate transpose.
        Example: H H†
        """
        
        return self @ self.conjugateTranspose()
    
    def isOrthogonal(self): return self.transpose() == self.inverse()
    
    def isNormal(self): return self.hermitianSquare() == self.inverseHermitianSquare()
    
    def isUnitary(self): return self.isNormal() and self.inverse() @ self == self.hermitianSquare()
    
    def isSpecial(self): return self.determinant() == 1 + 0j
    
    def isAntiSpecial(self): return self.determinant() == -1 + 0j
    
    def isHermitian(self): return self == self.conjugateTranspose()
    
    def isAntiHermitian(self): return self == -self.conjugateTranspose()
    
    def isSkewHermitian(self): return self.isAntiHermitian()
    
    def group(self):
        
        groupName = ''
        
        if self.isSpecial(): groupName += 'S'
        elif self.isAntiSpecial(): groupName += '-S'
        
        if self.isOrthogonal(): groupName += 'O'
        elif self.isUnitary(): groupName += 'U'
        elif self.isNormal(): groupName += 'N'
        
        if groupName == '': groupName += '?'
            
        groupName += f'({len(self)})'
        
        return groupName
    
    def eigen(self):
        
        if isinstance(self.meshbasis, tuple):
            
            if len(self.meshbasis) == 2:
            
                X, Y = self.meshbasis
                basis = ( len(X), len(Y) )
                
                eigenValues, eigenVectors = numpy.linalg.eig(self.matrix)
                
                eigenVectors = eigenVectors.T
                
                eigenStates = [ QuantumState(state.reshape(basis), self.meshbasis) for state in eigenVectors ]
                
                return eigenValues, eigenStates
            
        else:
            
            eigenValues, eigenVectors = numpy.linalg.eig(self.matrix)
            
            eigenVectors = eigenVectors.T
                
            eigenStates = [ QuantumState(state, self.meshbasis) for state in eigenVectors ]
            
            return eigenValues, eigenStates
            
    
def comutator(left: Operator, right: Operator):
    
    """
    Calculate the commutator of two operators.
    Example: [A B] = AB - BA
    """
    
    return left @ right - right @ left
    
def anticomutator(left: Operator, right: Operator):
    
    """
    Calculate the anticommutator of two operators.
    Example: [A B] = AB + BA
    """
    
    return left @ right + right @ left

def kronecker(left: Operator, right: Operator): return Operator(numpy.kron(left.matrix, right.matrix))

def identity(numberOfBasis: int = 2):
    
    """
    Identity operator. By default it is a 2D identity.
    """
    
    return Operator(numpy.identity(numberOfBasis, dtype=complex))

def antiIdentity(numberOfBasis: int = 2): return Operator(numpy.identity(numberOfBasis, dtype=complex)[::-1])

def null(numberOfBasis: int = 2): return Operator(numpy.zeros((numberOfBasis, numberOfBasis), dtype=complex))

def diagonal(diagonalArray: numpy.ndarray, **kwargs):
    
    type = kwargs.get('type', 'diagonal')
    
    diagonalMatrix = numpy.diag(diagonalArray)
    operator = Operator(diagonalMatrix, type = type)
    return operator

def ddx(meshbasis):
    
    if isinstance(meshbasis, tuple):
        
        if len(meshbasis) == 2:

            X, Y = meshbasis
            
            return kronecker(identity(len(Y[0, :])), ddx(X[0, :]))
        
        if len(meshbasis) == 3: print('3D')
        
    else:
        
        N = len(meshbasis)
        
        dx = [ meshbasis[i + 1] - meshbasis[i - 1] for i in range(1, N - 1) ]
        dx = numpy.array([ dx[0] ] + dx + [ dx[-1] ]) + 0j

        diagPlus = numpy.full(N - 1, 1)
        diagMinus = numpy.full(N - 1, -1)
        
        matrix = numpy.diag(diagPlus, 1) + numpy.diag(diagMinus, -1) + 0j
        matrix /= dx
        
        return Operator(matrix, type = 'derivative', meshbasis = meshbasis)

def ddy(meshbasis): 
    
    if isinstance(meshbasis, tuple):
        
        if len(meshbasis) == 2:

            X, Y = meshbasis
            
            return kronecker(ddx(Y[:, 0]), identity(len(X[:, 0])))
        
        if len(meshbasis) == 3: print('3D')
        
    else: TypeError('meshbasis must be in 2D or 3D')

def gradient(meshbasis):
    
    if isinstance(meshbasis, tuple):

        if len(meshbasis) == 2: return ddx(meshbasis) + ddy(meshbasis)
        elif len(meshbasis) == 3: return ddx(meshbasis) + ddy(meshbasis) # + ddz(meshbasis)
    
    else: return ddx(meshbasis)

def laplacian(meshbasis): return gradient(meshbasis) @ gradient(meshbasis)

def momentum(meshbasis): return - 1j * constant.hbar * gradient(meshbasis)

def kinetic(meshbasis, mass: float): return .5 / mass * momentum(meshbasis) @ momentum(meshbasis)

def potential(meshbasis, potentialField: numpy.ndarray):
    
    if isinstance(meshbasis, tuple):
        
        if len(meshbasis) == 2:
            
            X, Y = meshbasis
            N = len(X) * len(Y)
            potentialField = potentialField.reshape(N)
            return diagonal(potentialField)
        
        elif len(meshbasis) == 3: print('3D')
    
    else: return diagonal(potentialField) 

def hamiltonian(meshbasis, potentialField: numpy.ndarray, mass: float):
    
    kineticOperator = kinetic(meshbasis, mass)
    potentialOperator = potential(meshbasis, potentialField)
    
    hamiltonianOperator = kineticOperator + potentialOperator
    hamiltonianOperator.meshbasis = meshbasis
    return hamiltonianOperator

pauliXMatrix = numpy.array([ [ 0j, 1 ], [ 1, 0j ] ])
pauliYMatrix = numpy.array([ [ 0j, -1j ], [ 1j, 0j ] ])
pauliZMatrix = numpy.array([ [ 1, 0j ], [ 0j, -1 ] ])

pauliX = Operator(pauliXMatrix, type = 'pauli')
pauliY = Operator(pauliYMatrix, type = 'pauli')
pauliZ = Operator(pauliZMatrix, type = 'pauli')

pauli = numpy.array([ pauliX, pauliY, pauliZ ]) # <--- MUST BE OPERATOR ARRAY
pauli4 = numpy.array([ identity(), pauliX, pauliY, pauliZ ]) # <--- MUST BE OPERATOR ARRAY

spinX = pauliX.scale(constant.halfhbar, type = 'spin')
spinY = pauliY.scale(constant.halfhbar, type = 'spin')
spinZ = pauliZ.scale(constant.halfhbar, type = 'spin')

spin = numpy.array([ spinX, spinY, spinZ ])

hadamardMatrix = constant.roothalf * numpy.array([ [ 1, 1 ], [ 1, -1 ] ])
hadamard = Operator(hadamardMatrix)