# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""This file includes the type classes which could be used in mldesigner.command_component

.. remarks::

    The following pseudo-code shows how to create a command component with such classes.

    .. code-block:: python

        @command_component(name=f"mldesigner_component_train", display_name="my-train-job")
        def train_func(
            input_param0: Input,
            input_param1: Input(type="uri_folder", path="xxx", mode="ro_mount"),
            output_param: Output(type="uri_folder", path="xxx", mode="rw_mount"),
            int_param0: Input(type="integer", min=-3, max=10, optional=True) = 0,
            int_param1 = 2
            str_param = 'abc',
        ):
            pass

"""
from typing import overload, Union
from inspect import Parameter, signature
from collections import OrderedDict
from mldesigner._exceptions import UserErrorException
from mldesigner._constants import IO_CONSTANTS


# TODO: merge with azure.ai.ml.entities.Input/Output
class _IOBase:
    """Define the base class of Input/Output/Parameter class."""

    def __init__(self, name=None, type=None, description=None, **kwargs):
        """Define the basic properties of io definition."""
        self.name = name
        self.type = type
        self.description = description
        # record extra kwargs and pass to azure.ai.ml.entities.Input/Output for forward compatibility
        self._kwargs = kwargs or {}


class Input(_IOBase):
    """Define an input of a component.

    Default to be a uri_folder Input.

    :param type: The type of the data input. Possible values include:
                        'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', 'integer', 'number', 'string', 'boolean'
    :type type: str
    :param path: The path to which the input is pointing. Could be pointing to local data, cloud data, a registered name, etc.
    :type path: str

    :param mode: The mode of the data input. Possible values are:
                        'ro_mount': Read-only mount the data,
                        'download': Download the data to the compute target,
                        'direct': Pass in the URI as a string
    :type mode: str
    :param min: The min value -- if a smaller value is passed to a job, the job execution will fail
    :type min: Union[integer, float]
    :param max: The max value -- if a larger value is passed to a job, the job execution will fail
    :type max: Union[integer, float]
    :param optional: Determine if this input is optional
    :type optional: bool
    :param description: Description of the input
    :type description: str
    """

    _EMPTY = Parameter.empty

    @overload
    def __init__(
        self,
        *,
        type: str = "uri_folder",
        path: str = None,
        mode: str = "ro_mount",
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize an input of a component.

        :param path: The path to which the input is pointing. Could be pointing to local data, cloud data, a registered name, etc.
        :type path: str
        :param type: The type of the data input. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param mode: The mode of the data input. Possible values are:
                            'ro_mount': Read-only mount the data,
                            'download': Download the data to the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    @overload
    def __init__(
        self,
        *,
        type: str = "number",
        min: float = None,
        max: float = None,
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize a number input

        :param type: The type of the data input. Can only be set to "number".
        :type type: str
        :param min: The min value -- if a smaller value is passed to a job, the job execution will fail
        :type min: float
        :param max: The max value -- if a larger value is passed to a job, the job execution will fail
        :type max: float
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    @overload
    def __init__(
        self,
        *,
        type: str = "integer",
        min: int = None,
        max: int = None,
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize an integer input

        :param type: The type of the data input. Can only be set to "integer".
        :type type: str
        :param min: The min value -- if a smaller value is passed to a job, the job execution will fail
        :type min: integer
        :param max: The max value -- if a larger value is passed to a job, the job execution will fail
        :type max: integer
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    @overload
    def __init__(
        self,
        *,
        type: str = "string",
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize a string input.

        :param type: The type of the data input. Can only be set to "string".
        :type type: str
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    @overload
    def __init__(
        self,
        *,
        type: str = "boolean",
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        """Initialize a bool input.

        :param type: The type of the data input. Can only be set to "boolean".
        :type type: str
        :param optional: Determine if this input is optional
        :type optional: bool
        :param description: Description of the input
        :type description: str
        """

    def __init__(
        self,
        *,
        type: str = "uri_folder",
        path: str = None,
        mode: str = "ro_mount",
        min: Union[int, float] = None,
        max: Union[int, float] = None,
        enum=None,
        optional: bool = None,
        description: str = None,
        **kwargs,
    ):
        # As an annotation, it is not allowed to initialize the name.
        # The name will be updated by the annotated variable name.
        self._is_primitive_type = type in IO_CONSTANTS.PRIMITIVE_STR_2_TYPE
        self.path = path
        self.mode = None if self._is_primitive_type else mode
        self.min = min
        self.max = max
        self.enum = enum
        self.optional = optional
        self.default = kwargs.pop("default", None)
        super().__init__(name=None, type=type, description=description, **kwargs)
        # normalize properties like ["default", "min", "max", "optional"]
        self._normalize_self_properties()

    def _to_io_entity_args_dict(self):
        """Convert the Input object to a kwargs dict for azure.ai.ml.entity.Input."""
        keys = ["name", "path", "type", "mode", "description", "min", "max", "enum", "optional", "default"]
        result = {key: getattr(self, key, None) for key in keys}
        result = {**self._kwargs, **result}
        return _remove_empty_values(result)

    @classmethod
    def _get_input_by_type(cls, t: type, optional=None):
        if t in IO_CONSTANTS.PRIMITIVE_TYPE_2_STR:
            return cls(type=IO_CONSTANTS.PRIMITIVE_TYPE_2_STR[t], optional=optional)
        return None

    @classmethod
    def _get_default_string_input(cls, optional=None):
        return cls(type="string", optional=optional)

    def _normalize_self_properties(self):
        # parse value from string to it's original type. eg: "false" -> False
        if self.type in IO_CONSTANTS.PARAM_PARSERS:
            for key in ["default", "min", "max"]:
                if getattr(self, key) is not None:
                    origin_value = getattr(self, key)
                    new_value = IO_CONSTANTS.PARAM_PARSERS[self.type](origin_value)
                    setattr(self, key, new_value)
        self.optional = IO_CONSTANTS.PARAM_PARSERS["boolean"](getattr(self, "optional", "false"))
        self.optional = True if self.optional is True else None


class Output(_IOBase):
    """Define an output of a component.

    :param type: The type of the data output. Possible values include:
                        'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
    :type type: str
    :param path: The path to which the output is pointing. Needs to point to a cloud path.
    :type path: str
    :param mode: The mode of the data output. Possible values are:
                        'rw_mount': Read-write mount the data,
                        'upload': Upload the data from the compute target,
                        'direct': Pass in the URI as a string
    :type mode: str
    :param description: Description of the output
    :type description: str
    """

    @overload
    def __init__(self, type="uri_folder", path=None, mode="rw_mount", description=None):
        """Define an output of a component.

        :param path: The path to which the output is pointing. Needs to point to a cloud path.
        :type path: str
        :param type: The type of the data output. Possible values include:
                            'uri_folder', 'uri_file', 'mltable', 'mlflow_model', 'custom_model', and user-defined types.
        :type type: str
        :param mode: The mode of the data output. Possible values are:
                            'rw_mount': Read-write mount the data,
                            'upload': Upload the data from the compute target,
                            'direct': Pass in the URI as a string
        :type mode: str
        :param description: Description of the output
        :type description: str
        """

    def __init__(self, *, type="uri_folder", path=None, mode="rw_mount", description=None, **kwargs):
        # As an annotation, it is not allowed to initialize the name.
        # The name will be updated by the annotated variable name.
        self.path = path
        self.mode = mode
        super().__init__(name=None, type=type, description=description, **kwargs)
        self._is_primitive_type = self.type in IO_CONSTANTS.PRIMITIVE_STR_2_TYPE

    def _to_io_entity_args_dict(self):
        """Convert the Output object to a kwargs dict for azure.ai.ml.entity.Output."""
        keys = ["name", "path", "type", "mode", "description"]
        result = {key: getattr(self, key) for key in keys}
        result.update(self._kwargs)
        return _remove_empty_values(result)


def _remove_empty_values(data, ignore_keys=None):
    if not isinstance(data, dict):
        return data
    ignore_keys = ignore_keys or {}
    return {
        k: v if k in ignore_keys else _remove_empty_values(v)
        for k, v in data.items()
        if v is not None or k in ignore_keys
    }


def _get_annotation_cls_by_type(t: type, raise_error=False, optional=None):
    cls = Input._get_input_by_type(t=t, optional=optional)
    if cls is None and raise_error:
        raise UserErrorException(f"Can't convert type {t} to mldesigner.Input")
    return cls


def _get_annotation_by_value(val):

    if val is Parameter.empty or val is None:
        # If no default value or default is None, create val as the basic parameter type,
        # it could be replaced using component parameter definition.
        annotation = Input._get_default_string_input()
    else:
        # for types generated from default value, regard it as optional input
        annotation = _get_annotation_cls_by_type(type(val), raise_error=False)
        if not annotation:
            # Fall back to default
            annotation = Input._get_default_string_input()
    return annotation


def _standalone_get_param_with_standard_annotation(func):
    """Parse annotations for standalone mode func"""

    def _get_fields(annotations):
        """Return field names to annotations mapping in class."""
        annotation_fields = OrderedDict()
        for name, annotation in annotations.items():
            # Skip return type
            if name == "return":
                continue
            # Try create annotation by type when got like 'param: int'
            if not _is_mldesigner_type_cls(annotation) and not _is_mldesigner_types(annotation):
                annotation = _get_annotation_cls_by_type(annotation, raise_error=False)
                if not annotation:
                    # Fall back to string parameter
                    annotation = Input._get_default_string_input()
            annotation_fields[name] = annotation
        return annotation_fields

    def _merge_field_keys(annotation_fields, defaults_dict):
        """Merge field keys from annotations and cls dict to get all fields in class."""
        anno_keys = list(annotation_fields.keys())
        dict_keys = defaults_dict.keys()
        if not dict_keys:
            return anno_keys
        return [*anno_keys, *[key for key in dict_keys if key not in anno_keys]]

    def _update_annotation_with_default(anno, name, default):
        """Create annotation if is type class and update the default."""
        # Create instance if is type class
        complete_annotation = anno
        if _is_mldesigner_type_cls(anno):
            complete_annotation = anno()
        complete_annotation.name = name
        if default is Input._EMPTY:
            return complete_annotation
        if isinstance(complete_annotation, Input) and complete_annotation._is_primitive_type:
            # For mldesigner Input, user cannot set default inside Input class, instead it's set by "=" as parameter default
            # As mldesigner Input is merely an interface, there is no validation for default value yet
            complete_annotation.default = default
        return complete_annotation

    def _merge_and_update_annotations(annotation_fields, defaults_dict):
        """Use public values in class dict to update annotations."""
        all_fields = OrderedDict()
        all_filed_keys = _merge_field_keys(annotation_fields, defaults_dict)
        for name in all_filed_keys:
            # Get or create annotation
            annotation = (
                annotation_fields[name]
                if name in annotation_fields
                else _get_annotation_by_value(defaults_dict.get(name, Input._EMPTY))
            )
            # Create annotation if is class type and update default
            annotation = _update_annotation_with_default(annotation, name, defaults_dict.get(name, Input._EMPTY))
            all_fields[name] = annotation
        return all_fields

    annotations = getattr(func, "__annotations__", {})
    annotation_fields = _get_fields(annotations)
    defaults_dict = {key: val.default for key, val in signature(func).parameters.items()}
    all_fields = _merge_and_update_annotations(annotation_fields, defaults_dict)
    return all_fields


def _is_mldesigner_type_cls(t: type):
    if type(t) is not type:
        return False
    return issubclass(t, (Input, Output))


def _is_mldesigner_types(o: object):
    return _is_mldesigner_type_cls(type(o))
