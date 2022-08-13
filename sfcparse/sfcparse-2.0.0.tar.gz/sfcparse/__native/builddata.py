# builddata
#########################################################################################################
# Imports
from .importfile import SfcparseFileData

#########################################################################################################
# Build manual SfcparseFileData (python data)
def builddata() -> SfcparseFileData:
    """
    Returns an empty SfcparseFileData obj to manually build python data with sfcparse features
    
    Assign the output to var

    Literally just use attribute assignment as you normally would

    [Example]

    object.attribute1 = [1,2,3]

    object.attribute2 = 'string data'

    More information on object features: https://docs.sfcparse.org/docs/tools/build-data/python-data-build
    """
    return SfcparseFileData('', True, True)
