import numpy as np
from typing import ClassVar
from dataclasses import dataclass
from scipy.interpolate import interp1d

from SuPyMode.Tools.BaseClass import SetProperties, SetPlottings, ReprBase
from SuPyMode.SuperPosition   import SuperPosition

@dataclass
class SuperSet(SetProperties, SetPlottings, ReprBase):
    Description: ClassVar[str]  = 'SuperSet class'
    ReprVar    : ClassVar[list] = ["ParentSolver", "Size", "Geometry"]
    Methods    : ClassVar[list] = ["GetSuperposition", "Matrix"]

    ParentSolver: None = None
    def __post_init__(self):
        self.SuperModes     = []
        self.Matrix         = None
        self.ITR2SliceIntero = interp1d( self.ITRList, np.arange(self.ITRList.size) )

    def ITR2Slice(self, ITR: float):
        return int(self.ITR2SliceIntero(ITR))

    def GetPropagationMatrix(self):
        self.Matrix = np.zeros([self.Size, self.Size, len(self.ITRList)])

        for mode in self.SuperModes:
            self.Matrix[mode.ModeNumber, mode.ModeNumber, :] = mode.Betas

        return self.Matrix

    @property
    def Symmetries(self):
        return self.ParentSolver.Symmetries


    @property
    def FullxAxis(self):
        if self._FullxAxis is None:
            self._FullxAxis, self._FullyAxis = self.GetFullAxis(self.Axes.X, self.Axes.Y)
        return self._FullxAxis


    @property
    def FullyAxis(self):
        if self._FullyAxis is None:
            self._FullxAxis, self._FullyAxis = self.GetFullAxis(self.Axes.X, self.Axes.Y)
        return self._FullyAxis


    def IterateSuperMode(self):
        for n, supermode in enumerate(self.SuperModes):
            yield supermode


    def ComputeM(self, CouplingFactor):
        shape = self.Beta.shape
        M     = np.zeros( [shape[0], shape[1], shape[1]] )
        for iter in range(shape[0]):
            beta = self.Beta[iter]
            M[iter] = CouplingFactor[iter] * self.Coupling[iter] + beta * np.identity(shape[1])

        return M


    def ComputeCouplingFactor(self, Length):
        dx =  Length/(self.Geometry.ITRList.size)

        dITR = np.gradient(np.log(self.Geometry.ITRList), 1)

        return dITR/dx


    def GetSuperposition(self, Amplitudes):
        return SuperPosition(SuperSet=self, InitialAmplitudes=Amplitudes)


    def Propagate(self, Amplitude=[1,1, 0, 0, 0], Length=1000):
        Amplitude = np.asarray(Amplitude)

        Distance = np.linspace(0, Length, self.ITRList.size)

        #Factor = self.ComputeCouplingFactor(Length)

        #M = self.ComputeM(CouplingFactor=Factor)

        Minterp = interp1d(Distance, self.Matrix, axis=-1)

        def foo(t, y):
            return 1j * Minterp(t).dot(y)

        sol = solve_ivp(foo,
                        y0       = Amplitude.astype(complex),
                        t_span   = [0, Length],
                        method   = 'RK45')

        return sol.y


    def Propagate_(self, Amplitude, Length, **kwargs):
        Amplitude = np.asarray(Amplitude)

        Distance = np.linspace(0, Length, self.Geometry.ITRList.size)

        Factor = self.ComputeCouplingFactor(Length)


        M = self.ComputeM(CouplingFactor=Factor)

        Minterp = interp1d(Distance, M, axis=0)

        def foo(t, y):
            return 1j * Minterp(t).dot(y)

        sol = solve_ivp(foo,
                        y0       = Amplitude.astype(complex),
                        t_span   = [0, Length],
                        method   = 'RK45',
                        **kwargs)

        return sol

    @property
    def Size(self):
        return len(self.SuperModes)

    @property
    def Geometry(self):
        return self.ParentSolver.Geometry

    @property
    def ITRList(self):
        return self.ParentSolver.ITRList

    @property
    def Axes(self):
        return self.ParentSolver.Geometry.Axes


    def AppendSuperMode(self, CppSolver, BindingNumber, SolverNumber):
        from SuPyMode.SuperMode       import SuperMode
        superMode = SuperMode(ParentSet=self, CppSolver=CppSolver, BindingNumber=BindingNumber, SolverNumber=SolverNumber )

        self.SuperModes.append( superMode )


    def __getitem__(self, N):
        return self.SuperModes[N]


    def __setitem__(self, N, val):
        self.SuperModes[N] = val
