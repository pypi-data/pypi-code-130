import cmath
import numpy

from diracengine.cmathplus import *

class QuantumState:
    
    def totalProbability(self):
        
        """
        Get the total probability of the state.
        If it is not 1 then you should normilize it with
        the normalize() method.\n
        Example: < ψ | ψ > = 1\n
        Shorthand: totalProb()
        """
        
        probability = 0
        
        for probabilityAmplitude in self.probabilityAmplitudes:
            
            if isinstance(probabilityAmplitude, complex): probability += conjugateSquare(probabilityAmplitude)
            else: raise TypeError('probability amplitudes must be complex numbers')
        
        return probability
    
    def totalProb(self): return self.totalProbability()
    
    def scale(self, scalar: complex):
        
        """
        Scale every probability amplitude by some factor.\n
        Example: \ ψ > => f . \ ψ >
        """
        
        def scaleAmplitude(probabilityAmplitude):
            
            if isinstance(probabilityAmplitude, complex): return scalar * probabilityAmplitude
            else: raise TypeError('probability amplitudes must be complex numbers')
        
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
    
    def __init__(self, probabilityAmplitudes: numpy.ndarray = numpy.ndarray([ ]), basis: numpy.ndarray = numpy.ndarray([ ]), **kwargs):
        
        """
        Initiate a quantum state with given
        probability amplitudes and their state basis.\n
        Example: \ ψ > = Σ probability amplitude . \ state >
        """
        
        isNormalized = not kwargs.get('normalize', True)
        self.norm = kwargs.get('norm', 1)
        
        if isinstance(basis, tuple):
            
            if len(basis) == 2:
                
                self.dimentions = 2
                self.basis = []
                self.meshbasis = basis
                
                X, Y = self.meshbasis
                self.N = ( len(X), len(Y) )
                
                for x, y in zip(X, Y):
                    
                    for _x, _y in zip(x, y):
                        
                        self.basis.append((_x, _y))
                
                self.probabilityAmplitudes = probabilityAmplitudes.reshape(len(self.basis))
                
            elif len(basis) == 3:
                
                self.dimentions = 3
                self.basis = []
                self.meshbasis = basis
                
                X, Y, Z = basis
                self.N = ( len(X), len(Y), len(Z) )
                
                for x, y, z in zip(X, Y, Z):
                    
                    for _x, _y, _z in zip(x, y, z):
                        
                        for __x, __y, __z in zip(_x, _y, _z):
                            
                            self.basis.append((__x, __y, __z))
                            
                self.probabilityAmplitudes = probabilityAmplitudes.reshape(len(self.basis))
                
            else: raise Exception('must be 1D, 2D or 3D')
            
        else:
            
            if len(basis) == len(probabilityAmplitudes):
                
                self.dimentions = 1
                self.basis = basis
                self.meshbasis = self.basis
                self.probabilityAmplitudes = probabilityAmplitudes
                self.N = len(self)
            
            else: raise KeyError('basis does not match probability amplitudes')

        if not isNormalized: self.normalize()
        
    def __str__(self):
        
        quantumStateString = '[\n'
        
        for base, probabilityAmplitude in zip(self.basis, self.probabilityAmplitudes):
            
            quantumStateString += f'\t{base}: {probabilityAmplitude.real} + {probabilityAmplitude.imag }i \n'
            
        quantumStateString += ']'
        
        return quantumStateString
    
    def log(self): print(self)
    
    def __repr__(self): return f'< quantum state : {self.probabilityAmplitudes} >'
    
    def __len__(self): return len(self.basis)
    
    def probabilityAmplitude(self, base):
        
        """
        Return the probability amplitude of a given state.\n
        Example: probability amplitude =  < state | ψ >\n
        Shorthand: probAmp(base)
        """
        
        index = self.basis.index(base)
        return self.probabilityAmplitudes[index]
    
    def probAmp(self, base): return self.probabilityAmplitude(base)
    
    def probability(self, base):
        
        """
        Return the probability of a given state.\n
        Example: probability =  < ψ | state >< state | ψ >\n
        Shorthand: prob(base)
        """
        
        probabilityAmplitude = self.probabilityAmplitude(base)
        
        if isinstance(probabilityAmplitude, complex): return conjugateSquare(probabilityAmplitude)
        else: raise TypeError('probability amplitudes must be complex numbers')
    
    def prob(self, base): return self.probability(base)
    
    def changeProbabilityAmplitudes(self, newProbabilityAmplitudes: numpy.ndarray):
        
        self.probabilityAmplitudes = newProbabilityAmplitudes
    
    def changeProbAmp(self, newProbabilityAmplitudes: numpy.ndarray): return self.changeProbabilityAmplitudes(newProbabilityAmplitudes)
    
    def conjugate(self):
        
        """
        Conjugate transpose the quantum state.\n
        Example: < ψ / = \ ψ >†\n
        Shorthand: conj()
        """
        
        self.probabilityAmplitudes = [ probabilityAmplitude.conjugate() for probabilityAmplitude in self.probabilityAmplitudes ]
        
        return self
    
    def conj(self): return self.conjugate()
    
    def probabilityDensity(self):
        
        """
        Convert the quantum state to probability density distribution.\n
        Example: probability density = ψ* ψ\n
        Shorthand: probDensity()
        """
    
        def probabilityDensityOfAmplitude(probabilityAmplitude):
            
            if isinstance(probabilityAmplitude, complex): return conjugateSquare(probabilityAmplitude)
            raise TypeError('probability amplitudes must be complex numbers')
        
        return numpy.array([ probabilityDensityOfAmplitude(probabilityAmplitude) for probabilityAmplitude in self.probabilityAmplitudes ]).reshape(self.N)
    
    def probDensity(self): return self.probabilityDensity()
    
    def probabilityDensityPercent(self):
        
        """
        Convert the quantum state to probability density distribution.\n
        Example: probability density % = ψ* ψ %\n
        Shorthand: probDensityP()
        """
        
        return [ 100 * probabilityDensity for probabilityDensity in self.probabilityDensity() ]
    
    def probDensityP(self): return self.probabilityDensityPercent()
    
    def probabilityAmplitudeOfCollapse(self, other):
        
        """
        Probability amplitude of this quantum state
        collapsing into another state.\n
        Example: < ϕ | ψ >\n
        Shorthand: probAmpCollapse(other)
        """
        
        if isinstance(other, QuantumState):
            
            if self.basis == other.basis:
                
                probability = 0j
                for base in self.basis: probability += other.probabilityAmplitude(base).conjugate() * self.probabilityAmplitude(base)
                return probability.real
            
            else: raise KeyError('basis of quantum states does not match')
        
        else: raise TypeError('input must be of type QuantumState')
    
    def probAmpCollapse(self, other): self.probabilityAmplitudeOfCollapse(other)
    
    def probabilityOfCollapse(self, other):
        
        """
        Probability of this quantum state
        collapsing into another state.\n
        Example: < ϕ | ψ >\n
        Shorthand: probCollapse(other)
        """
        
        return conjugateSquare(self.probabilityAmplitudeOfCollapse(other))
    
    def probCollapse(self, other): self.probabilityOfCollapse(other)
    
    def phases(self):
        
        """
        Return a list of probability amplitudes' phases.\n
        """
        
        return [ cmath.phase(probabilityAmplitude) for probabilityAmplitude in self.probabilityAmplitudes ]

    def ket(self):
        
        """
        Return quantum state as a ket. Type of
        the returned ket is a numpy array.\n
        Example: \ ψ > = [ ., ., ... ]
        """
        
        return numpy.array(self.probabilityAmplitudes)

    def bra(self):
        
        """
        Return quantum state as a ket. Type of
        the returned bra is a numpy array.\n
        Example: < ψ / = [ [.], [.], ... ]
        """
        
        return self.ket().transpose()
        
    def expectationValue(self, operator):
        
        """
        Calculate the expectation value
        of a quantum operator.\n
        Example: < operator > = < ψ / operator \ ψ >
        """
   
        appliedKet = operator.act(self).ket()
        bra = self.bra()
        
        return bra @ appliedKet

    def expValue(self, operator): self.expectationValue(operator)