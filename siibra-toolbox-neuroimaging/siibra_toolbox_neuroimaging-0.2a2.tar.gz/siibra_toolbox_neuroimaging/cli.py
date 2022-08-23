#!/usr/bin/env python3

# Copyright 2018-2022
# Institute of Neuroscience and Medicine (INM-1), Forschungszentrum Jülich GmbH

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# disable logging during setup
import click

@click.command()
@click.argument("niftifiles", type=click.STRING, nargs=-1)
@click.option( "-s", "--space", type=click.STRING, default='mni152')
@click.option( "-p", "--parcellation", type=click.STRING, default="julich 2.9")
@click.option( "-o", "--outdir", type=click.STRING, default=None)
def nifti(niftifiles, space, parcellation, outdir):
    """Assign whole brain signals in NIfTI images to brain regions from a parcellation"""
    from siibra_toolbox_neuroimaging import AnatomicalAssignment
    analysis = AnatomicalAssignment(parcellation, space)
    for niftifile in niftifiles:
        assignments, component_mask = analysis.analyze(niftifile)
        analysis.create_report(assignments, niftifile, component_mask, outdir)
