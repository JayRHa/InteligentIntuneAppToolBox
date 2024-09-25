"""Module for uploading apps to the site"""

import os

from azure.storage.blob import BlobServiceClient


import streamlit as st
from loguru import logger
import json


import os
import streamlit as st
from azure.storage.blob import BlobServiceClient

from modules.openai import OpenAi


def upload_app(openai: OpenAi):
    """Upload app to Intune"""
    st.subheader("App package upload")
    CONNECTION_STRING = st.secrets["STORAG_CONNECTION_STRING"]
    uploaded_file = st.file_uploader("Choose a file")
    upload_AppName = st.text_input("Enter the app name")
    upload_InstallCommands = st.text_input("Enter Installation Commands")


    if st.button("Generate an AI Assisted silent install command"):

        if upload_InstallCommands is not None: st.session_state["providedCommands"] = upload_InstallCommands
        system = """You are an Senior Intune App Administrator. Your job is to get the Silent Install Commands for an specific app. You should only return the commands and nothing else."""
        prompt = f"""The app is called {upload_AppName}.
the executable file is {uploaded_file.name} and in addition to the generated parameters.
you must make sure it includes but does not duplicate {upload_InstallCommands}.
"""

        st.session_state["ai_installCommands"] = openai.open_ai_run(
            prompt=prompt, system=system
        )
        # show new description#
        st.text_area(
            label="## AI Generated Silent Install Commands",
            value=st.session_state["ai_installCommands"]
        )

    accept_AI = st.checkbox("Accept AI generated Silent Install Commands") 
    if accept_AI is not None:
        if accept_AI is True:
            st.session_state["finalInstallCommands"] = st.session_state["ai_installCommands"]
        else:
            st.session_state["finalInstallCommands"] = st.session_state["providedCommands"]
    
    st.text_area(
        label="## Final Silent Install Commands",
        value=st.session_state["finalInstallCommands"],
        disabled=True,
    )
    
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

            container_name = st.secrets["CONTAINER_NAME"]

            blob_name = uploaded_file.name
            blob_service_client = BlobServiceClient.from_connection_string(
                CONNECTION_STRING
            )
            container_client = blob_service_client.get_container_client(container_name)
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(bytes_data, overwrite=True)

            content_json = {
                "displayName": upload_AppName,
                "description": upload_AppName,
                "publisher": "Publisher",
                "vendorUrl": "",
                "appIconURL": "",
                "silentInstallCommands": st.session_state["finalInstallCommands"],
            }

            #Convert to json and upload to blob
            content_json = json.dumps(content_json)
            blob_name = f"{upload_AppName}.json"
            blob_client = container_client.get_blob_client(blob_name)
            blob_client.upload_blob(content_json, overwrite=True)
