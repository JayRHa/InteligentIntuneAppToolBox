import json
from azure.storage.blob import BlobServiceClient


class Blob:
    def __init__(
        self, storage_account_name: str, storage_account_key: str, container_name: str
    ):
        self.storage_account_name = storage_account_name
        self.storage_account_key = storage_account_key
        self.container_name = container_name

    def upload_blob(self, blob_name: str, data: dict):
        """Uploads a JSON object to the specified blob"""
        blob_service_client = BlobServiceClient.from_connection_string(
            f"DefaultEndpointsProtocol=https;AccountName={self.storage_account_name};AccountKey={self.storage_account_key};EndpointSuffix=core.windows.net"
        )
        blob_client = blob_service_client.get_blob_client(
            container=self.container_name, blob=blob_name
        )
        blob_client.upload_blob(json.dumps(data), overwrite=True)

    def upload_blob_bytes(self, blob_name: str, data: bytes):
        """Uploads a bytes object to the specified blob"""
        blob_service_client = BlobServiceClient.from_connection_string(
            f"DefaultEndpointsProtocol=https;AccountName={self.storage_account_name};AccountKey={self.storage_account_key};EndpointSuffix=core.windows.net"
        )
        blob_client = blob_service_client.get_blob_client(
            container=self.container_name, blob=blob_name
        )
        blob_client.upload_blob(data, overwrite=True)
