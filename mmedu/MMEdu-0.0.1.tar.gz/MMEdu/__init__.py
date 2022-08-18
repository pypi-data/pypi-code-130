from ensurepip import version
from .Classification import MMClassification
from .Detection import MMDetection
# from .Generation_Edu import MMGeneration
# from .Pose_Edu import MMPose
# from .Base_Edu import MMBase
from .version import __version__

__all__ = [
    'MMClassification',
    'MMDetection',
    '__version__',
    # 'MMGeneration',
    # 'MMPose'
    # 'MMBase',
]
