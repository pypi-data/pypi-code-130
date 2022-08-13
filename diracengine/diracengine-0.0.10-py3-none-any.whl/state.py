import cmath
import numpy

from diracengine.cmathplus import *

import diracengine.constant as constant

import diracengine.operator as operator
from diracengine.operator import Operator

class QuantumState:
    
    def totalProbability(self):
        
        """
        Get the total probability of the state.
        If it is not 1 then you should normilize it with
        the normalize() method.\n
        Example: < ψ | ψ > = 1
        """
        
        probability = 0
        
        for probabilityAmplitude in self.probabilityAmplitudes:
            
            if isinstance(probabilityAmplitude, complex): probability += conjugateSquare(probabilityAmplitude)
            elif isinstance(probabilityAmplitude, QuantumState): probability += probabilityAmplitude.totalProbability()
            else: TypeError()
        
        return probability
    
    def scale(self, factor: complex):
        
        """
        Scale every probability amplitude by some factor.\n
        Example: \ ψ > => f . \ ψ >
        """
        
        def scaleAmplitude(probabilityAmplitude):
            
            if isinstance(probabilityAmplitude, complex): return probabilityAmplitude * factor
            elif isinstance(probabilityAmplitude, QuantumState): return probabilityAmplitude.scale(factor)
            else: TypeError()
        
        self.probabilityAmplitudes = [ scaleAmplitude(probabilityAmplitude) for probabilityAmplitude in self.probabilityAmplitudes ]
        
        return self

    def normalize(self):
        
        """
        Normilize the quantum state. You can also
        normilize it so it has an arbitrary total probability.\n
        Example: \ ψ > => 1/√N \ ψ >
        """
        normalizationFactor = cmath.sqrt(self.norm / self.totalProbability())
        
        self = self.scale(normalizationFactor)
            
        return self
    
    def __init__(self, probabilityAmplitudes: list = [], basis: list = [], **kwargs):
        
        """
        Initiate a quantum state with given
        probability amplitudes and their state basis.\n
        Example: \ ψ > = Σ probability amplitude . \ state >
        """
        
        isNormalized = not kwargs.get('normalize', True)
        self.norm = kwargs.get('norm', 1)
        
        if len(basis) == len(probabilityAmplitudes):
            
            self.basis = basis   
            self.probabilityAmplitudes = probabilityAmplitudes
        
            if not isNormalized: self = self.normalize()
            
        else: raise AttributeError()
    
    def __str__(self):
        
        quantumStateString = '[\n'
        
        for base, probabilityAmplitude in zip(self.basis, self.probabilityAmplitudes):
            
            quantumStateString += f'\t{base}: {probabilityAmplitude.real} + {probabilityAmplitude.imag }i \n'
            
        quantumStateString += ']'
        
        return quantumStateString
    
    def __repr__(self): return f'Quantum state: {self.probabilityAmplitudes}'
    
    def __len__(self): return len(self.basis)
    
    def probabilityAmplitude(self, base):
        
        """
        Return the probability amplitude of a given state.\n
        Example: probability amplitude =  < state | ψ >
        """
        
        index = self.basis.index(base)
        return self.probabilityAmplitudes[index]
    
    def probability(self, base):
        
        """
        Return the probability of a given state.\n
        Example: probability =  < state | ψ >²
        """
        
        probabilityAmplitude = self.probabilityAmplitude(base)
        
        if isinstance(probabilityAmplitude, complex): return conjugateSquare(probabilityAmplitude)
        elif isinstance(probabilityAmplitude, QuantumState): return probabilityAmplitude.totalProbability()
        else: TypeError()
    
    def changeProbabilityAmplitudes(self, newProbabilityAmplitudes: list):
        
        self.probabilityAmplitudes = newProbabilityAmplitudes
    
    def conjugate(self):
        
        """
        Conjugate transpose the quantum state.\n
        Example: < ψ / = \ ψ >†
        """
        
        self.probabilityAmplitudes = [ probabilityAmplitude.conjugate() for probabilityAmplitude in self.probabilityAmplitudes ]
        
        return self
    
    def probabilityDensity(self):
        
        """
        Convert the quantum state to probability density distribution.\n
        Example: probability density = ψ* ψ
        """
    
        def probabilityDensityOfAmplitude(probabilityAmplitude):
            
            if isinstance(probabilityAmplitude, complex): return conjugateSquare(probabilityAmplitude)
            elif isinstance(probabilityAmplitude, QuantumState): return probabilityAmplitude.probabilityDensity()
            else: TypeError()
        
        return [ probabilityDensityOfAmplitude(probabilityAmplitude) for probabilityAmplitude in self.probabilityAmplitudes ]
    
    def probabilityDensityPercent(self):
        
        """
        Convert the quantum state to probability density distribution.\n
        Example: probability density % = ψ* ψ %
        """
        
        return [ 100 * probabilityDensity for probabilityDensity in self.probabilityDensity() ]
    
    def probabilityAmplitudeOfColapse(self, other):
        
        """
        Probability amplitude of this quantum state
        collapsing into another state.\n
        Example: < ϕ | ψ >
        """
        
        if isinstance(other, QuantumState):
            
            if self.basis == other.basis:
                
                probability = complex.zero
                
                for base in self.basis:
                    
                    probability += other.probabilityAmplitude(base).conjugate() * self.probabilityAmplitude(base)
                    
                return probability.real
            
            else: raise AttributeError()
        
        else: raise AttributeError()
    
    def probabilityOfColapse(self, other):
        
        """
        Probability of this quantum state
        collapsing into another state.\n
        Example: < ϕ | ψ >
        """
        
        if isinstance(other, QuantumState): return conjugateSquare(self.probabilityAmplitudeOfColapse(other))
        else: raise AttributeError()
    
    def phases(self):
        
        return [ cmath.phase(probabilityAmplitude) for probabilityAmplitude in self.probabilityAmplitudes ]

    def ket(self):
        
        """
        Return quantum state as a ket. Type of
        the returned ket is a numpy array.\n
        Example: \ ψ > = [ . . . ]
        """
        
        return numpy.array(self.probabilityAmplitudes)

    def bra(self):
        
        """
        Return quantum state as a ket. Type of
        the returned ket is a numpy array.\n
        Example: \ ψ > = [ . . . ]
        """
        
        return self.ket().transpose()

    def apply(self, operator: Operator):
        
        """
        Apply operator to the quantum state.\n
        Example: \ ψ > => operator \ ψ >
        """
        
        if operator.isMatrix:
            
            probabilityAmplitudesArray = operator.matrix @ self.ket()
            
            probabilityAmplitudes = probabilityAmplitudesArray.tolist()
            
            return QuantumState(probabilityAmplitudes, self.basis, normalize=False)
        
        elif operator.isComposed:
            
            state = self
            for operation in operator.composition: state = state.apply(operation)
            
            return state
        
        elif operator.type == 'factor': return self.scale(operator.factor)
        
        elif operator.type == 'position':
            
            basis = numpy.array(self.basis)
            matrixOperator = numpy.diag(basis)
            return self.apply(Operator(matrixOperator))
            
        
        elif operator.type == 'd/dx':
            
            N = len(self)
            X = self.basis
            PSI = self.probabilityAmplitudes
            nextPsi = [ 0 for _ in range(N) ]

            for x in range(N):
                
                core = PSI[x]
                coreX = X[x]
                
                try:
                    leftWing = PSI[x - 1]
                    leftX = X[x - 1]
                except:
                    leftWing = 0
                    leftX = 2 * X[x + 1] - X[x + 2]
                    
                try:
                    rightWing = PSI[x + 1]
                    rightX = X[x + 1]
                except:
                    leftWing = 0
                    rightX = 2 * X[x - 1] - X[x - 2]

                deltaX = rightX - leftX
                nextPsi[x] = (rightWing - leftWing) / deltaX
            
            return QuantumState(nextPsi, self.basis, normalize=False)
        
        elif operator.type == 'd2/dx2': 
            
            N = len(self)
            X = self.basis
            PSI = self.probabilityAmplitudes
            nextPsi = [ 0 for _ in range(N) ]
            
            for x in range(N):
                
                core = PSI[x]
                coreX = X[x]
                
                try:
                    leftWing = PSI[x - 1]
                    leftX = X[x - 1]
                except:
                    leftWing = 0
                    leftX = 2 * X[x + 1] - X[x + 2]
                
                try:
                    rightWing = PSI[x + 1]
                    rightX = X[x + 1]
                except:
                    leftWing = 0
                    rightX = 2 * X[x - 1] - X[x - 2]
                
                deltaX2 = (rightX - coreX) * (coreX - leftX)
                
                nextPsi[x] = (leftWing - 2 * core + rightWing) / deltaX2
            
            return QuantumState(nextPsi, self.basis, normalize=False)
        
        else: raise ValueError()
        
    def expectedValue(self, operator: Operator):
        
        """
        Calculate the expected value
        of a quantum operator.\n
        Example: < operator > = < ψ / operator \ ψ >
        """
   
        appliedKet = self.apply(operator).ket()
        bra = self.bra()
        
        expected = 0
        for ketAmplitude, braAmplitude in zip(appliedKet, bra): expected += ketAmplitude * braAmplitude
        
        return expected
   
    def timeEvolve(self, hamiltonian: Operator):
        
        """
        Calculate how the quantum state changes
        over small interval of time with a given
        potential. This returns the next state.\n
        Example: \ ψ > => [ 1 - i/ℏ H Δt ] \ ψ >
        """
        
        N = len(self)
        deltaT = constant.delta
        
        timeEvolutionOperator = numpy.identity(N) - hamiltonian.scale(constant.isubhbar * deltaT)
        
        result = self.apply(timeEvolutionOperator)
        return QuantumState(result.probabilityAmplitudes, self.basis)
    
    def shrodingerEvolve(self, mass: float, potentialField: list):
        
        """
        Solve Schrodinger's equation with given particle
        mass and potential. Note that this returns the next
        quantum state.\n
        Example: \ ψ > => [ 1 - i/ℏ ( p²/2m + U ) Δt ] \ ψ >
        """
        
        kineticEnergy = self.apply(operator.kinetic(mass)).ketMatrix()
        potentialEnergy = self.apply(operator.potential(potentialField)).ketMatrix()
        
        totalEnergy = kineticEnergy + potentialEnergy
        
        deltaT = constant.delta
        nextQuantumStateKet = self.ketMatrix() - totalEnergy.scale(constant.isubhbar * deltaT)
        
        return QuantumState(nextQuantumStateKet.matrix[0], self.basis)