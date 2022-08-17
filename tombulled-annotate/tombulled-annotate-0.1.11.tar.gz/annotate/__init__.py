from .api import annotate
from .attributes import annotations
from .models import Annotation
from .decorators import annotation, marker


get_raw_annotations = annotations.get
has_annotations = annotations.has
set_annotations = annotations.set
del_annotations = annotations.delete
setdefault_annotations = annotations.setdefault


def get_annotations(obj):
    return {
        annotation.key: annotation.value
        for annotation in get_raw_annotations(obj).values()
    }
