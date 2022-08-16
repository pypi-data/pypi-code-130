from typing import List

from .exceptions import LimsError
from .dataclasses import Query
from .queries import EXP_WKFT_QUERY, IMAGE_WKFT_QUERY, PROBE_WKFT_QUERY

EXP_FILE_TYPES = [
    "NewstepConfiguration",
    "EcephysReplayStimulus",
    "EcephysAreaClassifications",
    "SideDlcOutputFile",
    "EyeTracking Ellipses",
    "RawEyeTrackingVideo",
    "RawEyeTrackingVideoMetadata",
    "EcephysSurgeryNotes",
    "RawFaceTrackingVideoMetadata",
    "RawBehaviorTrackingVideoMetadata",
    "StimulusPickle",
    "EyeDlcOutputFile",
    "OptoPickle",
    "MappingPickle",
    "RawBehaviorTrackingVideo",
    "FaceDlcOutputFile",
    "EcephysRigSync",
    "EcephysPlatformFile",
    "RawFaceTrackingVideo",
]

IMAGE_FILE_TYPES = [
    "EcephysPostStimulusRight",
    "EcephysPostInsertionLeft",
    "EcephysInsertionLocationImage",
    "EcephysPostInsertionRight",
    "EcephysPreExperimentRight",
    "EcephysPostExperimentLeft",
    "EcephysPreInsertionLeft",
    "EcephysFiducialImage",
    "EcephysPreInsertionRight",
    "EcephysBrainSurfaceRight",
    "EcephysPostExperimentRight",
    "EcephysBrainSurfaceLeft",
    "EcephysPostStimulusLeft",
    "EcephysPreExperimentLeft",
    "EcephysOverlayImage",
]

PROBE_FILE_TYPES = [
    "EcephysSortedParams",
    "EcephysSortedWhiteningMatInv",
    "EcephysSortedTemplates",
    "EcephysSortedSpikeClusters",
    "EcephysSortedChannelMap",
    "EcephysChannelStates",
    "EcephysSortedSpikeTimes",
    "EcephysSortedProbeInfo",
    "EcephysSortedChannelPositions",
    "EcephysTemplatesInd",
    "EcephysSortedSpikeTemplates",
    "EcephysSortedMeanWaveforms",
    "EcephysSortedEventTimestamps",
    "EcephysSortedSimilarTemplates",
    "EcephysSortedLfpTimestamps",
    "EcephysSortedMetrics",
    "EcephysProbeRawData",
    "EcephysSortedLfpContinuous",
    "EcephysSortedWhiteningMat",
    "EcephysSortedAmplitudes",
]

WKFT = {
    **(
        {
            name: {
                "template": EXP_WKFT_QUERY,
                "filters": [
                    (
                        "wkft",
                        name,
                    )
                ],
                "return_name": "wkf_path",
            }
            for name in EXP_FILE_TYPES
        }
    ),
    **(
        {
            name: {
                "template": IMAGE_WKFT_QUERY,
                "filters": [
                    (
                        "image_type",
                        name,
                    )
                ],
                "return_name": "image_path",
            }
            for name in IMAGE_FILE_TYPES
        }
    ),
    **(
        {
            name: {
                "template": PROBE_WKFT_QUERY,
                "filters": [
                    (
                        "wkft",
                        name,
                    )
                ],
                "return_name": "wkf_path",
            }
            for name in PROBE_FILE_TYPES
        }
    ),
}


def wkft_to_Query(wkft: str, exp_id: str) -> Query:
    """Transforms a well known file type (wkft) into a query.

    :param wkft: well known file type name
    :param exp_id: lims experiment id

    :returns: resolved query
    """
    try:
        wkft_dict = WKFT[wkft]
    except KeyError:
        raise LimsError("Unsupported wkft=%s" % wkft)

    return Query(
        query_str=wkft_dict["template"].format(exp_id),
        filters=wkft_dict["filters"],
        return_name=wkft_dict["return_name"],
    )


def get_wkft_names() -> list[str]:
    """Gets a list of all supported well known file types.

    :returns: List of supported well known file types.
    """
    return [
        *EXP_FILE_TYPES,
        *IMAGE_FILE_TYPES,
        *PROBE_FILE_TYPES,
    ]
