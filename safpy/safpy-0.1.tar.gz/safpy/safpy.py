from cmath import nan
import pandas as pd

class StructuralSchema():

    def __init__(self):

        self.modelDict = {
            'fields' : [
                'Name',
                'Description',
                'Discipline',
                'Level of detail',
                'Status',
                'Owner',
                'Revision number',
                'Created',
                'Last update',
                'Source type',
                'Source application',
                'Source company',
                'Global coordinate system',
                'LCS of cross-section',
                'System of units',
                'SAF Version',
                'Module version',
                'Ignored objects',
                'Ignored groups',
                'Id'
                ],
            'responses': [
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                ''
                ]
        }

        self.projectDict = {
            'fields' : [
                'Name',
                'Description',
                'Project nr',
                'Created',
                'Last update',
                'Project type',
                'Project kind',
                'Building type',
                'Status',
                'Location'
                        ],
            'responses' :[
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                '',
                ''
            ]
        }

        self.materialDict = {
            'Name' : [],
            'Type' : [],
            'Subtype' : [],
            'Quality' : [],
            'Unit mass [kg/m3]' : [],
            'E modulus [MPa]' : [],
            'G modulus [MPa]' : [],
            'Poisson Coefficient' : [],
            'Thermal expansion [1/K]' : [],
            'Design properties' : [],
            'Id' : []
            }

        self.sectionDict = {
            'Name' : [],
            'Material' : [],
            'Cross-section type' : [],
            'Shape' : [],
            'Parameters [mm]' : [],
            'Profile' : [],
            'Form code' : [],
            'Description ID of the profile' : [],
            'Iy [m4]' : [],
            'Iz [m4]' : [],
            'It [m4]' : [],
            'Iw [m6]' : [],
            'Wply [m3]' : [],
            'Wplz [m3]' : [],
            'Id' : []
        }

        self.pointDict = {
            'Name' : [],
            'Coordinate X [m]' : [],
            'Coordinate Y [m]' : [],
            'Coordinate Z [m]' : [],
            'Id' : []
        }

    def getModelInfo(self):

        return self.modelDict

    def addModelInfo(self, 
                     modelName: str = "", 
                     modelDesc: str = "", 
                     modelDisp: str = "", 
                     modelDetail: str = "", 
                     modelStatus: str = "", 
                     modelOwner: str = "", 
                     modelRevNum: str = "", 
                     modelCreated: str = "", 
                     modelLastUpdate: str = "", 
                     modelSourceType: str = "", 
                     modelSourceApp: str = "", 
                     modelSourceCompany: str = "", 
                     modelGlobalCoords: str = "", 
                     modelLCS: str = "", 
                     modelUnits: str = "", 
                     modelSAFVersion: str = "", 
                     modelModuleVersion: str = "", 
                     modelIgnoredObjects: str = "", 
                     modelIgnoredGroups: str = "", 
                     modelID: str = ""):

        self.modelName = modelName
        self.modelDesc = modelDesc
        self.modelDisp = modelDisp
        self.modelDetail = modelDetail
        self.modelStatus = modelStatus
        self.modelOwner = modelOwner
        self.modelRevNum = modelRevNum
        self.modelCreated = modelCreated
        self.modelLastUpdate = modelLastUpdate
        self.modelSourceType = modelSourceType
        self.modelSourceApp = modelSourceApp
        self.modelSourceCompany = modelSourceCompany
        self.modelGlobalCoords = modelGlobalCoords
        self.modelLCS = modelLCS
        self.modelUnits = modelUnits
        self.modelSAFVersion = modelSAFVersion
        self.modelModuleVersion = modelModuleVersion
        self.modelIgnoredObjects = modelIgnoredObjects
        self.modelIgnoredGroups = modelIgnoredGroups
        self.modelID = modelID

        self.modelDict['responses'][0]=(self.modelName)
        self.modelDict['responses'][1]=(self.modelDesc)
        self.modelDict['responses'][2]=(self.modelDisp)
        self.modelDict['responses'][3]=(self.modelDetail)
        self.modelDict['responses'][4]=(self.modelStatus)
        self.modelDict['responses'][5]=(self.modelOwner)
        self.modelDict['responses'][6]=(self.modelRevNum)
        self.modelDict['responses'][7]=(self.modelCreated)
        self.modelDict['responses'][8]=(self.modelLastUpdate)
        self.modelDict['responses'][9]=(self.modelSourceType)
        self.modelDict['responses'][10]=(self.modelSourceApp)
        self.modelDict['responses'][11]=(self.modelSourceCompany)
        self.modelDict['responses'][12]=(self.modelGlobalCoords)
        self.modelDict['responses'][13]=(self.modelLCS)
        self.modelDict['responses'][14]=(self.modelUnits)
        self.modelDict['responses'][15]=(self.modelSAFVersion)
        self.modelDict['responses'][16]=(self.modelModuleVersion)
        self.modelDict['responses'][17]=(self.modelIgnoredObjects)
        self.modelDict['responses'][18]=(self.modelIgnoredGroups)
        self.modelDict['responses'][19]=(self.modelID)

    def getProjectInfo(self):

        return self.projectDict

    def addProjectInfo(self, 
                       projectName: str = '', 
                       projectDesc: str = '', 
                       projectNr: str = '', 
                       projectCreated: str = '',
                       projectLastUpdate: str = '', 
                       projectType: str = '',
                       projectKind: str = '', 
                       projectBuildingType: str = '', 
                       projectStatus: str = '', 
                       projectLocation: str = ''):

        self.projectName = projectName
        self.projectDesc = projectDesc
        self.projectNr = projectNr
        self.projectCreated = projectCreated
        self.projectLastUpdate = projectLastUpdate
        self.projectType = projectType
        self.projectKind = projectKind
        self.projectBuildingType = projectBuildingType
        self.projectStatus = projectStatus
        self.projectLocation = projectLocation

        self.projectDict['responses'][0]=(self.projectName)
        self.projectDict['responses'][1]=(self.projectDesc)
        self.projectDict['responses'][2]=(self.projectNr)
        self.projectDict['responses'][3]=(self.projectCreated)
        self.projectDict['responses'][4]=(self.projectLastUpdate)
        self.projectDict['responses'][5]=(self.projectType)
        self.projectDict['responses'][6]=(self.projectKind)
        self.projectDict['responses'][7]=(self.projectBuildingType)
        self.projectDict['responses'][8]=(self.projectStatus)
        self.projectDict['responses'][9]=(self.projectLocation)

    def getMaterialInfo(self):

        return self.materialDict

    def addMaterial(self, 
                    materialName: str = "", 
                    materialType: str = "", 
                    materialSubtype: str = "", 
                    materialQuality: str = "", 
                    materialUnitMass: float = None, 
                    materialEMod: float = None, 
                    materialGMod: float = None, 
                    materialPoisson: float = None, 
                    materialThermal: float = None,  
                    materialDesignProps: float = None, 
                    materialId: int = None):

        self.materialName = materialName
        self.materialType = materialType
        self.materialSubtype = materialSubtype
        self.materialQuality= materialQuality
        self.materialUnitMass = materialUnitMass
        self.materialEMod = materialEMod
        self.materialGMod = materialGMod
        self.materialPoisson = materialPoisson
        self.materialThermal = materialThermal
        self.materialDesignProps = materialDesignProps
        self.materialId = materialId

        self.materialDict['Name'].append(self.materialName)
        self.materialDict['Type'].append(self.materialType)
        self.materialDict['Subtype'].append(self.materialSubtype)
        self.materialDict['Quality'].append(self.materialQuality)
        self.materialDict['Unit mass [kg/m3]'].append(self.materialUnitMass)
        self.materialDict['E modulus [MPa]'].append(self.materialEMod)
        self.materialDict['G modulus [MPa]'].append(self.materialGMod)
        self.materialDict['Poisson Coefficient'].append(self.materialPoisson)
        self.materialDict['Thermal expansion [1/K]'].append(self.materialThermal)
        self.materialDict['Design properties'].append(self.materialDesignProps)
        self.materialDict['Id'].append(self.materialId)

    def getSectionInfo(self):

        return self.sectionDict

    def addSection(self, 
                   sectionName: str = "", 
                   sectionMaterial: str = "",
                   sectionType: str = "",
                   sectionShape: str = "", 
                   sectionParameters: float = None, 
                   sectionProfile: str = "", 
                   sectionFormCode: str = "", 
                   sectionDescription: int = None, 
                   sectionArea: float = None, 
                   sectionIy: float = None, 
                   sectionIz: float = None, 
                   sectionIt: float = None, 
                   sectionIw: float = None, 
                   sectionWply: float = None, 
                   sectionWplz: float = None,
                   sectionId: int = None):

        self.sectionName = sectionName
        self.sectionMaterial = sectionMaterial
        self.sectionType = sectionType
        self.sectionShape = sectionShape
        self.sectionParameters = sectionParameters
        self.sectionProfile = sectionProfile
        self.sectionFormCode = sectionFormCode
        self.sectionDescription = sectionDescription
        self.sectionArea = sectionArea
        self.sectionIy = sectionIy
        self.sectionIz = sectionIz
        self.sectionIt = sectionIt
        self.sectionIw = sectionIw
        self.sectionWply = sectionWply
        self.sectionWplz = sectionWplz
        self.sectionId = sectionId

        self.sectionDict['Name'].append(self.sectionName)
        self.sectionDict['Material'].append(self.sectionMaterial)
        self.sectionDict['Cross-section type'].append(self.sectionType)
        self.sectionDict['Shape'].append(self.sectionShape)
        self.sectionDict['Parameters [mm]'].append(self.sectionParameters)
        self.sectionDict['Profile'].append(self.sectionProfile)
        self.sectionDict['Form code'].append(self.sectionFormCode)
        self.sectionDict['Description ID of the profile'].append(self.sectionDescription) 
        self.sectionDict['Iy [m4]'].append(self.sectionIy)
        self.sectionDict['Iz [m4]'].append(self.sectionIz) 
        self.sectionDict['It [m4]'].append(self.sectionIt) 
        self.sectionDict['Iw [m6]'].append(self.sectionIw) 
        self.sectionDict['Wply [m3]'].append(self.sectionWply)
        self.sectionDict['Wplz [m3]'].append(self.sectionWplz)
        self.sectionDict['Id'].append(self.sectionId)

    def getPointInfo(self):

        return self.pointDict

    def addPoint(self, 
                pointName: str = "", 
                pointX: float = None, 
                pointY: float = None, 
                pointZ: float = None, 
                pointId: int = None):

        self.pointName = pointName
        self.pointX = pointX
        self.pointY = pointY
        self.pointZ = pointZ
        self.pointId = pointId

        self.pointDict['Name'].append(self.pointName)
        self.pointDict['Coordinate X [m]'].append(self.pointX)
        self.pointDict['Coordinate Y [m]'].append(self.pointY)
        self.pointDict['Coordinate Z [m]'].append(self.pointZ)
        self.pointDict['Id'].append(self.pointId)

    def readExcel(self):
        '''
        Read an external xlsx file to define a StructuralSchema object.
        '''

        # read excel sheets
        self.externalModel = pd.read_excel(r"C:\Users\KaratasD\Desktop\Folders\safpy\safGeometryTest.xlsx", sheet_name="Model", index_col=False)
        self.externalProject = pd.read_excel(r"C:\Users\KaratasD\Desktop\Folders\safpy\safGeometryTest.xlsx", sheet_name="Project", index_col=False)
        externalMaterials = pd.read_excel(r"C:\Users\KaratasD\Desktop\Folders\safpy\safGeometryTest.xlsx", sheet_name="StructuralMaterial")

        # assign model information to object dictionary
        if len(self.externalModel.columns) == 2:

            self.modelResponses = self.externalModel.iloc[: ,1].to_list()

            if self.externalModel.columns[1] == 'Unnamed: 1':
                self.modelResponses.insert(0, nan)
            else:
                self.modelResponses.insert(0, self.externalModel.columns[1])
        else:
            pass

        # assign project information to object dictionary
        if len(self.externalProject.columns) == 2:

            self.projectResponses = self.externalProject.iloc[: ,1].to_list()

            if self.externalProject.columns[1] == 'Unnamed: 1':
                self.projectResponses.insert(0, nan)
            else:
                self.projectResponses.insert(0, self.externalProject.columns[1])

        else:
            pass

        # assign material information to the object dictionary
        self.materialDict['Name'] = externalMaterials['Name'].to_list()
        self.materialDict['Type'] = externalMaterials['Type'].to_list()
        self.materialDict['Subtype'] = externalMaterials['Subtype'].to_list()
        self.materialDict['Quality'] = externalMaterials['Quality'].to_list()
        self.materialDict['Unit mass [kg/m3]'] = externalMaterials['Unit mass [kg/m3]'].to_list()
        self.materialDict['E modulus [MPa]'] = externalMaterials['NaE modulus [MPa]me'].to_list()
        self.materialDict['G modulus [MPa]'] = externalMaterials['G modulus [MPa]'].to_list()
        self.materialDict['Poisson Coefficient'] = externalMaterials['Poisson Coefficient'].to_list()
        self.materialDict['Thermal expansion [1/K]'] = externalMaterials['Thermal expansion [1/K]'].to_list()
        self.materialDict['Design properties'] = externalMaterials['Design properties'].to_list()
        self.materialDict['Id'] = externalMaterials['Id'].to_list()

    def exportExcel(self):

        modelFrame = pd.DataFrame(self.modelDict)
        projectFrame = pd.DataFrame(self.projectDict)
        materialFrame = pd.DataFrame(self.materialDict)
        sectionFrame = pd.DataFrame(self.sectionDict)
        pointFrame = pd.DataFrame(self.pointDict)

        safFile = pd.ExcelWriter(r'C:\Users\KaratasD\Desktop\Folders\safpy\mySAF.xlsx')

        modelFrame.to_excel(safFile, sheet_name='Model', index=False, header=False)
        projectFrame.to_excel(safFile, sheet_name='Project', index=False, header=False)
        materialFrame.to_excel(safFile, sheet_name='StructuralMaterial', index=False)
        sectionFrame.to_excel(safFile, sheet_name='StructuralCrossSection', index=False)
        pointFrame.to_excel(safFile, sheet_name='StructuralPointConnection', index=False)

        safFile.save()



