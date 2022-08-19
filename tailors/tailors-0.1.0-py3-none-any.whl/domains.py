# -*- coding: utf-8 -*-
import hao

LOGGER = hao.logs.get_logger(__name__)


class Derivable:

    @classmethod
    def subclasses(cls):
        all_subclasses = []

        for subclass in cls.__subclasses__():
            all_subclasses.append(subclass)
            all_subclasses.extend(subclass.subclasses())

        return all_subclasses
