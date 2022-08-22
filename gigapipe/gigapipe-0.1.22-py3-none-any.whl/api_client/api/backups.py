import requests
from http import HTTPStatus
from typing import Dict, Any
from requests import Response
from gigapipe.exceptions import GigapipeServerError
from gigapipe.api_client.api import Base
from gigapipe.api_client.gigapipe_api import GigapipeApi


class Backups(Base):
    """
    Backups Class
    """

    def __init__(self, api):
        """
        Backups Constructor
        :param api: The API instance
        """
        super(Backups, self).__init__(api)

    @GigapipeApi.autorefresh_access_token
    def get_organization_backups(self) -> Response:
        """
        Obtains the list of backups for the user's organization
        :return: A list containing the backups
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/backups"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_cluster_backups(self, cluster_slug: str) -> Response:
        """
        Obtains the list of backups for a given cluster
        :param cluster_slug: the cluster slug
        :return: A list containing the backups
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/backups/cluster/{cluster_slug}"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def restore_backup(self, cluster_slug: str, *, backup_payload: Dict[str, Any]) -> Response:
        """
        Restores from a backup
        :param cluster_slug: the cluster which the backup will be restored for
        :param backup_payload: the dictionary containing the necessary info to restore a backup
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/backups/restore/cluster/{cluster_slug}"

        try:
            response: Response = requests.post(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=backup_payload)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def delete_backup(self, cluster_slug: str, *, backup_payload: Dict[str, Any]) -> Response:
        """
        Deletes a backup
        :param cluster_slug: the cluster which the backup will be deleted for
        :param backup_payload: the dictionary containing the necessary info to delete a backup
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/backups/delete/cluster/{cluster_slug}"

        try:
            response: Response = requests.delete(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=backup_payload)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_organization_backups_cronjobs(self) -> Response:
        """
        Obtains the list of backups' cronjobs for the user organization
        :return: A list containing the cronjobs
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/backups/cronjobs"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_cluster_backups_cronjobs(self, cluster_slug: str) -> Response:
        """
        Obtains the list of backups cronjobs for a given cluster
        :param cluster_slug: the cluster slug
        :return: A list containing the cronjobs
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/backups/cronjobs/cluster/{cluster_slug}"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def get_backup_cronjob_from_id(self, cronjob_id: int) -> Response:
        """
        Obtains a cronjob from a given ID
        :param cronjob_id: the id of the cronjob
        :return: A dictionary containing the backup info
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/backups/cronjobs/{cronjob_id}"

        try:
            response: Response = requests.get(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def create_backup_cronjob(self, cluster_slug: str, *, cronjob_payload: Dict[str, Any]) -> Response:
        """
        Creates a new backup cronjob
        :param cluster_slug: the cluster which the cronjob will be created for
        :param cronjob_payload: the dictionary containing the necessary info to create a cronjob
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/backups/cronjobs/{cluster_slug}"

        try:
            response: Response = requests.post(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=cronjob_payload)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def update_backup_cronjob(self, cluster_slug: str, *, cronjob_payload: Dict[str, Any]) -> Response:
        """
        Update a backup cronjob
        :param cluster_slug: the cluster which the cronjob will be updated for
        :param cronjob_payload: the dictionary containing the necessary info to update a cronjob
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/backups/cronjobs/{cluster_slug}"

        try:
            response: Response = requests.patch(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            }, json=cronjob_payload)
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response

    @GigapipeApi.autorefresh_access_token
    def delete_backup_cronjob(self, cluster_slug: str, *, cronjob_id: str) -> Response:
        """
        Deletes a backup cronjob
        :param cluster_slug: the cluster which the cronjob will be deleted for
        :param cronjob_id: the cronjob id that will be deleted
        :return: A message response
        """
        url: str = f"{self.api.url}/{self.api.__class__.version}/backups/cronjobs/{cluster_slug}/{cronjob_id}"

        try:
            response: Response = requests.delete(url, headers={
                "Authorization": f"Bearer {self.api.access_token}"
            })
        except requests.RequestException as e:
            raise GigapipeServerError(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                message=f"Internal Server Error: {e}"
            )
        return response
