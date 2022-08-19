import pytest
import sys
sys.path.append(r'C:\Program Files\DIgSILENT\PowerFactory 2022 SP1\Python\3.10')
import powerfactory
sys.path.insert(0,r'.\src')
import powerfactorypy 
import importlib
importlib.reload(powerfactorypy)
from matplotlib import pyplot

from test_base_interface import pfbi, pf_app, activate_test_project

@pytest.fixture
def pfplot(pf_app):
    # Return PFPlotInterface instance
    return powerfactorypy.PFPlotInterface(pf_app)  

def test_pyplot_from_csv(pfplot,activate_test_project):
    export_dir = r"D:\User\seberlein\Code\powerfactorypy\tests"
    file_name = "results"
    pfsim = powerfactorypy.PFDynSimInterface(pfplot.app)
    pfsim.export_dir =  export_dir
    pfsim.activate_study_case(r"Study Cases\Study Case 1")
    pfsim.initialize_and_run_sim()
    pfsim.export_to_csv(file_name=file_name)

    pyplot.figure()
    powerfactorypy.PFPlotInterface.pyplot_from_csv(
    export_dir + "\\" + file_name + ".csv",
    [r"Network Model\Network Data\Grid\AC Voltage Source\s:u0",
     r"Network Model\Network Data\Grid\AC Voltage Source\m:Qsum:bus1"]) 
    pyplot.xlabel("t [s]")

def test_copy_graphics_board_content(pfplot,activate_test_project):
    source_study_case = r"Study Cases\Study Case 1"
    target_study_cases = [r"Study Cases\Study Case 2", 
        r"Study Cases\Study Case 3"]
    pfplot.copy_graphics_board_content(source_study_case,target_study_cases,
        obj_to_copy="*.GrpPage",clear_target_graphics_board=True)  

def test_copy_graphics_board_content_to_all_study_cases(pfplot,activate_test_project):
    source_study_case = r"Study Cases\Study Case 1"
    pfplot.copy_graphics_board_content_to_all_study_cases(source_study_case)

if __name__ == "__main__":
    pytest.main(([r"tests\test_plot_interface.py"]))


