from tygle_docs.types.resources.structural_element import StructuralElementList


def find_paragraph_element(elements: StructuralElementList, text: str):
    for element in elements:
        if element.paragraph:
            for paragraph_element in element.paragraph.elements:
                if paragraph_element.text_run:
                    if paragraph_element.text_run.content == text:
                        return paragraph_element
