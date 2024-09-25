"""This module contains the functions to display app details and manage app assignments"""

import streamlit as st

from modules.functions import (
    show_app_details,
    show_installation_status,
)

from modules.functions import Apps


def show_app_details_page(apps: Apps):
    """Function to display app details and manage app assignments"""
    st.subheader("Add Details")
    apps.show_load_or_freshen_apps()


    # App Selection
    if st.session_state["apps"]:
        apps.show_app_selection_list()

        if st.session_state["selected_app"]:
            selected_app = st.session_state["selected_app"]
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                show_app_details(selected_app=selected_app)
            with col2:
                installation_status = apps.get_app_installation_status(
                    selected_app["id"]
                )
                show_installation_status(
                    installation_status=installation_status,
                )
            with col3:
                # Display app image if available
                apps.show_picture_description(selected_app=selected_app)

            apps.show_app_assignments(selected_app=selected_app)

            apps.add_app_assignments(selected_app_id=selected_app["id"])
