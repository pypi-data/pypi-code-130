from typing import Optional

from annotell.openlabel.models.models import OpenLabelAnnotation

from annotell.input_api.model.calibration.common import BaseSerializer


class ValidatedPreAnnotation(BaseSerializer):
    resource_id: str
    signed_url: Optional[str]
    preannotation: OpenLabelAnnotation


class ValidatePreAnnotationRequest(BaseSerializer):
    preannotation: OpenLabelAnnotation
    internal_id: str
