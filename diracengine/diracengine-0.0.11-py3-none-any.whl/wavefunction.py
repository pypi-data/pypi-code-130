from matplotlib import pyplot, animation

import diracengine.constant as constant

import diracengine.operator as operator
from diracengine.operator import Operator

import diracengine.state as state
from diracengine.state import QuantumState

class WaveFunction:
    
    def __init__(self, probabilityAmplitudes, basis, **kwargs):
        
        """
        Initate a wave function
        """
        
        self.basis = basis
        self.initState = QuantumState(probabilityAmplitudes, basis)
        
        self.mass = kwargs.get('mass', 1)
        self.isEvolved = kwargs.get('evolved', False)
        
        
    def evolve(self, potential, totalTime):
        
        """
        Calculate how the wave function will evolve
        """
        
        self.state = [self.initState]
        
        for time in range(1, totalTime):
            self.state.append(self.state[-1].shrodingerEvolve(self.mass, potential))

        self.totalTime = totalTime
        self.isEvolved = True
        
    def plot(self):
        
        """
        Plot animation of the wave funtion
        """
        
        fig = pyplot.figure()
        ax = pyplot.axes(xlim=(self.basis[0], self.basis[-1]), ylim=(0, .25), xlabel='X', ylabel='ψ* ψ')
        line, = ax.plot([], [], lw=2, color='g')

        def init():
            line.set_data([], [])
            return line,

        def animate(t):
            line.set_data(self.basis, self.state[t-1].probabilityDensity())
            return line,

        anim = animation.FuncAnimation(fig, animate, init_func=init, frames=self.totalTime, interval=30, blit=True)
        pyplot.show()