"""This module contains all functionality interacting with hpc apps.
"""
import ast

from marketplace.client import MarketPlaceClient

from ..utils import check_capability_availability


class HpcGatewayApp(MarketPlaceClient):
    """General HPC gateway app with all the supported capabilities."""

    @check_capability_availability("update_dataset")
    def upload(self, resourceid, source_path=str):
        """Upload file to remote path `resourceid` from source path"""
        with open(source_path, "rb") as fh:
            self.put(
                path="updateDataset",
                params={"resourceid": f"{resourceid}"},
                files={"file": fh},
            )

    @check_capability_availability("get_dataset")
    def download(self, resourceid, filename) -> str:
        """Download file from `resourceid`
        return str of content"""
        resp = self.get(
            path="getDataset",
            params={"resourceid": f"{resourceid}"},
            json={"filename": filename},
        )

        return resp.text

    @check_capability_availability("delete_dataset")
    def delete(self, resourceid, filename):
        """Delete file from `resourceid`"""
        self.delete(
            path="deleteDataset",
            params={"resourceid": f"{resourceid}"},
            json={"filename": filename},
        )

    @check_capability_availability("new_transformation")
    def new_job(self, config=None):
        """Create a new job and return resourceid for further operations"""
        resp = self.post(path="newTransformation", json=config).text
        resp = ast.literal_eval(resp)

        return resp["resourceid"]

    @check_capability_availability("get_transpormationList")
    def list_jobs(self):
        """List the jobs"""
        return self.get(path="getTransformationList").json()

    @check_capability_availability("startTransformation")
    def run_job(self, resourceid):
        """
        Submit job in the path `resourceid`
        """
        resp = self.post(
            path="startTransformation", params={"resourceid": f"{resourceid}"}
        )

        return resp.text

    @check_capability_availability("stop_transformation")
    def cancel_job(self, resourceid):
        """Cancel a job"""
        resp = self.post(
            path="stopTransformation", params={"resourceid": f"{resourceid}"}
        )

        return resp.text

    @check_capability_availability("delete_transformation")
    def delete_job(self, resourceid):
        """
        Delete job corresponded to path `resourceid`.
        """
        resp = self.delete(
            path="deleteTransformation", params={"resourceid": f"{resourceid}"}
        )

        return resp.text
