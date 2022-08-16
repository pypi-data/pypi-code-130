"""
FILE: test_inptest.py
LAST MODIFIED: 24-12-2015 
DESCRIPTION: Test INP reading and writing

===============================================================================
This file is part of GIAS2. (https://bitbucket.org/jangle/gias2)

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, You can obtain one at http://mozilla.org/MPL/2.0/.
===============================================================================
"""
import importlib
import os.path
import unittest

from gias3.mesh import inp
import gias3.testing as testing

inputFilename = 'data/prox_femur.inp'
outputFilename = 'data/prox_femur_out.inp'


class TestDistanceToLine(unittest.TestCase):

    def test_read_mesh(self):
        try:
            with importlib.resources.path(testing, inputFilename) as p:
                package_path = p
        except AttributeError:
            package_path = os.path.realpath(os.path.dirname(__file__))

        reader = inp.InpReader(os.path.join(package_path, inputFilename))
        header = reader.readHeader()
        self.assertEqual('affine hemi-pelvis', header[0])
        meshnames = reader.readMeshNames()
        self.assertEqual('Femur_template', meshnames[0])
        mesh = reader.readMesh(meshnames[0])

        writer = inp.InpWriter(os.path.join(package_path, outputFilename))
        writer.addHeader(header[0])
        writer.addMesh(mesh)
        writer.write()

        self.assertEqual(9212, mesh.getNumberOfElems())
        self.assertEqual(4642, mesh.getNumberOfNodes())
        location = mesh.getNode(10)
        self.assertAlmostEqual(-61.07562143, location[0])
        self.assertAlmostEqual(-27.0663306, location[1])
        self.assertAlmostEqual(-15.74273052, location[2])
        self.assertEqual([6, 21, 20], mesh.getElem(10))
        self.assertEqual('R3D3', mesh.getElemType())


if __name__ == '__main__':
    unittest.main()
