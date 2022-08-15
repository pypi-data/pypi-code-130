"""
Gender Enum Class
"""

from enum import Enum


class Gender (Enum):
    MALE = 1
    FEMALE = 2
    OTHER = 3
    UNKNOWN = 4

    @staticmethod
    def to_string(gender) -> str:
        """
        Helper function that parses string into a gender enum
        :param gender: string that will be converted to Gender Enum
        """
        if gender is None:
            return gender
        if gender == Gender.MALE:
            return "MALE"
        if gender == Gender.FEMALE:
            return "FEMALE"
        if gender == Gender.OTHER:
            return "OTHER"
        if gender == Gender.UNKNOWN:
            return "UNKNOWN"
        return None

    @staticmethod
    def string_to_gender(string_gender: str):
        """
        Helper function that parses string into a gender enum
        :param string_gender: string that will be converted to Gender Enum
        """
        if string_gender is None:
            return None
        if string_gender.upper() == "MALE":
            return Gender.MALE
        if string_gender.upper() == "FEMALE":
            return Gender.FEMALE
        if string_gender.upper() == "OTHER":
            return Gender.OTHER
        if string_gender.upper() == "UNKNOWN":
            return Gender.UNKNOWN
        return None
