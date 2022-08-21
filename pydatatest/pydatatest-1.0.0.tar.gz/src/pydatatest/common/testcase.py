#! /usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from common.inject import _inject_multi_to


class TestError(Exception):
    pass


class PyDataTestCase(unittest.TestCase):
    '''test base case
    '''
    def __init__(self, methodName):
        super().__init__(methodName)
        self._pydatatest_runner = None
        self._pydatatest_multi = False
        self._pydatatest_dataset = []

    @classmethod
    def before_all(cls):
        '''
        before all tests
        '''
        pass

    @classmethod
    def after_all(cls):
        '''
        after all tests
        '''
        pass
    
    def before_each(self):
        '''
        run before each test method
        '''
        pass

    def after_each(self):
        '''
        run after each test method
        '''
        pass
    
    def before_each_data(_self):
        '''
        run before each test data
        '''
        pass

    def after_each_data(self):
        '''
        run after each test data
        '''
        pass

    def run(self, result=None):
        '''
        run a testcase method
        '''
        e = None
        if result is not None:
            if hasattr(result, 'dots'):
                result.dots = False

        self.before_each_data()
        # try:
        super().run(result)
        # except Exception as e:
        #     self.after_each_data()
        #     pass
        self.after_each_data()

        if (self._pydatatest_multi):
            for i in range(len(self._pydatatest_dataset)):
                print("dataset in self", self._pydatatest_dataset)
                # _inject_multi_to(self._pydatatest_dataset, self)
                self.before_each_data()
                # try:
                super().run(result)
                print(result)
                # except Exception as e:
                #     self.after_each_data()
                #     break
                self.after_each_data()
            # multi = self._pydatatest_multi
            # dataset = self._pydatatest_dataset
            # while multi:
            #     print("===before inject::", dataset, multi)
            #     self.before_each_data()
            #     super().run(result)
            #     dataset = self._pydatatest_dataset
            #     multi = self._pydatatest_multi
            #     print("===after inject::", self._pydatatest_dataset, self._pydatatest_multi)
            #     self.after_each_data()
        if e is not None:
            raise TestError(e)
    
    def setUp(self):
        self.before_each()

    def tearDown(self):
        self.after_each()

    @classmethod
    def setUpClass(cls):
        cls.before_all()

    @classmethod
    def tearDownClass(cls):
        cls.after_all()
