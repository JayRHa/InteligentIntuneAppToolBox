"""This module contains the functions for logging in with Microsoft Authentication"""

import requests
import streamlit as st
from msal import ConfidentialClientApplication


def initialize_app():
    """Initialize the MSAL app"""
    client_id = st.secrets["CLIENT_ID"]
    tenant_id = st.secrets["TENANT_ID"]
    client_secret = st.secrets["CLIENT_SECRET"]
    authority_url = f"https://login.microsoftonline.com/{tenant_id}"
    return ConfidentialClientApplication(
        client_id, authority=authority_url, client_credential=client_secret
    )


def acquire_access_token(app, code, scopes, redirect_uri):
    """Acquire access token using the authorization code"""
    return app.acquire_token_by_authorization_code(
        code, scopes=scopes, redirect_uri=redirect_uri
    )


def fetch_user_data(access_token):
    """Fetch user data from Microsoft Graph API"""
    headers = {"Authorization": f"Bearer {access_token}"}
    graph_api_endpoint = "https://graph.microsoft.com/v1.0/me"
    response = requests.get(graph_api_endpoint, headers=headers)
    return response.json()


def authentication_process(app):
    """Authenticate user with Microsoft Authentication"""
    scopes = [
        "User.Read",
        "Group.ReadWrite.All",
        "DeviceManagementManagedDevices.ReadWrite.All",
        "DeviceManagementManagedDevices.PrivilegedOperations.All",
        "DeviceManagementApps.ReadWrite.All",
    ]
    redirect_uri = st.secrets["REDIRECT_URI"]
    auth_url = app.get_authorization_request_url(scopes, redirect_uri=redirect_uri)
    st.markdown(f"Please go to [this URL]({auth_url}) and authorize the app.")
    if st.query_params.get("code"):
        st.session_state["auth_code"] = st.query_params.get("code")
        token_result = acquire_access_token(
            app, st.session_state.auth_code, scopes, redirect_uri
        )
        if "access_token" in token_result:
            user_data = fetch_user_data(token_result["access_token"])
            return {"userData": user_data, "token": token_result["access_token"]}
        else:
            st.error("Failed to acquire token. Please check your input and try again.")


def login_ui():
    """UI for logging in with Microsoft Authentication"""
    st.title("Microsoft Authentication")
    app = initialize_app()
    auth = authentication_process(app)
    if auth:
        user_data = auth.get("userData")
        token = auth.get("token")
        st.write("Welcome, ", user_data.get("displayName"))
        st.session_state["authenticated"] = True
        st.session_state["display_name"] = user_data.get("displayName")
        st.session_state["access_token"] = token
        st.rerun()
