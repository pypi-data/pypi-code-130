import logging

from python_sdk_client.clients_enum import EnvType
from python_sdk_client.libs.cropin_client import CropinClient


class CropinAPI:
    """Class to connect CropinAPI to do different operations.
    As part of initialization, it's first step is Authentication.

    Parameters
    ----------
    tenant : string
        tenant for Cropin
    username : string
        username for Cropin
    password : string
        password for Cropin

    """

    logger = logging.getLogger("insights-sdk.CropinAPI")

    def __init__(self, tenant: str, username: str, password: str, env: EnvType = EnvType.PROD):
        self.cropin_client = CropinClient(tenant, username, password, env)
        print("CropinAPI is ready !!!!")

    def get_plot_details(self, plot_ids: str = None, **kwargs) -> list:
        """
        Fetch plot's details by providing multiple plot_ids as list.
        If list of ids is not provided, it will return few latest plot's details.

        Parameters
        ----------
        :param str plot_ids: Filter by ids, it can be single id or list
        :param str external_ids: Filter by externalIds
        :param str parent_ids: Filter by parentIds
        :param str min_created_date_time: Filter by specific date range
        :param str max_created_date_time: Filter by specific date range
        :param str sort_by: Sort by given parameter name
        :param str direction: Order by ascending or descending fashion

        :return: List[Plots]

        """
        return self.cropin_client.get_plot_details(plot_ids, **kwargs)

    def get_satellite_details(self, ids: str = None, **kwargs) -> list:
        """ Fetch satellite details for the plot ids passed.

        Satellite details returns data for satellite indices and
        crop details for the models subscribed.

        :param str ids: Filter by ids, it can be single id or list
        :param str boundary_id: Filter by boundaryId
        :param str captured_date_time: Filter by capturedDateTime
        :param str min_cloud_coverage: Filters by cloudCoverge >= minCloudCoverage
        :param str max_cloud_coverage: Filters by cloudCoverge <= maxCloudCoverage
        :param str sort_by: Sort by given parameter name
        :param str direction: Order by ascending or descending fashion


        :return: List[SatelliteMetricsResponse]
        """
        return self.cropin_client.get_satellite_details(ids, **kwargs)

    def get_weather_details(self, ids: str = None, **kwargs) -> list:
        """
        Fetches weather details for the plot ids passed.

        :param str ids: Filter by ids, it can be single id or list
        :param str plot_id: Filter by plotId
        :param str _date: Filter by date
        :param str date_to: Filter by specific date range
        :param str date_from: Filter by specific date range
        :param str external_id: Filter by externalId
        :param str sort_by: Sort by given parameter name
        :param str direction: Order by ascending or descending fashion

        :return: List[WeatherDataResponse]
        """
        return self.cropin_client.get_weather_details(ids, **kwargs)

    def get_yield_details(self, ids: str = None, **kwargs) -> list:
        """
        Fetches yield details for the plot ids passed.

        :param str ids: Filter by ids, it can be single id or list
        :param str boundary_id: Filter by boundaryId
        :param str external_id: Filter by externalId
        :param str sort_by: Sort by given parameter name
        :param str direction: Order by ascending or descending fashion
        :return: List[YieldResponse]

        """
        return self.cropin_client.get_yield_details(ids, **kwargs)

    def download_image(self, ca_id: str, image_name, image_type, date) -> dict:
        """

        Returns plot image byte streams for a single plot id at a given date and image type and name.

        :param str boundary_id:  Boundary Id (required)
        :param str _date: Date (required)
        :param str image_name: Plot image name (required)
        :param str org_id: orgId
        :param str image_type: Plot image type
        :param str tile_size: Tile size , default value - [255,255]

        :return: PlotImageResponse

        """
        return self.cropin_client.download_image(ca_id, image_name, image_type, date)
