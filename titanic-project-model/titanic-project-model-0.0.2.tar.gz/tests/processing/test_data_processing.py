import pytest

from titanic_project.processing import data_processing


# def test_sum_items_case_positive_numbers():
#     test_object = data_processing.sum_items(5, 6)
#     expected_object = 11
#
#     assert test_object == expected_object
#
#
# def test_sum_items_case_negative_numbers():
#     test_object = data_processing.sum_items(-5, -6)
#     expected_object = -11
#
#     assert test_object == expected_object
#
#
# def test_sum_items_case_different_numbers():
#     test_object = data_processing.sum_items(5, -6)
#     expected_object = -1
#
#     assert test_object == expected_object


def test_validate_predict_data_normal_case():

    data = {
        'Age': [5],
        'Sex': ['male'],
        'Embarked': ['C']
    }

    data_processing.validate_predict_data(data)


def test_validate_predict_data_wrong_embarked_case():

    data = {
        'Age': [5],
        'Sex': ['male'],
        'Embarked': ['A']
    }

    with pytest.raises(ValueError):
        data_processing.validate_predict_data(data)


def test_validate_predict_data_wrong_type_age_str():

    data = {
        'Age': ['5'],
        'Sex': ['male'],
        'Embarked': ['A']
    }

    with pytest.raises(TypeError):
        data_processing.validate_predict_data(data)


def test_validate_predict_data_wrong_type_sex_list():

    data = {
        'Age': [5],
        'Sex': [['cat']],
        'Embarked': ['A']
    }

    with pytest.raises(TypeError):
        data_processing.validate_predict_data(data)


def test_validate_predict_data_wrong_type_embarked_list():

    data = {
        'Age': ['5'],
        'Sex': ['male'],
        'Embarked': [['A']]
    }

    with pytest.raises(TypeError):
        data_processing.validate_predict_data(data)
