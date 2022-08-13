datafile  = "../reference.root"
TupleName = "BS_POLY1_MISTAG"
Nmax      = -1
DoCalibrations = 1

CalibrationMode   = "Bs"
CalibrationLink   = "MISTAG"
CalibrationDegree = 1
CalibrationModel  = "POLY"
UseNewtonRaphson  = 0

BranchID = "FLAV_DECAY"
ProductionAsymmetry = 0

TauUnits  = "ps"
UseTau    = 1
BranchTau = "TAU"
UseTauErr = 0

OS_Muon_Use            = 1
OS_Muon_Write          = 0
OS_Muon_BranchDec      = "TOY0_DEC"
OS_Muon_BranchProb     = "TOY0_ETA"
OS_Electron_Use        = 1
OS_Electron_Write      = 0
OS_Electron_BranchDec  = "TOY1_DEC"
OS_Electron_BranchProb = "TOY1_ETA"
SS_Pion_Use        = 1
SS_Pion_Write      = 0
SS_Pion_BranchDec  = "TOY2_DEC"
SS_Pion_BranchProb = "TOY2_ETA"
SaveCalibrationsToXML = 1
