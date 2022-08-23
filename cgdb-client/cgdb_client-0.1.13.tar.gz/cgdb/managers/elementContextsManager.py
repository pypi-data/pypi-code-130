from cgdb.recources.elementContext import ElementContext
from cgdb.utils.ManagerMix import ManagerMix


class ElementContextsManager(ManagerMix):
    def __init__(self, client):
        super().__init__(client)

        self.elementContextsCached = None

    def element_contexts(self):
        content = self.get("element-contexts")
        element_contexts = []

        for element_context_raw in content:
            element_contexts.append(ElementContext(**element_context_raw, client=self._client))

        return element_contexts

    def element_context(self, id):
        content = self.get("element-contexts/id:" + str(id))

        return ElementContext(**content, client=self._client)

    def element_context_by_element(self, element_mark: str, aggregation: str, timestamp_code: str):
        if self.elementContextsCached is None:
            self.elementContextsCached = self.element_contexts()

        for elementContext in self.elementContextsCached:
            if elementContext.aggregation == aggregation and elementContext.element.mark == element_mark and elementContext.time_step.code == timestamp_code:
                return elementContext

        return None