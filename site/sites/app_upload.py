"""Module for uploading apps to the site"""

import os

from azure.storage.blob import BlobServiceClient


import streamlit as st
from loguru import logger


import os
import streamlit as st
from azure.storage.blob import BlobServiceClient

from modules.openai import OpenAi


def upload_app(openai: OpenAi):
    """Upload app to Intune"""
    st.subheader("App package upload")
    CONNECTION_STRING = st.secrets["STORAG_CONNECTION_STRING"]
    uploaded_file = st.file_uploader("Choose a file")

    installation_type = st.radio(
        "Select installation type",
        ("System installation", "User installation"),
    )

    if uploaded_file is not None:
        # Show butotn
        if st.button("Upload"):
            # To read file as bytes:
            bytes_data = uploaded_file.getvalue()
            st.write(bytes_data)

            container_name = "test"

            blob_name = uploaded_file.name
            blob_service_client = BlobServiceClient.from_connection_string(
                CONNECTION_STRING
            )
            container_client = blob_service_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(bytes_data, overwrite=True)



            content_json = {
                "displayName": "",
                "description": "",
                "publisher": "",
                "vendorUrl": "",
            }
