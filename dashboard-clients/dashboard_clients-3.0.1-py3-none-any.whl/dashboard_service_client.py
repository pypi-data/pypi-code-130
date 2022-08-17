from typing import Any, Union
from clients_core.service_clients import E360ServiceClient
from .models import TabbedDashboardModel


class DashboardsClient(E360ServiceClient):
    """
    Subclasses dataclass `clients_core.service_clients.E360ServiceClient`.

    Args:
        client (clients_core.rest_client.RestClient): an instance of a rest client
        user_id (str): the user_id guid

    """

    service_endpoint = ""
    extra_headers = {
        "accept": "application/json",
        "Content-Type": "application/json-patch+json",
    }

    def create(
        self, payload: TabbedDashboardModel, **kwargs: Any
    ) -> TabbedDashboardModel:
        """
        Creates a dashboard, returns a deserialised model instance.

        Args:
            payload: a pydantic model for tabbed dashboard

        """
        data: dict = payload.dump()
        response = self.client.post(
            "", json=data, headers=self.service_headers, raises=True, **kwargs
        )
        return TabbedDashboardModel.parse_obj(response.json())

    def get_dashboard_by_id(
        self, dashboard_id: Union[int, str], **kwargs: Any
    ) -> TabbedDashboardModel:
        """
        Gets a dashboard by id
        """
        response = self.client.get(
            str(dashboard_id), headers=self.service_headers, raises=True, **kwargs
        )
        return TabbedDashboardModel.parse_obj(response.json())

    def update_dashboard(
        self, payload: TabbedDashboardModel, **kwargs: Any
    ) -> TabbedDashboardModel:
        """
        Updates a dashboard with given payload which includes the dashboard id

        Args:
            payload: a pydantic model for tabbed dashboard

        """
        data: dict = payload.dump()
        response = self.client.put(
            str(payload.id),
            json=data,
            headers=self.service_headers,
            raises=True,
            **kwargs,
        )
        return TabbedDashboardModel.parse_obj(response.json())

    def delete_by_id(self, dashboard_id: Union[int, str], **kwargs: Any) -> bool:
        """Deletes a dashboard by id"""
        response = self.client.delete(str(dashboard_id), raises=True, **kwargs)
        return response.ok
