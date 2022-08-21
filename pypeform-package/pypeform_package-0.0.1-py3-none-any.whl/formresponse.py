import datetime
import logging
import typing

import iso8601

from .answer import Answer
from .field import Field
from .variable import Variable


class FormResponse:
    form_id: str
    token: str
    landed_at: datetime.datetime
    submitted_at: datetime.datetime

    # hidden_variables: dict
    variables: typing.Optional[typing.Dict[str, Variable]] = None
    fields: typing.Dict[str, Field] = None
    answers: typing.Dict[str, Answer]
    _answer_reference_to_id = typing.Dict[str, str]

    def __init__(self, form_id: str, token: str,
                 landed_at: datetime.datetime,
                 submitted_at: datetime.datetime,
                 variables: typing.List[dict],
                 answers: typing.List[dict],
                 fields: typing.List[dict]):
        self.form_id = form_id
        self.token = token
        self.landed_at = landed_at
        self.submitted_at = submitted_at

        # clean up the variables
        self.variables = FormResponse._clean_variable_list(variables) if variables else None

        # clean up the answers
        self.answers, self._answer_reference_to_id = FormResponse._clean_answer_list(answer_list=answers)

        # clean up the field definitions
        self.fields = FormResponse._clean_field_list(field_list=fields)

    @staticmethod
    def _clean_field_list(field_list: typing.List[dict]) -> typing.Dict[str, Field]:
        field_dict: typing.Dict[str, Field] = dict()
        for field in field_list:
            f = Field.from_definition_json(field)
            field_dict[f.id] = f

        return field_dict

    ### Answers
    # Answers are accessible via ID or reference
    @staticmethod
    def _clean_answer_list(answer_list: typing.List[typing.Dict[str, typing.Any]]) -> (typing.Dict[str, Answer],
                                                                                       typing.Dict[str, str]):
        """
        Cleaned answers take the format of
        {
            'field_id_from_typeform': {
                'simple_type': 'choices',
                'full_type': 'multiple_choice',
                'answer': 123, # or 'my_string' or '['string_1', 'string_3']
                'reference': 'block_reference', # if exists, otherwise equals field_id_from_typeform
            },
            ...
        }
        """

        answer_dict = dict()
        reference_to_id = dict()
        for answer in answer_list:
            field: typing.Dict[str, typing.Any] = answer['field']
            field_id = field['id']
            field_type = field['type']
            field_ref = field.get('ref', None)
            if field_ref is None:
                field_ref = field_id

            simple_type = answer['type']

            if simple_type == 'choice':
                if 'label' in answer['choice']:
                    extracted_answer = answer['choice']['label']
                elif 'other' in answer['choice']:
                    extracted_answer = answer['choice']['other']
                else:
                    logging.warning(f'No label or other found for answer {answer}, skipping..')
                    continue
            elif simple_type == 'choices':
                extracted_answer = list()
                if 'labels' in answer['choices']:
                    extracted_answer += answer['choices']['labels']
                if 'other' in answer['choices']:
                    extracted_answer += list(answer['choices']['other'])
            elif simple_type == 'number':
                extracted_answer = answer['number']
            elif simple_type == 'date':
                date_string: str = answer['date']
                extracted_answer = datetime.datetime.strptime(date_string, '%Y-%m-%d')
            else:
                extracted_answer = answer[simple_type]

            # TODO: add Field data like title, properties, etc.
            answer_dict[field_id] = Answer(answer=extracted_answer, full_type=field_type,
                                           reference=field_ref, simple_type=simple_type)
            reference_to_id[field_ref] = field_id

        return answer_dict, reference_to_id

    def get_answer_from_field_id(self, _id) -> Answer:
        return self.answers[_id]

    def get_field_id_from_field_reference(self, reference):
        return self._answer_reference_to_id[reference]

    @property
    def field_references(self) -> typing.List[str]:
        """
        Returns a list of all answer references
        :return: list of answer references
        """
        return list(self._answer_reference_to_id.keys())

    @property
    def field_ids(self) -> typing.List[str]:
        """
        Returns a list of all fields IDs
        :return: list of fields IDs
        """
        return list(self.answers.keys())

    def get_answer_from_field_reference(self, reference, include_field=True) -> Answer:
        """
        Returns the answer from the reference
        :param reference: the reference for this answer
        :return: the Answer object, if found
        """
        _id = self.get_field_id_from_field_reference(reference=reference)
        answer = self.get_answer_from_field_id(_id=_id)
        # TODO: add Field object into the Answer object

        return answer

    @property
    def variable_keys(self) -> typing.List[str]:
        """
        Returns a list of all variable keys
        :return: all variable keys
        """
        return list(self.variables.keys())

    def get_variable_from_key(self, key: str) -> Variable:
        """
        Returns a Variable object from the key
        :param key: the key for this Variable object
        :return: the Variable object
        """
        variable = self.variables[key]
        if variable.key != key:
            raise IndexError(f'Variable key in object ({variable.key} doesnt match dictionary key ({key})). '
                             f'Malformed dictionary?')
        return self.variables[key]

    def get_variable_value(self, key: str) -> typing.Union[str, float, int]:
        """
        Returns the value of the variable from the key
        :param key: the key for the Variable object
        :return: the value stored in this variable
        """
        return self.get_variable_from_key(key).value

    @staticmethod
    def _clean_variable_list(variable_list: typing.Iterable[dict]) -> typing.Dict[str, Variable]:
        clean_dict = dict()
        for variable in variable_list:
            v = FormResponse._clean_variable_single(variable)
            clean_dict[v.key] = v
        return clean_dict

    @staticmethod
    def _clean_variable_single(variable: dict) -> Variable:
        key = variable['key']
        type = variable['type']
        value = variable[type]

        return Variable(key=key, _type=type, value=value)

    def __str__(self):
        return f'FormResponse(form_id={self.form_id}, token={self.token}, ' \
               f'landed_at={self.landed_at}, submitted_at={self.submitted_at},' \
               f'\nvariables={self.variables},\nanswers={self.answers})'

    @classmethod
    def from_form_response_json(cls, form_response_json):
        form_id = form_response_json['form_id']
        token = form_response_json['token']

        landed_at = iso8601.parse_date(form_response_json['landed_at'])
        submitted_at = iso8601.parse_date(form_response_json['submitted_at'])

        variables = form_response_json.get('variables', None)
        answers = form_response_json.get('answers', None)
        fields = form_response_json.get('definition', None).get('fields', None)

        return cls(form_id=form_id, token=token,
                   landed_at=landed_at, submitted_at=submitted_at,
                   variables=variables,
                   answers=answers,
                   fields=fields)
