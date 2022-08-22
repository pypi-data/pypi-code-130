import numpy as np
from dataclasses import dataclass

from SuPyMode.SuperSet              import SuperSet
from SuPyMode.SuperMode             import SuperMode
from SuPyMode.bin.EigenSolver       import CppSolver as _CppSolver
from SuPyMode.Tools.utils           import Axes

from PyFinitDiff.Source import FiniteDifference2D




@dataclass
class SuPySolver(object):
    """ 
    This object corresponds to the solver.
    It solves the eigenvalues problems for a given geometry.

    """

    Geometry: None
    Tolerance : float = 1e-5
    MaxIter : int = 10000
    Accuracy: int = 2  
    Debug: bool = True
    SolverNumber: int = 0

    def __post_init__(self):
        self.Geometry.CreateMesh()


    def InitBinding(self, Symmetries: dict, Wavelength: float, nComputedMode: int, nSortedMode: int): 
        self.Symmetries = Symmetries
        self.Axes.Symmetries = Symmetries

        self.FD = FiniteDifference2D(Nx         = self.Geometry.Ny, 
                                     Ny         = self.Geometry.Nx, 
                                     dx         = self.Geometry.Axes.dy, 
                                     dy         = self.Geometry.Axes.dx, # TODO: check why I need to swap dx and dy
                                     Derivative = 2, 
                                     Accuracy   = self.Accuracy,
                                     Symmetries = Symmetries)


        self.FD.Compute()

        CppSolver = _CppSolver(Mesh          = self.Geometry._Mesh,
                               Gradient      = self.Geometry.Gradient().ravel(),
                               FinitMatrix   = self.FD.ToTriplet(),
                               nComputedMode = nComputedMode,
                               nSortedMode   = nSortedMode,
                               MaxIter       = self.MaxIter,
                               Tolerance     = self.Tolerance,
                               dx            = self.Axes.dx,
                               dy            = self.Axes.dy,
                               Wavelength    = Wavelength,
                               Debug         = self.Debug )

        CppSolver.ComputeLaplacian()

        return CppSolver


    def CreateSuperSet(self, Wavelength: float, NStep: int, ITRi: float, ITRf: float):
        self.Wavelength = Wavelength
        self.NStep      = NStep
        self.ITRi       = ITRi
        self.ITRf       = ITRf
        self.ITRList    = np.linspace(ITRi, ITRf, NStep)
        self.Set        = SuperSet(ParentSolver = self)


    def AddModes(self, nComputedMode: int, nSortedMode: int, Symmetries: dict, Sorting: str = 'Index'):

        CppSolver  = self.InitBinding(Symmetries, self.Wavelength, nComputedMode, nSortedMode)

        CppSolver.LoopOverITR(ITR=self.ITRList, ExtrapolationOrder=3)

        CppSolver.SortModes(Sorting=Sorting)

        CppSolver.ComputeCouplingAdiabatic()


        for BindingNumber in range(CppSolver.nSortedMode):
            self.Set.AppendSuperMode(CppSolver=CppSolver, BindingNumber=BindingNumber, SolverNumber=self.SolverNumber)

        self.SolverNumber += 1


    def GetSet(self):
        return self.Set


    @property
    def Axes(self):
        return self.Geometry.Axes



# ---
