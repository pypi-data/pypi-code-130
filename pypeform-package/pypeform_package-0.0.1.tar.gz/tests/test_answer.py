import typing

from pypeform import Answer

_full_type = 'test_full_type'
_reference = 'test_reference'
_simple_type = 'test_simple_type'


def check_answer_values(answer_obj: Answer, answer: typing.Union[typing.List[str], int, float, str],
                        full_type: str, reference: str, simple_type: str) -> bool:
    assert answer_obj.answer == answer
    assert answer_obj.full_type == full_type
    assert answer_obj.reference == reference
    assert answer_obj.simple_type == simple_type

    return True


def test_answer_stores_variables():
    answer = 'test_answer'
    answer_obj = Answer(answer=answer, full_type=_full_type, reference=_reference, simple_type=_simple_type)
    check_answer_values(answer_obj=answer_obj, answer=answer, full_type=_full_type,
                        reference=_reference, simple_type=_simple_type)


def test_answer_stores_int_value():
    answer = 1
    answer_obj = Answer(answer=answer, full_type=_full_type, reference=_reference, simple_type=_simple_type)
    check_answer_values(answer_obj=answer_obj, answer=answer, full_type=_full_type,
                        reference=_reference, simple_type=_simple_type)


def test_answer_stores_float_value():
    answer = 3.14
    answer_obj = Answer(answer=answer, full_type=_full_type, reference=_reference, simple_type=_simple_type)
    check_answer_values(answer_obj=answer_obj, answer=answer, full_type=_full_type,
                        reference=_reference, simple_type=_simple_type)


def test_answer_stores_str_value():
    answer = 'string_value'
    answer_obj = Answer(answer=answer, full_type=_full_type, reference=_reference, simple_type=_simple_type)
    check_answer_values(answer_obj=answer_obj, answer=answer, full_type=_full_type,
                        reference=_reference, simple_type=_simple_type)


def test_answer_stores_list_of_str_value():
    answer = ['string_1', 'string_2', 'skip_a_few', 'string_a_million']
    answer_obj = Answer(answer=answer, full_type=_full_type, reference=_reference, simple_type=_simple_type)
    check_answer_values(answer_obj=answer_obj, answer=answer, full_type=_full_type,
                        reference=_reference, simple_type=_simple_type)
