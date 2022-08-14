from __future__ import annotations

from ..ns import *
from .Procedure import Procedure


class PublicProcurement(Procedure):
    __type__ = PUBC["PublicProcurement"]
