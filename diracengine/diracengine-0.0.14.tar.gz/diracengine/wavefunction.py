import numpy
from matplotlib import pyplot, animation

import diracengine.constant as constant

import diracengine.operator as operator
from diracengine.operator import Operator, identity

import diracengine.state as state
from diracengine.state import QuantumState

class WaveFunction:
    
    def __init__(self, initState: QuantumState, **kwargs):
        
        """
        Initate a wave function.
        Example: \ψ(0)>
        """
        
        self.initState = initState
        self.basis = initState.basis
        self.value = [self.initState]
        
        self.mass = kwargs.get('mass', 1)
        self.isEvolved = kwargs.get('evolved', False)
    
    def __len__(self): return len(self.basis)
    
    def next(self, hamiltonian: operator):
        
        """
        Calculate the next state of the wave function:
        Example: \ψ(t + Δt)> = [ 1 - i/ℏ H Δt ] \ψ(t)>
        """
    
        deltaTime = constant.delta()
        lastState = self.value[-1]
    
        nextState = ( -1j / constant.hbar * deltaTime * hamiltonian + identity(len(lastState)) ) @ lastState
        
        self.value.append(nextState)
    
    def evolve(self, hamiltonian: operator, totalTime: int):
        
        for _ in range(1, totalTime): self.next(hamiltonian)
        
        self.totalTime = totalTime
        self.isEvolved = True
            
    def plot(self, t: int = 0):
        
        """
        """
        
        pyplot.plot(self.basis, self.value[t].probabilityDensity())
        pyplot.show()
    
    def animate(self):
        
        """
        Animate how the wave function evolves over time
        """
        
        fig = pyplot.figure()
        ax = pyplot.axes(xlim=(self.basis[0], self.basis[-1]), ylim=(0, .25), xlabel='X', ylabel='ψ* ψ')
        line, = ax.plot([], [], lw=2, color='g')

        def init():
            line.set_data([], [])
            return line,

        def animate(t):
            line.set_data(self.basis, self.value[t-1].probabilityDensity())
            return line,

        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=self.totalTime, interval=30, blit=True)
        pyplot.show()