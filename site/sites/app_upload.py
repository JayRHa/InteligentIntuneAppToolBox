"""Module for uploading apps to the site"""

import os

import streamlit as st
from loguru import logger
from modules.blob import Blob
from modules.bing import Bing
from modules.openai import OpenAi

from modules.openai import OpenAi
from .app_description import generate_description


def upload_app(openai: OpenAi, blob: Blob, bing: Bing, openAi: OpenAi):
    """Upload app to Intune"""
    st.subheader("App package upload")
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

            container_name = "test"
            blob_name = uploaded_file.name

            blob.upload_blob_bytes(
                blob_name=blob_name,
                data=bytes_data,
            )

            description = generate_description(
                bing=bing,
                openAi=openAi,
                display_name=blob_name,
                app_type="win32",
                description="",
            )

            content_json = {
                "displayName": blob_name,
                "description": description,
                "publisher": "",
                "vendorUrl": "",
                "installationType": installation_type,
            }
            blob.upload_blob(
                blob_name="definition.json",
                data=content_json,
            )

            system = """ You are an Senior Intune App Administrator. Your job is to answer with an valid powershell script to install the following app."""
            prompt = f"""The app is called {blob_name}.
            Only answer with code and nothing else. It should be an valid installation script for the app.
            """
            script = openAi.open_ai_run(prompt=prompt, system=system)

            blob.upload_blob(
                blob_name="installation.ps1",
                data=script,
            )

            st.write(f"File uploaded to {blob_name}")
