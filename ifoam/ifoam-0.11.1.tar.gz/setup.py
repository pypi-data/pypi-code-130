# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['foam',
 'foam.app',
 'foam.app.command',
 'foam.app.information',
 'foam.app.postprocess',
 'foam.base']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0']

extras_require = \
{'7z': ['py7zr>=0.17.2,<0.18.0'],
 'cli': ['click>=8.0.3,<9.0.0'],
 'full': ['py7zr>=0.17.2,<0.18.0',
          'click>=8.0.3,<9.0.0',
          'tqdm>=4.63.1,<5.0.0',
          'vtk>=9.1.0,<10.0.0'],
 'tqdm': ['tqdm>=4.63.1,<5.0.0'],
 'vtk': ['vtk>=9.1.0,<10.0.0']}

setup_kwargs = {
    'name': 'ifoam',
    'version': '0.11.1',
    'description': 'Python Interface to OpenFOAM (Configured Using YAML)',
    'long_description': '<!-- Template from https://github.com/othneildrew/Best-README-Template -->\n<div id="top"></div>\n\n\n\n<!-- PROJECT SHIELDS -->\n[![Contributors][contributors-shield]][contributors-url]\n[![Forks][forks-shield]][forks-url]\n[![Stargazers][stars-shield]][stars-url]\n[![Issues][issues-shield]][issues-url]\n[![GPL-3.0 License][license-shield]][license-url]\n\n\n\n<!-- PROJECT LOGO -->\n<br />\n<div align="center">\n  <a href="https://github.com/iydon/of.yaml">\n    🟢⬜🟩⬜🟩<br />\n    ⬜⬜⬜⬜⬜<br />\n    🟩⬜🟩⬜🟩<br />\n    ⬜⬜⬜⬜⬜<br />\n    🟩⬜🟩⬜🟩<br />\n  </a>\n\n  <h3 align="center">OpenFOAM.YAML</h3>\n\n  <p align="center">\n    Python Interface to OpenFOAM (Configured Using YAML)\n    <br />\n    <a href="https://github.com/iydon/of.yaml"><strong>Explore the docs »</strong></a>\n    <br />\n    <br />\n    <a href="https://github.com/iydon/of.yaml">View Demo</a>\n    ·\n    <a href="https://github.com/iydon/of.yaml/issues">Report Bug</a>\n    ·\n    <a href="https://github.com/iydon/of.yaml/issues">Request Feature</a>\n  </p>\n</div>\n\n\n\n<!-- TABLE OF CONTENTS -->\n<details>\n  <summary>Table of Contents</summary>\n  <ol>\n    <li>\n      <a href="#about-the-project">About The Project</a>\n      <ul>\n        <li><a href="#built-with">Built With</a></li>\n      </ul>\n    </li>\n    <li>\n      <a href="#getting-started">Getting Started</a>\n      <ul>\n        <li><a href="#prerequisites">Prerequisites</a></li>\n        <li><a href="#installation">Installation</a></li>\n      </ul>\n    </li>\n    <li><a href="#usage">Usage</a></li>\n      <ul>\n        <li><a href="#demo">Demo</a></li>\n        <li><a href="#tutorials">Tutorials</a></li>\n        <li><a href="#task-list">Task List</a></li>\n      </ul>\n    </li>\n    <li><a href="#contributing">Contributing</a></li>\n    <li><a href="#license">License</a></li>\n    <li><a href="#contact">Contact</a></li>\n  </ol>\n</details>\n\n\n\n<!-- ABOUT THE PROJECT -->\n## About The Project\n\nThis repository was originally designed to solve the problem of complex OpenFOAM case structure, and the solution was to re-present the original cases using the common configuration file format YAML. Later, since there is a corresponding package for the YAML format in Python, I wrote this Python interface package for OpenFOAM, and then I added progress bars to most OpenFOAM solvers by analyzing log files in real time. Although there are still many details to be specified in this repository, its function of generating cases and calling solvers is ready for preliminary use, for example, I used this package to generate cases in batch in my own project. In the future I would like to integrate the post-processing steps into this interface package as well.\n\n<p align="right">(<a href="#top">back to top</a>)</p>\n\n### Built With\n\n* [Poetry](https://github.com/python-poetry/poetry)\n* [PyYAML](https://github.com/yaml/pyyaml)\n* [py7zr](https://github.com/miurahr/py7zr)\n* [packaging](https://github.com/pypa/packaging)\n* [click](https://github.com/pallets/click)\n* [tqdm](https://github.com/tqdm/tqdm)\n\n<p align="right">(<a href="#top">back to top</a>)</p>\n\n\n\n<!-- GETTING STARTED -->\n## Getting Started\n\nTo get a local copy up and running follow these simple example steps.\n\n### Prerequisites\n\nThis project currently uses Poetry to manage Python dependencies. I\'ve heard good things about [PDM](https://github.com/pdm-project/pdm) so far, and may provide PDM support subsequently. If Poetry is not installed, you can refer to [official installation guide](https://github.com/python-poetry/poetry#installation).\n\n### Installation\n\n1. Clone the repository\n   ```sh\n   git clone https://github.com/iydon/of.yaml.git\n   ```\n2. Install Python dependencies\n   ```sh\n   poetry install --extras full\n   ```\n3. Activate the virtual environment\n   ```sh\n   poetry shell\n   ```\n4. (Optional) Convert Python package into a single file\n   ```sh\n   make standalone\n   ```\n\n<p align="right">(<a href="#top">back to top</a>)</p>\n\n\n\n<!-- USAGE EXAMPLES -->\n## Usage\n\n### Demo\n\nSave the following demo code as a separate file (e.g. `demo.py`).\n\n```python\nfrom foam import Foam\n\nfoam = Foam.from_file(\'tutorials/incompressible/simpleFoam/airFoil2D.yaml\')\nfoam.save(\'airFoil2D\')\nfoam.cmd.all_run()\n```\n\nRunning the demo code in the virtual environment results in the following output.\n\n```sh\n$ poetry run python demo.py\nRunning simpleFoam on .../of.yaml/airFoil2D\n 63%|██████████████████████████████████████▏                      | 313.0/500.0 [00:06<00:04, 46.66it/s]\n```\n\n### Tutorials\n\nThe following table shows the OpenFOAM cases that have been converted to YAML format. You can find the corresponding rules by comparing the YAML format with its original format, and I don\'t have the time or interest to organize the corresponding documentation for the time being.\n\n<details>\n  <summary>The existing OpenFOAM tutorials in YAML format</summary>\n\n  | YAML | OpenFOAM | Version | Solver |\n  | --- | --- | --- | --- |\n  | [airFoil2D.yaml](tutorials/incompressible/simpleFoam/airFoil2D.yaml) | [airFoil2D](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/incompressible/simpleFoam/airFoil2D) | 7 | [incompressible/simpleFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/incompressible/simpleFoam) |\n  | [beamEndLoad.yaml](tutorials/stressAnalysis/solidEquilibriumDisplacementFoam/beamEndLoad.yaml) | [beamEndLoad](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/stressAnalysis/solidEquilibriumDisplacementFoam/beamEndLoad) | 7 | [stressAnalysis/solidEquilibriumDisplacementFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/stressAnalysis/solidEquilibriumDisplacementFoam) |\n  | [boxTurb16.yaml](tutorials/DNS/dnsFoam/boxTurb16.yaml) | [boxTurb16](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/DNS/dnsFoam/boxTurb16) | 7 | [DNS/dnsFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/DNS/dnsFoam) |\n  | [cylinder.yaml](tutorials/basic/potentialFoam/cylinder.yaml) | [cylinder](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/basic/potentialFoam/cylinder) | 7 | [basic/potentialFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/basic/potentialFoam) |\n  | [damBreak.yaml](tutorials/multiphase/interMixingFoam/laminar/damBreak.yaml) | [damBreak](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/interMixingFoam/laminar/damBreak) | 7 | [multiphase/interMixingFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/interFoam/interMixingFoam) |\n  | [damBreak4phase.yaml](tutorials/multiphase/multiphaseInterFoam/laminar/damBreak4phase.yaml) | [damBreak4phase](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/multiphaseInterFoam/laminar/damBreak4phase) | 7 | [multiphase/multiphaseInterFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/multiphaseInterFoam) |\n  | [damBreak4phaseFine.yaml](tutorials/multiphase/multiphaseInterFoam/laminar/damBreak4phaseFine.yaml) | [damBreak4phaseFine](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/multiphaseInterFoam/laminar/damBreak4phaseFine) | 7 | [multiphase/multiphaseInterFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/multiphaseInterFoam) |\n  | [damBreakWithObstacle.yaml](tutorials/multiphase/interFoam/laminar/damBreakWithObstacle.yaml) | [damBreakWithObstacle](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/interFoam/laminar/damBreakWithObstacle) | 7 | [multiphase/interFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/interFoam) |\n  | [DTCHull.yaml](tutorials/multiphase/interFoam/RAS/DTCHull.yaml) | [DTCHull](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/interFoam/RAS/DTCHull) | 7 | [multiphase/interFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/interFoam) |\n  | [elbow.yaml](tutorials/incompressible/icoFoam/elbow.yaml) | [elbow](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/incompressible/icoFoam/elbow) | 7 | [incompressible/icoFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/incompressible/icoFoam) |\n  | [europeanCall.yaml](tutorials/financial/financialFoam/europeanCall.yaml) | [europeanCall](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/financial/financialFoam/europeanCall) | 7 | [financial/financialFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/financial/financialFoam) |\n  | [fileHandler.yaml](tutorials/IO/fileHandler.yaml) | [fileHandler](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/IO/fileHandler) | 7 | [lagrangian/icoUncoupledKinematicParcelFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/lagrangian/icoUncoupledKinematicParcelFoam) |\n  | [flange.yaml](tutorials/basic/laplacianFoam/flange.yaml) | [flange](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/basic/laplacianFoam/flange) | 7 | [basic/laplacianFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/basic/laplacianFoam) |\n  | [mixerVessel2D.yaml](tutorials/multiphase/multiphaseInterFoam/laminar/mixerVessel2D.yaml) | [mixerVessel2D](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/multiphaseInterFoam/laminar/mixerVessel2D) | 7 | [multiphase/multiphaseInterFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/multiphaseInterFoam) |\n  | [nozzleFlow2D.yaml](tutorials/multiphase/interFoam/LES/nozzleFlow2D.yaml) | [nozzleFlow2D](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/interFoam/LES/nozzleFlow2D) | 7 | [multiphase/interFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/interFoam) |\n  | [pipeCyclic.yaml](tutorials/incompressible/simpleFoam/pipeCyclic.yaml) | [pipeCyclic](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/incompressible/simpleFoam/pipeCyclic) | 7 | [incompressible/simpleFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/incompressible/simpleFoam) |\n  | [pitzDaily.yaml](tutorials/basic/potentialFoam/pitzDaily.yaml) | [pitzDaily](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/basic/potentialFoam/pitzDaily) | 7 | [basic/potentialFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/basic/potentialFoam) |\n  | [pitzDaily.yaml](tutorials/basic/scalarTransportFoam/pitzDaily.yaml) | [pitzDaily](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/basic/scalarTransportFoam/pitzDaily) | 7 | [basic/scalarTransportFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/basic/scalarTransportFoam) |\n  | [plateHole.yaml](tutorials/stressAnalysis/solidDisplacementFoam/plateHole.yaml) | [plateHole](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/stressAnalysis/solidDisplacementFoam/plateHole) | 7 | [stressAnalysis/solidDisplacementFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/stressAnalysis/solidDisplacementFoam) |\n  | [sloshingTank3D6DoF.yaml](tutorials/multiphase/interFoam/laminar/sloshingTank3D6DoF.yaml) | [sloshingTank3D6DoF](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/interFoam/laminar/sloshingTank3D6DoF) | 7 | [multiphase/interFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/interFoam) |\n  | [propeller.yaml](tutorials/multiphase/interPhaseChangeFoam/propeller.yaml) | [propeller](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/interPhaseChangeFoam/propeller) | 7 | [multiphase/interPhaseChangeFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/interPhaseChangeFoam) |\n  | [mixerVesselAMI.yaml](tutorials/multiphase/interFoam/RAS/mixerVesselAMI.yaml) | [mixerVesselAMI](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/interFoam/RAS/mixerVesselAMI) | 7 | [multiphase/interFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/interFoam) |\n  | [sloshingTank2D.yaml](tutorials/multiphase/compressibleInterFoam/laminar/sloshingTank2D.yaml) | [sloshingTank2D](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/compressibleInterFoam/laminar/sloshingTank2D) | 7 | [multiphase/compressibleInterFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/compressibleInterFoam) |\n  | [damBreak4phase.yaml](tutorials/multiphase/compressibleMultiphaseInterFoam/laminar/damBreak4phase.yaml) | [damBreak4phase](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/compressibleMultiphaseInterFoam/laminar/damBreak4phase) | 7 | [multiphase/compressibleMultiphaseInterFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/compressibleMultiphaseInterFoam) |\n  | [flamePropagationWithObstacles.yaml](tutorials/combustion/PDRFoam/flamePropagationWithObstacles.yaml) | [flamePropagationWithObstacles](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/combustion/PDRFoam/flamePropagationWithObstacles) | 7 | [combustion/PDRFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/combustion/PDRFoam) |\n  | [kivaTest.yaml](tutorials/combustion/XiEngineFoam/kivaTest.yaml) | [kivaTest](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/combustion/XiEngineFoam/kivaTest) | 7 | [combustion/XiEngineFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/combustion/XiFoam/XiEngineFoam) |\n  | [moriyoshiHomogeneous.yaml](tutorials/combustion/XiFoam/RAS/moriyoshiHomogeneous.yaml) | [moriyoshiHomogeneous](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/combustion/XiFoam/RAS/moriyoshiHomogeneous) | 7 | [combustion/XiFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/combustion/XiFoam) |\n  | [throttle.yaml](tutorials/multiphase/cavitatingFoam/LES/throttle.yaml) | [throttle](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/cavitatingFoam/LES/throttle) | 7 | [multiphase/cavitatingFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/cavitatingFoam) |\n  | [throttle3D.yaml](tutorials/multiphase/cavitatingFoam/LES/throttle3D.yaml) | [throttle3D](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/cavitatingFoam/LES/throttle3D) | 7 | [multiphase/cavitatingFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/cavitatingFoam) |\n  | [throttle.yaml](tutorials/multiphase/cavitatingFoam/RAS/throttle.yaml) | [throttle](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/tutorials/multiphase/cavitatingFoam/RAS/throttle) | 7 | [multiphase/cavitatingFoam](https://github.com/OpenFOAM/OpenFOAM-7/tree/master/applications/solvers/multiphase/cavitatingFoam) |\n</details>\n\n### Task List\n\nThe following is a task list to convert [OpenFOAM-7](https://github.com/OpenFOAM/OpenFOAM-7) to the corresponding YAML format. The corresponding rules for conversion are not currently organized because some of them are still unstable. I will first try to convert as many tutorials as possible, and then organize the rules afterwards.\n\n<details>\n  <summary>Conversion task list</summary>\n\n  - [x] DNS\n      - [x] dnsFoam\n          - [x] boxTurb16\n  - [x] IO\n      - [x] fileHandler\n  - [x] basic\n      - [x] laplacianFoam\n          - [x] flange\n      - [x] potentialFoam\n          - [x] cylinder\n          - [x] pitzDaily\n      - [x] scalarTransportFoam\n          - [x] pitzDaily\n  - [ ] combustion\n      - [x] PDRFoam\n          - [x] flamePropagationWithObstacles\n      - [x] XiEngineFoam\n          - [x] kivaTest\n      - [x] XiFoam\n          - [x] RAS\n              - [x] moriyoshiHomogeneous\n      - [ ] chemFoam\n          - [ ] gri\n          - [ ] h2\n          - [ ] ic8h18\n          - [ ] ic8h18_TDAC\n          - [ ] nc7h16\n      - [ ] coldEngineFoam\n          - [ ] freePiston\n      - [ ] fireFoam\n          - [ ] LES\n              - [ ] flameSpreadWaterSuppressionPanel\n              - [ ] oppositeBurningPanels\n              - [ ] smallPoolFire2D\n              - [ ] smallPoolFire3D\n      - [ ] reactingFoam\n          - [ ] RAS\n              - [ ] DLR_A_LTS\n              - [ ] SandiaD_LTS\n              - [ ] membrane\n          - [ ] laminar\n              - [ ] counterFlowFlame2D\n              - [ ] counterFlowFlame2DLTS\n              - [ ] counterFlowFlame2DLTS_GRI_TDAC\n              - [ ] counterFlowFlame2D_GRI\n              - [ ] counterFlowFlame2D_GRI_TDAC\n  - [ ] compressible\n      - [ ] rhoCentralFoam\n          - [ ] LadenburgJet60psi\n          - [ ] biconic25-55Run35\n          - [ ] forwardStep\n          - [ ] movingCone\n          - [ ] obliqueShock\n          - [ ] shockTube\n          - [ ] wedge15Ma5\n      - [ ] rhoPimpleFoam\n          - [ ] LES\n              - [ ] pitzDaily\n          - [ ] RAS\n              - [ ] aerofoilNACA0012\n              - [ ] angledDuct\n              - [ ] angledDuctLTS\n              - [ ] annularThermalMixer\n              - [ ] cavity\n              - [ ] mixerVessel2D\n              - [ ] nacaAirfoil\n              - [ ] prism\n              - [ ] squareBendLiq\n          - [ ] laminar\n              - [ ] blockedChannel\n              - [ ] decompressionTank\n              - [ ] forwardStep\n              - [ ] helmholtzResonance\n              - [ ] shockTube\n      - [ ] rhoPorousSimpleFoam\n          - [ ] angledDuctExplicit\n          - [ ] angledDuctImplicit\n      - [ ] rhoSimpleFoam\n          - [ ] aerofoilNACA0012\n          - [ ] angledDuctExplicitFixedCoeff\n          - [ ] squareBend\n          - [ ] squareBendLiq\n  - [ ] discreteMethods\n      - [ ] dsmcFoam\n          - [ ] freeSpacePeriodic\n          - [ ] freeSpaceStream\n          - [ ] supersonicCorner\n          - [ ] wedge15Ma5\n      - [ ] molecularDynamics\n          - [ ] mdEquilibrationFoam\n              - [ ] periodicCubeArgon\n              - [ ] periodicCubeWater\n          - [ ] mdFoam\n              - [ ] nanoNozzle\n  - [ ] electromagnetics\n      - [ ] electrostaticFoam\n          - [ ] chargedWire\n      - [ ] mhdFoam\n          - [ ] hartmann\n  - [x] financial\n      - [x] financialFoam\n          - [x] europeanCall\n  - [ ] heatTransfer\n      - [ ] buoyantPimpleFoam\n          - [ ] BernardCells\n          - [ ] hotRoom\n          - [ ] hotRoomBoussinesq\n      - [ ] buoyantSimpleFoam\n          - [ ] buoyantCavity\n          - [ ] circuitBoardCooling\n          - [ ] externalCoupledCavity\n          - [ ] hotRadiationRoom\n          - [ ] hotRadiationRoomFvDOM\n          - [ ] hotRoomBoussinesq\n          - [ ] iglooWithFridges\n      - [ ] chtMultiRegionFoam\n          - [ ] coolingSphere\n          - [ ] heatExchanger\n          - [ ] heatedDuct\n          - [ ] reverseBurner\n          - [ ] shellAndTubeHeatExchanger\n  - [ ] incompressible\n      - [ ] SRFPimpleFoam\n          - [ ] rotor2D\n      - [ ] SRFSimpleFoam\n          - [ ] mixer\n      - [ ] adjointShapeOptimizationFoam\n          - [ ] pitzDaily\n      - [ ] boundaryFoam\n          - [ ] boundaryLaunderSharma\n          - [ ] boundaryWallFunctions\n          - [ ] boundaryWallFunctionsProfile\n      - [ ] icoFoam\n          - [ ] cavity\n              - [ ] cavity\n              - [ ] cavityClipped\n              - [ ] cavityGrade\n          - [x] elbow\n      - [ ] nonNewtonianIcoFoam\n          - [ ] offsetCylinder\n      - [ ] pimpleFoam\n          - [ ] LES\n              - [ ] channel395\n          - [ ] RAS\n              - [ ] TJunction\n              - [ ] TJunctionFan\n              - [ ] elipsekkLOmega\n              - [ ] impeller\n              - [ ] oscillatingInletACMI2D\n              - [ ] pitzDaily\n              - [ ] pitzDailyLTS\n              - [ ] propeller\n              - [ ] wingMotion\n          - [ ] laminar\n              - [ ] blockedChannel\n              - [ ] mixerVesselAMI2D\n              - [ ] movingCone\n              - [ ] offsetCylinder\n              - [ ] planarContraction\n              - [ ] planarCouette\n              - [ ] planarPoiseuille\n      - [ ] pisoFoam\n          - [ ] LES\n              - [ ] motorBike\n              - [ ] pitzDaily\n              - [ ] pitzDailyMapped\n          - [ ] RAS\n              - [ ] cavity\n              - [ ] cavityCoupledU\n          - [ ] laminar\n              - [ ] porousBlockage\n      - [ ] porousSimpleFoam\n          - [ ] angledDuctExplicit\n          - [ ] angledDuctImplicit\n          - [ ] straightDuctImplicit\n      - [ ] shallowWaterFoam\n          - [ ] squareBump\n      - [ ] simpleFoam\n          - [ ] T3A\n          - [x] airFoil2D\n          - [ ] mixerVessel2D\n          - [ ] motorBike\n          - [x] pipeCyclic\n          - [ ] pitzDaily\n          - [ ] pitzDailyExptInlet\n          - [ ] rotorDisk\n          - [ ] turbineSiting\n          - [ ] windAroundBuildings\n  - [ ] lagrangian\n      - [ ] DPMFoam\n          - [ ] Goldschmidt\n      - [ ] MPPICFoam\n          - [ ] Goldschmidt\n          - [ ] column\n          - [ ] cyclone\n          - [ ] injectionChannel\n      - [ ] coalChemistryFoam\n          - [ ] simplifiedSiwek\n      - [ ] icoUncoupledKinematicParcelFoam\n          - [ ] hopper\n              - [ ] hopperEmptying\n              - [ ] hopperInitialState\n          - [ ] mixerVesselAMI2D\n      - [ ] reactingParcelFoam\n          - [ ] counterFlowFlame2DLTS\n          - [ ] cylinder\n          - [ ] filter\n          - [ ] hotBoxes\n          - [ ] parcelInBox\n          - [ ] rivuletPanel\n          - [ ] splashPanel\n          - [ ] verticalChannel\n          - [ ] verticalChannelLTS\n      - [ ] simpleReactingParcelFoam\n          - [ ] verticalChannel\n      - [ ] sprayFoam\n          - [ ] aachenBomb\n  - [ ] mesh\n      - [ ] blockMesh\n          - [ ] pipe\n          - [ ] sphere\n          - [ ] sphere7\n          - [ ] sphere7ProjectedEdges\n      - [ ] foamyHexMesh\n          - [ ] blob\n          - [ ] flange\n          - [ ] mixerVessel\n          - [ ] simpleShapes\n          - [ ] straightDuctImplicit → ../../incompressible/porousSimpleFoam/straightDuctImplicit\n      - [ ] foamyQuadMesh\n          - [ ] jaggedBoundary\n          - [ ] square\n      - [ ] moveDynamicMesh\n          - [ ] SnakeRiverCanyon\n      - [ ] refineMesh\n          - [ ] refineFieldDirs\n      - [ ] snappyHexMesh\n          - [ ] flange\n          - [ ] iglooWithFridges → ../../heatTransfer/buoyantSimpleFoam/iglooWithFridges\n          - [ ] motorBike → ../../incompressible/simpleFoam/motorBike\n  - [ ] multiphase\n      - [x] cavitatingFoam\n          - [x] LES\n              - [x] throttle\n              - [x] throttle3D\n          - [x] RAS\n              - [x] throttle\n      - [ ] compressibleInterFoam\n          - [ ] laminar\n              - [ ] climbingRod\n              - [ ] depthCharge2D\n              - [ ] depthCharge3D\n              - [x] sloshingTank2D\n      - [x] compressibleMultiphaseInterFoam\n          - [x] laminar\n              - [x] damBreak4phase\n      - [ ] driftFluxFoam\n          - [ ] RAS\n              - [ ] dahl\n              - [ ] mixerVessel2D\n              - [ ] tank3D\n      - [ ] interFoam\n          - [x] LES\n              - [x] nozzleFlow2D\n          - [ ] RAS\n              - [x] DTCHull\n              - [ ] DTCHullMoving\n              - [ ] DTCHullWave\n              - [ ] angledDuct\n              - [ ] damBreak\n              - [ ] damBreakPorousBaffle\n              - [ ] floatingObject\n              - [x] mixerVesselAMI\n              - [ ] waterChannel\n              - [ ] weirOverflow\n          - [ ] laminar\n              - [ ] capillaryRise\n              - [ ] damBreak\n              - [x] damBreakWithObstacle\n              - [ ] mixerVessel2D\n              - [ ] sloshingCylinder\n              - [ ] sloshingTank2D\n              - [ ] sloshingTank2D3DoF\n              - [ ] sloshingTank3D\n              - [ ] sloshingTank3D3DoF\n              - [x] sloshingTank3D6DoF\n              - [ ] testTubeMixer\n              - [ ] wave\n      - [x] interMixingFoam\n          - [x] laminar\n              - [x] damBreak\n      - [ ] interPhaseChangeFoam\n          - [ ] cavitatingBullet\n          - [x] propeller\n      - [ ] multiphaseEulerFoam\n          - [ ] bubbleColumn\n          - [ ] damBreak4phase\n          - [ ] damBreak4phaseFine\n          - [ ] mixerVessel2D\n      - [x] multiphaseInterFoam\n          - [x] laminar\n              - [x] damBreak4phase\n              - [x] damBreak4phaseFine\n              - [x] mixerVessel2D\n      - [ ] potentialFreeSurfaceFoam\n          - [ ] movingOscillatingBox\n          - [ ] oscillatingBox\n      - [ ] reactingMultiphaseEulerFoam\n          - [ ] RAS\n              - [ ] wallBoiling1D_2phase\n              - [ ] wallBoiling1D_3phase\n          - [ ] laminar\n              - [ ] bed\n              - [ ] bubbleColumn\n              - [ ] bubbleColumnFixedPolydisperse\n              - [ ] bubbleColumnPolydisperse\n              - [ ] mixerVessel2D\n              - [ ] trickleBed\n      - [ ] reactingTwoPhaseEulerFoam\n          - [ ] LES\n              - [ ] bubbleColumn\n          - [ ] RAS\n              - [ ] LBend\n              - [ ] bubbleColumn\n              - [ ] bubbleColumnEvaporatingReacting\n              - [ ] bubbleColumnPolydisperse\n              - [ ] fluidisedBed\n              - [ ] wallBoiling\n              - [ ] wallBoiling1D\n              - [ ] wallBoilingIATE\n              - [ ] wallBoilingPolyDisperse\n          - [ ] laminar\n              - [ ] bubbleColumn\n              - [ ] bubbleColumnEvaporating\n              - [ ] bubbleColumnEvaporatingDissolving\n              - [ ] bubbleColumnIATE\n              - [ ] fluidisedBed\n              - [ ] injection\n              - [ ] mixerVessel2D\n              - [ ] steamInjection\n      - [ ] twoLiquidMixingFoam\n          - [ ] lockExchange\n      - [ ] twoPhaseEulerFoam\n          - [ ] LES\n              - [ ] bubbleColumn\n          - [ ] RAS\n              - [ ] bubbleColumn\n              - [ ] fluidisedBed\n          - [ ] laminar\n              - [ ] bubbleColumn\n              - [ ] bubbleColumnIATE\n              - [ ] fluidisedBed\n              - [ ] injection\n              - [ ] mixerVessel2D\n  - [ ] resources\n      - [ ] geometry\n  - [x] stressAnalysis\n      - [x] solidDisplacementFoam\n          - [x] plateHole\n      - [x] solidEquilibriumDisplacementFoam\n          - [x] beamEndLoad\n</details>\n\n<p align="right">(<a href="#top">back to top</a>)</p>\n\n\n\n<!-- CONTRIBUTING -->\n## Contributing\n\nContributions are what make the open source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.\n\nIf you have a suggestion that would make this better, please fork the repository and create a pull request. You can also simply open an issue with the tag "enhancement".\nDon\'t forget to give the project a star! Thanks again!\n\n1. Fork the Project\n2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)\n3. Commit your Changes (`git commit -m \'Add some AmazingFeature\'`)\n4. Push to the Branch (`git push origin feature/AmazingFeature`)\n5. Open a Pull Request\n\n<p align="right">(<a href="#top">back to top</a>)</p>\n\n\n\n<!-- LICENSE -->\n## License\n\nDistributed under the GPL-3.0 License. See `LICENSE.txt` for more information.\n\n<p align="right">(<a href="#top">back to top</a>)</p>\n\n\n\n<!-- CONTACT -->\n## Contact\n\nIydon Liang - [@iydon](https://github.com/iydon) - liangiydon_AT_gmail.com\n\n<p align="right">(<a href="#top">back to top</a>)</p>\n\n\n\n<!-- MARKDOWN LINKS & IMAGES -->\n[contributors-shield]: https://img.shields.io/github/contributors/iydon/of.yaml.svg?style=for-the-badge\n[contributors-url]: https://github.com/iydon/of.yaml/graphs/contributors\n[forks-shield]: https://img.shields.io/github/forks/iydon/of.yaml.svg?style=for-the-badge\n[forks-url]: https://github.com/iydon/of.yaml/network/members\n[stars-shield]: https://img.shields.io/github/stars/iydon/of.yaml.svg?style=for-the-badge\n[stars-url]: https://github.com/iydon/of.yaml/stargazers\n[issues-shield]: https://img.shields.io/github/issues/iydon/of.yaml.svg?style=for-the-badge\n[issues-url]: https://github.com/iydon/of.yaml/issues\n[license-shield]: https://img.shields.io/github/license/iydon/of.yaml.svg?style=for-the-badge\n[license-url]: https://github.com/iydon/of.yaml/blob/master/LICENSE.txt\n',
    'author': 'Iydon Liang',
    'author_email': 'liangiydon@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/iydon/of.yaml',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
