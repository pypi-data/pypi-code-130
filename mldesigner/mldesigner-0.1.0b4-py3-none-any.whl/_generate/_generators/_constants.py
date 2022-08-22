# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azure.ai.ml.constants import NodeType
from azure.ai.ml.entities._builders import Command, Parallel
from azure.ai.ml._internal.entities import (
    Scope,
    InternalBaseNode,
    Command as InternalCommand,
    Distributed,
    Parallel as InternalParallel,
    DataTransfer as DataTransfer,
    HDInsight,
    Hemera,
    Starlite,
    Ae365exepool,
)
from azure.ai.ml._internal._schema.component import NodeType as V1NodeType

V2_COMPONENT_TO_NODE = {
    NodeType.COMMAND: Command,
    NodeType.PARALLEL: Parallel,
}

V1_COMPONENT_TO_NODE = {
    V1NodeType.SCOPE: Scope,
    V1NodeType.COMMAND: InternalCommand,
    V1NodeType.PARALLEL: InternalParallel,
    V1NodeType.DATA_TRANSFER: DataTransfer,
    V1NodeType.DISTRIBUTED: Distributed,
    V1NodeType.HDI: HDInsight,
    V1NodeType.STARLITE: Starlite,
    V1NodeType.HEMERA: Hemera,
    V1NodeType.AE365EXEPOOL: Ae365exepool,
    # TODO: add other internal components
    V1NodeType.SWEEP: InternalBaseNode,
    V1NodeType.PIPELINE: InternalBaseNode,
}

COMPONENT_TO_NODE = {**V2_COMPONENT_TO_NODE, **V1_COMPONENT_TO_NODE}
