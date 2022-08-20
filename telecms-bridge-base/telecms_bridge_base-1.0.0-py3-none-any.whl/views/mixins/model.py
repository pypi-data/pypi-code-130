from telecms_bridge_base.views.base.generic_api import GenericAPIView
from telecms_bridge_base.views.mixins.create import CreateAPIViewMixin
from telecms_bridge_base.views.mixins.destroy import DestroyAPIViewMixin
from telecms_bridge_base.views.mixins.list import ListAPIViewMixin
from telecms_bridge_base.views.mixins.retrieve import RetrieveAPIViewMixin
from telecms_bridge_base.views.mixins.update import UpdateAPIViewMixin


class ModelAPIViewMixin(ListAPIViewMixin,
                        RetrieveAPIViewMixin,
                        DestroyAPIViewMixin,
                        CreateAPIViewMixin,
                        UpdateAPIViewMixin,
                        GenericAPIView):
    pass
