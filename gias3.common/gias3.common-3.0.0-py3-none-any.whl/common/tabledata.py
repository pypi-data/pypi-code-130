"""
FILE: tabledata.py
LAST MODIFIED: 24-12-2015 
DESCRIPTION: representing a table of data.

===============================================================================
This file is part of GIAS2. (https://bitbucket.org/jangle/gias2)

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
===============================================================================
"""
import numpy as np


class Classification(object):

    def __init__(self, name, labels_dict, code):
        self.name = name
        self.labels = labels_dict
        self.code = code


class TableData(object):

    def __init__(self, name):
        self.name = name
        self._classifications = {}
        self._headers = None
        self._rowLabels = None
        self._units = None
        self._dataArray = None

    def addClassification(self, classification):
        self._classifications[classification.name] = classification

    def setData(self, headers, rows, units, data_array):
        self._headers = list(headers)
        self._rowLabels = list(rows)
        self._units = list(units)
        self._dataArray = np.array(data_array)

    def addDataColumn(self, header, unit, data):
        self._headers.append(header)
        self._units.append(unit)
        self._dataArray = np.hstack([self._dataArray, data[:, np.newaxis]])

    def addDataRow(self, row_label, data):
        self._rowLabels = self._rowLabels.append(row_label)
        self._dataArray = np.vstack([self._dataArray, data])

    def getClasses(self):
        return list(self._classifications.keys())

    def getLabelsForClass(self, classification_name):
        return self._classifications[classification_name].labels

    def getHeaders(self):
        return self._headers

    def getUnits(self):
        return self._units

    def getUnitsForHeader(self, header):
        return self._units[self._headers.index(header)]

    def getData(self, header, classification_name=None, class_label=None):
        data = self._dataArray[:, self._headers.index(header)]
        if classification_name is not None:
            C = self._classifications[classification_name]
            data = data[C.code == C.labels[class_label]]

        return data

    def getRowLabels(self, classification_name=None, class_label=None):
        if classification_name is None:
            return self._rowLabels
        else:
            C = self._classifications[classification_name]
            return [self._rowLabels[i] for i in np.where(C.code == C.labels[class_label])[0]]
