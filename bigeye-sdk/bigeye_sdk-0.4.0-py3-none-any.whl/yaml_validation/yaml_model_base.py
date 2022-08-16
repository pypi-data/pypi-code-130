from __future__ import annotations

from typing import List

import yaml
from pydantic import root_validator
from pydantic_yaml import YamlModel

from bigeye_sdk.functions.search_and_match_functions import fuzzy_match
from bigeye_sdk.yaml_validation.YamlValidationErrorMessages import INVALID_DECLARED_ATTRIBUTE_ERRMSG, \
    NO_POSSIBLE_MATCH_ERRMSG, POSSIBLE_MATCH_ERRMSG
from bigeye_sdk.yaml_validation.validation_context import put_validation_error_to_ix

from bigeye_sdk.yaml_validation.validation_models import ValidationError


class YamlModelWithValidatorContext(YamlModel):
    @classmethod
    def raise_validation_error(cls, error_lines: List[str], error_context_lines: List[str] = None,
                               error_message: str = None):
        """
        Appends a validation error to the _Validator_Context by instantiating a ValidationError.
        Args:
            error_lines: lines of the exact error
            error_context_lines: lines of the broader section of yaml containing error
            error_message: error message to log as a warning.

        Returns: None

        """
        ve = ValidationError(error_lines=error_lines,
                             erroneous_configuration_cls_name=cls.__name__,
                             error_message=error_message,
                             error_context_lines=error_context_lines)

        put_validation_error_to_ix(ve)

    def get_error_lines(self) -> List[str]:
        """
        Returns object serialized to yaml and split to lines.  Used to search files.
        Returns: List of yaml string lines.

        """
        return self.yaml(exclude_unset=True, exclude_defaults=True,
                         exclude_none=True, indent=True).splitlines()

    @root_validator(pre=True)
    def verify_all_attributes_valid(cls, values):
        expected_attribs = cls.__annotations__
        unexpected_attribs = {}
        return_values = {}

        # for c in cls.mro():
        #     try:
        #         expected_attribs.update(**c.__annotations__)
        #     except AttributeError:
        #         # object, at least, has no __annotations__ attribute.
        #         pass

        for attrib_name, attrib_value in values.items():
            if attrib_name in expected_attribs.keys() or attrib_name == 'type':
                return_values[attrib_name] = attrib_value
            else:
                unexpected_attribs[attrib_name] = attrib_value
                possible_matches = fuzzy_match(search_string=attrib_name, contents=list(expected_attribs.keys()))
                if possible_matches:
                    pms = [i[1] for i in possible_matches]
                    possible_match_message = POSSIBLE_MATCH_ERRMSG.format(possible_matchs=", ".join(pms))
                else:
                    possible_match_message = NO_POSSIBLE_MATCH_ERRMSG

                error_message = INVALID_DECLARED_ATTRIBUTE_ERRMSG.format(cls_name=cls.__name__, err_attrib=attrib_name,
                                                                         possible_message=possible_match_message)
                cls.raise_validation_error(error_lines=[yaml.safe_dump({attrib_name: attrib_value})],
                                           error_message=error_message)

                for err_attrib, match in possible_matches:
                    return_values[match] = attrib_value

        return return_values
