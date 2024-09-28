"""Streamlit app for deploying Intune apps to groups"""

import os
import streamlit as st
from loguru import logger


from modules.functions import Apps
from modules.openai import OpenAi
from modules.blob import Blob
from modules.bing import Bing

from sites.app_details import show_app_details_page
from sites.rollout_groups import show_rollout_groups
from sites.app_description import optimize_app_description
from sites.app_upload import upload_app
from sites.client_log_summarizer import summarize_logfile

from login_ui import login_ui
# Configuration settings for your Azure AD app

apps = Apps(
    access_token=st.session_state.get("access_token"),
)

openai = OpenAi(
    endpoint=os.getenv("OPENAI_ENDPOINT", ""),
    key=os.getenv("OPENAI_KEY", ""),
    model=os.getenv("OPENAI_MODEL", ""),
)

blob = Blob(
    storage_account_name=os.getenv("STORAGE_ACCOUNT_NAME", ""),
    storage_account_key=os.getenv("STORAGE_ACCOUNT_KEY", ""),
    container_name=os.getenv("CONTAINER_NAME", ""),
)

bing = Bing(secret=os.getenv("BING_SECRET", ""))

# Set page layout to wide
st.set_page_config(layout="wide")

# Initialize session state for storing app data
if "apps" not in st.session_state:
    st.session_state["apps"] = None
if "rollout_groups" not in st.session_state:
    st.session_state["rollout_groups"] = []
if "selected_app" not in st.session_state:
    st.session_state["selected_app"] = None


def main():
    """Main function for the Streamlit app"""
    if not st.session_state.get("authenticated", False):
        login_ui()
    else:
        st.title("Intelligent Intune App Tool Box")
        st.sidebar.title("Navigation")

        st.sidebar.markdown(f"Welcome, {st.session_state.get('display_name')}")

        app_mode = st.sidebar.selectbox(
            "Choose the page",
            [
                "App Details",
                "App Rollout Groups",
                "App Description Creator",
                "App Uploaded",
                "IME Log Summarizer",
            ],
        )

        if app_mode == "App Details":
            show_app_details_page(apps=apps)
        elif app_mode == "App Rollout Groups":
            show_rollout_groups(apps=apps, blob=blob)
        elif app_mode == "App Description Creator":
            optimize_app_description(apps=apps, bing=bing, openAi=openai)
        elif app_mode == "App Uploaded":
            upload_app(openai=openai, blob=blob, bing=bing, openAi=openai)
        elif app_mode == "IME Log Summarizer":
            summarize_logfile(openai=openai)

            # https://storeedgefd.dsx.mp.microsoft.com/v9.0/manifestSearch
            # {"MaximumResults":50,"Filters":[{"PackageMatchField":"Market","RequestMatch":{"KeyWord":"US","MatchType":"CaseInsensitive"}}],"Query":{"KeyWord":"Green","MatchType":"Substring"}}


if __name__ == "__main__":
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    main()
