import os
import tempfile

import click
from PyPDF2 import PdfMerger

from inkplot.layered_svg import LayeredSVG
from inkplot.pages import read_yaml, pagedef_expanded_pattern_visible_iterator, page_zoom_rectangle_id
from inkplot.svg_locator import SVGLocator


@click.command()
@click.argument("pages_def")
@click.argument("output")
def inkplot(pages_def, output):
    build_pdf(pages_def, output)


def build_pdf(pages_def, output):
    SVGLocator.set_call_dirpath()
    pages_def_abs_filepath = os.path.realpath(pages_def)
    pages_def_data = read_yaml(pages_def_abs_filepath)

    # register shared layersets to local map
    shared_layerset_defs = pages_def_data['shared']['layersets']
    name_to_layerset_def = {}
    for layerset_def in shared_layerset_defs:
        name_to_layerset_def[layerset_def['name']] = layerset_def

    # iterate over pages
    with tempfile.TemporaryDirectory() as tmpdirname:
        os.chdir(tmpdirname)
        page_pdfs = []
        for page_def in pages_def_data['pages']:

            # read the source svg
            svg = LayeredSVG(filepath=SVGLocator(page_def.get('source'),
                                                 pages_def_abs_filepath).filepath())

            # update layer visibility
            pattern_visibility_tuples = pagedef_expanded_pattern_visible_iterator(
                page_def=page_def,
                shared_layersets_dict=name_to_layerset_def)
            for pattern, is_visible in pattern_visibility_tuples:
                svg.set_layer_visibility(pattern=pattern, visible=is_visible)

            # update the viewbox
            svg.set_viewbox_to_rect(page_zoom_rectangle_id(page_def, pages_def_data['shared']['zoom-rectangles']))

            page_pdf_filename = '{}.pdf'.format(page_def['name'])
            svg.write_pdf(page_pdf_filename)
            page_pdfs.append(page_pdf_filename)

        # combine the page pdfs into a final pdf
        merger = PdfMerger()
        for pdf in page_pdfs:
            merger.append(pdf)
        merger.write(output)
        merger.close()
