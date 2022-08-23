from cgdb.recources.element import Element
from cgdb.utils.ManagerMix import ManagerMix


class ElementsManager(ManagerMix):
    def __init__(self, client):
        super().__init__(client)

    def elements(self, url="elements"):
        content = self.get(url)
        elements = []

        for element_raw in content:
            elements.append(Element(**element_raw, client=self._client))

        return elements

    def element(self, mark):
        content = self.get("elements/" + mark)

        return Element(**content, client=self._client)

