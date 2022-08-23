"""Interface for the MDF dataengine library.

Warnings
--------
Vendors and clients should not develop scripts or applications against
this module. The contents may change at any time without warning.

"""
###############################################################################
#
# (C) Copyright 2020, Maptek Pty Ltd. All rights reserved.
#
###############################################################################

# pylint: disable=line-too-long
# pylint: disable=invalid-name;reason=Names match C++ names.
import ctypes
from .types import (T_ReadHandle, T_ObjectHandle, T_NodePathHandle,
                    T_AttributeId, T_AttributeValueType, T_ContainerIterator,
                    T_TypeIndex, T_MessageHandle, T_ObjectWatcherHandle)
from .util import singleton, CApiUnknownError
from .wrapper_base import WrapperBase

@singleton
class DataEngine(WrapperBase):
  """Provides access to functions available from the mdf_dataengine.dll"""
  def __init__(self):
    super().__init__("mdf_dataengine", "mapteksdk.capi.dataengine")
    self.is_connected = False

  @staticmethod
  def method_prefix():
    return "DataEngine"

  def capi_functions(self):
    return [
      # Functions changed in version 0.
      # Format:
      # "name" : (return_type, arg_types)
      {"DataEngineErrorCode" : (ctypes.c_uint32, None),
       "DataEngineErrorMessage" : (ctypes.c_char_p, None),
       "DataEngineConnect" : (ctypes.c_bool, [ctypes.c_bool, ]),
       "DataEngineCreateLocal" : (ctypes.c_bool, None),
       "DataEngineOpenProject" : (ctypes.c_uint16, [ctypes.c_char_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_uint32, ]),
       "DataEngineCloseProject" : (ctypes.c_void_p, [ctypes.c_uint16, ]),
       "DataEngineDisconnect" : (ctypes.c_void_p, [ctypes.c_bool, ]),
       "DataEngineDeleteStaleLockFile" : (ctypes.c_bool, [ctypes.c_char_p, ]),
       "DataEngineFlushProject" : (ctypes.c_bool, [ctypes.c_uint16, ]),
       "DataEngineObjectHandleFromString" : (ctypes.c_bool, [ctypes.c_char_p, ctypes.POINTER(T_ObjectHandle), ]),
       "DataEngineObjectHandleIcon" : (ctypes.c_uint32, [T_ObjectHandle, ctypes.c_char_p, ctypes.c_uint64, ]),
       "DataEngineObjectHandleFromNodePath" : (ctypes.c_bool, [T_NodePathHandle, ctypes.POINTER(T_ObjectHandle), ]),
       "DataEngineObjectHandleNodePath" : (T_NodePathHandle, [T_ObjectHandle, ]),
       "DataEngineObjectParentId" : (T_ObjectHandle, [T_ObjectHandle, ]),
       "DataEngineProjectRoot" : (T_ObjectHandle, [ctypes.c_uint16, ]),
       "DataEngineObjectHandleIsOrphan" : (ctypes.c_bool, [T_ObjectHandle, ]),
       "DataEngineObjectHandleExists" : (ctypes.c_bool, [T_ObjectHandle, ]),
       "DataEngineObjectHandleIsInRecycleBin" : (ctypes.c_bool, [T_ObjectHandle, ]),
       "DataEngineObjectBackEnd" : (ctypes.c_bool, [T_ObjectHandle, ctypes.POINTER(ctypes.c_uint16), ]),
       "DataEngineObjectDynamicType" : (T_TypeIndex, [T_ObjectHandle, ]),
       "DataEngineObjectIsLocked" : (ctypes.c_bool, [T_ObjectHandle, ]),
       "DataEngineNullType" : (T_TypeIndex, None),
       "DataEngineObjectType" : (T_TypeIndex, None),
       "DataEngineContainerType" : (T_TypeIndex, None),
       "DataEngineSlabType" : (T_TypeIndex, None),
       "DataEngineSlabOfBoolType" : (T_TypeIndex, None),
       "DataEngineSlabOfInt8uType" : (T_TypeIndex, None),
       "DataEngineSlabOfInt8sType" : (T_TypeIndex, None),
       "DataEngineSlabOfInt16uType" : (T_TypeIndex, None),
       "DataEngineSlabOfInt16sType" : (T_TypeIndex, None),
       "DataEngineSlabOfInt32uType" : (T_TypeIndex, None),
       "DataEngineSlabOfInt32sType" : (T_TypeIndex, None),
       "DataEngineSlabOfInt64uType" : (T_TypeIndex, None),
       "DataEngineSlabOfInt64sType" : (T_TypeIndex, None),
       "DataEngineSlabOfFloat32Type" : (T_TypeIndex, None),
       "DataEngineSlabOfFloat64Type" : (T_TypeIndex, None),
       "DataEngineSlabOfStringType" : (T_TypeIndex, None),
       "DataEngineSlabOfObjectIdType" : (T_TypeIndex, None),
       "DataEngineTypeParent" : (T_TypeIndex, [T_TypeIndex, ]),
       "DataEngineTypeName" : (ctypes.c_char_p, [T_TypeIndex, ]),
       "DataEngineFindTypeByName" : (T_TypeIndex, [ctypes.c_char_p, ]),
       "DataEngineTypeIsA" : (ctypes.c_bool, [T_TypeIndex, T_TypeIndex, ]),
       "DataEngineObjectWatcherFree" : (ctypes.c_void_p, [T_ObjectWatcherHandle, ]),
       "DataEngineObjectWatcherNewContentAndChildWatcher" : (T_ObjectWatcherHandle, [T_ObjectHandle, ctypes.c_void_p, ]),
       "DataEngineObjectWatcherNewNameWatcher" : (T_ObjectWatcherHandle, [T_ObjectHandle, ctypes.c_void_p, ]),
       "DataEngineObjectWatcherNewPathWatcher" : (T_ObjectWatcherHandle, [T_ObjectHandle, ctypes.c_void_p, ]),
       "DataEngineNodePathFree" : (ctypes.c_void_p, [T_NodePathHandle, ]),
       "DataEngineNodePathLeaf" : (ctypes.c_uint32, [T_NodePathHandle, ctypes.c_char_p, ctypes.c_uint64, ]),
       "DataEngineNodePathStem" : (T_NodePathHandle, [T_NodePathHandle, ]),
       "DataEngineNodePathHead" : (ctypes.c_uint32, [T_NodePathHandle, ctypes.c_char_p, ctypes.c_uint64, ]),
       "DataEngineNodePathTail" : (T_NodePathHandle, [T_NodePathHandle, ]),
       "DataEngineNodePathIsValid" : (ctypes.c_bool, [T_NodePathHandle, ]),
       "DataEngineNodePathIsNull" : (ctypes.c_bool, [T_NodePathHandle, ]),
       "DataEngineNodePathIsRoot" : (ctypes.c_bool, [T_NodePathHandle, ]),
       "DataEngineNodePathIsHidden" : (ctypes.c_bool, [T_NodePathHandle, ]),
       "DataEngineNodePathToString" : (ctypes.c_uint32, [T_NodePathHandle, ctypes.c_char_p, ctypes.c_uint64, ]),
       "DataEngineNodePathFromString" : (T_NodePathHandle, [ctypes.c_char_p, ]),
       "DataEngineNodePathEquality" : (ctypes.c_bool, [T_NodePathHandle, T_NodePathHandle, ]),
       "DataEngineReadObject" : (ctypes.POINTER(T_ReadHandle), [T_ObjectHandle, ]),
       "DataEngineEditObject" : (ctypes.POINTER(T_ReadHandle), [T_ObjectHandle, ]),
       "DataEngineCloseObject" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineDeleteObject" : (ctypes.c_bool, [T_ObjectHandle, ]),
       "DataEngineCloneObject" : (T_ObjectHandle, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint16, ]),
       "DataEngineAssignObject" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineGetObjectCreationDateTime" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), ctypes.POINTER(ctypes.c_int64), ]),
       "DataEngineGetObjectModificationDateTime" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), ctypes.POINTER(ctypes.c_int64), ]),
       "DataEngineGetObjectRevisionNumber" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), ctypes.POINTER(ctypes.c_uint32), ]),
       "DataEngineGetObjectIdRevisionNumber" : (ctypes.c_bool, [T_ObjectHandle, ctypes.POINTER(ctypes.c_uint32), ]),
       "DataEngineObjectToJson" : (ctypes.c_uint32, [ctypes.POINTER(T_ReadHandle), ctypes.c_char_p, ctypes.c_uint64, ]),
       "DataEngineCreateContainer" : (T_ObjectHandle, None),
       "DataEngineIsContainer" : (ctypes.c_bool, [T_ObjectHandle, ]),
       "DataEngineContainerElementCount" : (ctypes.c_uint32, [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineContainerFind" : (T_ObjectHandle, [ctypes.POINTER(T_ReadHandle), ctypes.c_char_p, ]),
       "DataEngineContainerBegin" : (T_ContainerIterator, [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineContainerEnd" : (T_ContainerIterator, [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineContainerPreviousElement" : (T_ContainerIterator, [ctypes.POINTER(T_ReadHandle), T_ContainerIterator, ]),
       "DataEngineContainerNextElement" : (T_ContainerIterator, [ctypes.POINTER(T_ReadHandle), T_ContainerIterator, ]),
       "DataEngineContainerFindElement" : (T_ContainerIterator, [ctypes.POINTER(T_ReadHandle), ctypes.c_char_p, ]),
       "DataEngineContainerElementName" : (ctypes.c_uint32, [ctypes.POINTER(T_ReadHandle), T_ContainerIterator, ctypes.c_char_p, ctypes.c_uint64, ]),
       "DataEngineContainerElementObject" : (T_ObjectHandle, [ctypes.POINTER(T_ReadHandle), T_ContainerIterator, ]),
       "DataEngineContainerInsert" : (T_ContainerIterator, [ctypes.POINTER(T_ReadHandle), T_ContainerIterator, ctypes.c_char_p, T_ObjectHandle, ctypes.c_bool, ]),
       "DataEngineContainerAppend" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_char_p, T_ObjectHandle, ctypes.c_bool, ]),
       "DataEngineContainerRemoveElement" : (T_ContainerIterator, [ctypes.POINTER(T_ReadHandle), T_ContainerIterator, ctypes.c_bool, ]),
       "DataEngineContainerRemove" : (T_ObjectHandle, [ctypes.POINTER(T_ReadHandle), ctypes.c_char_p, ]),
       "DataEngineContainerRemoveObject" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_ObjectHandle, ctypes.c_bool, ]),
       "DataEngineContainerReplaceElement" : (T_ContainerIterator, [ctypes.POINTER(T_ReadHandle), T_ContainerIterator, T_ObjectHandle, ]),
       "DataEngineContainerReplaceObject" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_ObjectHandle, T_ObjectHandle, ctypes.c_bool, ]),
       "DataEngineContainerPurge" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfBoolCreate" : (T_ObjectHandle, None),
       "DataEngineSlabOfInt8uCreate" : (T_ObjectHandle, None),
       "DataEngineSlabOfInt8sCreate" : (T_ObjectHandle, None),
       "DataEngineSlabOfInt16uCreate" : (T_ObjectHandle, None),
       "DataEngineSlabOfInt16sCreate" : (T_ObjectHandle, None),
       "DataEngineSlabOfInt32uCreate" : (T_ObjectHandle, None),
       "DataEngineSlabOfInt32sCreate" : (T_ObjectHandle, None),
       "DataEngineSlabOfInt64uCreate" : (T_ObjectHandle, None),
       "DataEngineSlabOfInt64sCreate" : (T_ObjectHandle, None),
       "DataEngineSlabOfFloat32Create" : (T_ObjectHandle, None),
       "DataEngineSlabOfFloat64Create" : (T_ObjectHandle, None),
       "DataEngineSlabOfStringCreate" : (T_ObjectHandle, None),
       "DataEngineSlabOfObjectIdCreate" : (T_ObjectHandle, None),
       "DataEngineSlabElementCount" : (ctypes.c_uint64, [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabSetElementCount" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ]),
       "DataEngineSlabOfBoolArrayBeginR" : (ctypes.POINTER(ctypes.c_bool), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt8uArrayBeginR" : (ctypes.POINTER(ctypes.c_uint8), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt8sArrayBeginR" : (ctypes.POINTER(ctypes.c_int8), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt16uArrayBeginR" : (ctypes.POINTER(ctypes.c_uint16), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt16sArrayBeginR" : (ctypes.POINTER(ctypes.c_int16), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt32uArrayBeginR" : (ctypes.POINTER(ctypes.c_uint32), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt32sArrayBeginR" : (ctypes.POINTER(ctypes.c_int32), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt64uArrayBeginR" : (ctypes.POINTER(ctypes.c_uint64), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt64sArrayBeginR" : (ctypes.POINTER(ctypes.c_int64), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfFloat32ArrayBeginR" : (ctypes.POINTER(ctypes.c_float), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfFloat64ArrayBeginR" : (ctypes.POINTER(ctypes.c_double), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfObjectIdArrayBeginR" : (ctypes.POINTER(T_ObjectHandle), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfBoolArrayBeginRW" : (ctypes.POINTER(ctypes.c_bool), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt8uArrayBeginRW" : (ctypes.POINTER(ctypes.c_uint8), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt8sArrayBeginRW" : (ctypes.POINTER(ctypes.c_int8), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt16uArrayBeginRW" : (ctypes.POINTER(ctypes.c_uint16), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt16sArrayBeginRW" : (ctypes.POINTER(ctypes.c_int16), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt32uArrayBeginRW" : (ctypes.POINTER(ctypes.c_uint32), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt32sArrayBeginRW" : (ctypes.POINTER(ctypes.c_int32), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt64uArrayBeginRW" : (ctypes.POINTER(ctypes.c_uint64), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfInt64sArrayBeginRW" : (ctypes.POINTER(ctypes.c_int64), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfFloat32ArrayBeginRW" : (ctypes.POINTER(ctypes.c_float), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfFloat64ArrayBeginRW" : (ctypes.POINTER(ctypes.c_double), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfObjectIdArrayBeginRW" : (ctypes.POINTER(T_ObjectHandle), [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineSlabOfBoolReadValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_bool), ]),
       "DataEngineSlabOfInt8uReadValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint8), ]),
       "DataEngineSlabOfInt8sReadValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_int8), ]),
       "DataEngineSlabOfInt16uReadValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint16), ]),
       "DataEngineSlabOfInt16sReadValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_int16), ]),
       "DataEngineSlabOfInt32uReadValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint32), ]),
       "DataEngineSlabOfInt32sReadValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_int32), ]),
       "DataEngineSlabOfInt64uReadValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64), ]),
       "DataEngineSlabOfInt64sReadValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_int64), ]),
       "DataEngineSlabOfFloat32ReadValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_float), ]),
       "DataEngineSlabOfFloat64ReadValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_double), ]),
       "DataEngineSlabOfObjectIdReadValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(T_ObjectHandle), ]),
       "DataEngineSlabOfBoolSetValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_bool), ]),
       "DataEngineSlabOfInt8uSetValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint8), ]),
       "DataEngineSlabOfInt8sSetValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_int8), ]),
       "DataEngineSlabOfInt16uSetValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint16), ]),
       "DataEngineSlabOfInt16sSetValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_int16), ]),
       "DataEngineSlabOfInt32uSetValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint32), ]),
       "DataEngineSlabOfInt32sSetValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_int32), ]),
       "DataEngineSlabOfInt64uSetValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_uint64), ]),
       "DataEngineSlabOfInt64sSetValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_int64), ]),
       "DataEngineSlabOfFloat32SetValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_float), ]),
       "DataEngineSlabOfFloat64SetValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(ctypes.c_double), ]),
       "DataEngineSlabOfObjectIdSetValues" : (ctypes.c_void_p, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_uint64, ctypes.POINTER(T_ObjectHandle), ]),
       "DataEngineSlabOfStringReadValue" : (ctypes.c_uint64, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_char_p, ctypes.c_uint64, ]),
       "DataEngineSlabOfStringSetValue" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), ctypes.c_uint64, ctypes.c_char_p, ctypes.c_uint64, ]),
       "DataEngineGetAttributeId" : (T_AttributeId, [ctypes.c_char_p, ]),
       "DataEngineGetAttributeName" : (ctypes.c_uint64, [T_AttributeId, ctypes.c_char_p, ctypes.c_uint64, ]),
       "DataEngineGetAttributeList" : (ctypes.c_uint64, [ctypes.POINTER(T_ReadHandle), ctypes.c_void_p, ctypes.c_uint64, ]),
       "DataEngineGetAttributeValueType" : (T_AttributeValueType, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ]),
       "DataEngineGetAttributeValueBool" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.POINTER(ctypes.c_bool), ]),
       "DataEngineGetAttributeValueInt8s" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.POINTER(ctypes.c_int8), ]),
       "DataEngineGetAttributeValueInt8u" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.POINTER(ctypes.c_uint8), ]),
       "DataEngineGetAttributeValueInt16s" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.POINTER(ctypes.c_int16), ]),
       "DataEngineGetAttributeValueInt16u" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.POINTER(ctypes.c_uint16), ]),
       "DataEngineGetAttributeValueInt32s" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.POINTER(ctypes.c_int32), ]),
       "DataEngineGetAttributeValueInt32u" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.POINTER(ctypes.c_uint32), ]),
       "DataEngineGetAttributeValueInt64s" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.POINTER(ctypes.c_int64), ]),
       "DataEngineGetAttributeValueInt64u" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.POINTER(ctypes.c_uint64), ]),
       "DataEngineGetAttributeValueFloat32" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.POINTER(ctypes.c_float), ]),
       "DataEngineGetAttributeValueFloat64" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.POINTER(ctypes.c_double), ]),
       "DataEngineGetAttributeValueDateTime" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.POINTER(ctypes.c_int64), ]),
       "DataEngineGetAttributeValueDate" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.POINTER(ctypes.c_int32), ctypes.POINTER(ctypes.c_uint8), ctypes.POINTER(ctypes.c_uint8), ]),
       "DataEngineGetAttributeValueString" : (ctypes.c_uint64, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_char_p, ctypes.c_uint64, ]),
       "DataEngineSetAttributeNull" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ]),
       "DataEngineSetAttributeBool" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_bool, ]),
       "DataEngineSetAttributeInt8s" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_int8, ]),
       "DataEngineSetAttributeInt8u" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_uint8, ]),
       "DataEngineSetAttributeInt16s" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_int16, ]),
       "DataEngineSetAttributeInt16u" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_uint16, ]),
       "DataEngineSetAttributeInt32s" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_int32, ]),
       "DataEngineSetAttributeInt32u" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_uint32, ]),
       "DataEngineSetAttributeInt64s" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_int64, ]),
       "DataEngineSetAttributeInt64u" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_uint64, ]),
       "DataEngineSetAttributeFloat32" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_float, ]),
       "DataEngineSetAttributeFloat64" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_double, ]),
       "DataEngineSetAttributeDateTime" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_int64, ]),
       "DataEngineSetAttributeDate" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_int32, ctypes.c_uint8, ctypes.c_uint8, ]),
       "DataEngineSetAttributeString" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ctypes.c_char_p, ]),
       "DataEngineDeleteAttribute" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), T_AttributeId, ]),
       "DataEngineDeleteAllAttributes" : (ctypes.c_bool, [ctypes.POINTER(T_ReadHandle), ]),
       "DataEngineRootContainer" : (T_ObjectHandle, None),
       "DataEngineAppendHandleToMessage" : (ctypes.c_void_p, [T_MessageHandle, T_ObjectHandle, ]),
       "DataEngineCreateMaptekObjFile" : (ctypes.c_bool, [ctypes.c_char_p, T_ObjectHandle, ]),
       "DataEngineCreateMaptekObjJsonFile" : (ctypes.c_bool, [ctypes.c_char_p, T_ObjectHandle, ]),
       "DataEngineReadMaptekObjFile" : (T_ObjectHandle, [ctypes.c_char_p, ]),
       "DataEngineGetSelectedObjectCount" : (ctypes.c_uint32, None),
       "DataEngineGetSelectedObjects" : (ctypes.c_void_p, [ctypes.POINTER(T_ObjectHandle), ]),
       "DataEngineSetSelectedObject" : (ctypes.c_void_p, [T_ObjectHandle, ]),
       "DataEngineSetSelectedObjects" : (ctypes.c_void_p, [ctypes.POINTER(T_ObjectHandle), ctypes.c_uint32, ])},
      # Functions changed in version 1.
      {"DataEngineCApiVersion" : (ctypes.c_uint32, None),
       "DataEngineCApiMinorVersion" : (ctypes.c_uint32, None),

       # New in API version 1.6.
       #
       # The argument should really be a T_EditHandle but
       # DataEngineEditObject() returns a T_ReadHandle. In part because there
       # are cases where a T_EditHandle and T_ReadHandle can be used.
       "DataEngineCancelObjectCommit" : (ctypes.c_uint32, [ctypes.POINTER(T_ReadHandle)]),
       }
    ]

  def Disconnect(self, *args):
    """Handles backwards compatibility with disconnecting from a project."""
    if self.version < (1, 1):
      # There was a bug with this function that meant it would leave the
      # application is a bad state which often result in it crashing.
      self.log.warning("Unable to disconnect from project. This means "
                       "connecting to another project won't work.")
      return

    self.dll.DataEngineDisconnect(*args)

  def TypeIsA(self, object_type, type_index):
    """Wrapper for checking the type of an object."""
    if type_index is None:
      return False
    return self.dll.DataEngineTypeIsA(object_type, type_index)

  def CancelObjectCommit(self, edit_handle):
    """Handles backwards compatibility by ignoring the cancel."""
    if self.version < (1, 6):
      # Do nothing, ignore the cancel in older versions.
      self.log.warning("Cannot cancel the commit of an object due to old "
                       "application version. Some changes may still be "
                       "committed.")
      return None

    if not edit_handle:
      raise ValueError('The edit handle must not be 0')

    return self.dll.DataEngineCancelObjectCommit(edit_handle)

  def GetObjectRevisionNumber(self, read_handle):
    """Get the revision number of an open object.

    Parameters
    ----------
    read_handle : lock
      Read lock on the object whose revision number should be returned.

    Returns
    -------
    int
      The object's revision number.
      This will be None if the application is too old.
    """
    if self.version < (1, 7):
      return None

    revision_number = ctypes.c_uint32(0)
    result = self.dll.DataEngineGetObjectRevisionNumber(
      read_handle, ctypes.byref(revision_number))

    if not result:
      raise CApiUnknownError(self.dll.DataEngineErrorMessage())

    return revision_number.value

  def GetObjectIdRevisionNumber(self, handle):
    """Get the revision number of an object id.

    This allows the revision number to be queried without opening the object.

    Parameters
    ----------
    handle : T_ObjectHandle
      Read lock on the object whose revision number should be returned.

    Returns
    -------
    int
      The object's revision number.
      This will be None if the application is too old.
    """
    if self.version < (1, 7):
      return None

    revision_number = ctypes.c_uint32(0)
    result = self.dll.DataEngineGetObjectIdRevisionNumber(
      handle, ctypes.byref(revision_number))

    if not result:
      raise CApiUnknownError(self.dll.DataEngineErrorMessage())

    return revision_number.value
