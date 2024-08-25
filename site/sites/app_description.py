"""This module contains the function to show the rollout groups for an app"""

import copy
import streamlit as st

from modules.functions import Apps
from modules.bing import Bing
from modules.openai import OpenAi
from modules.graph import set_description

if "new_description" not in st.session_state:
    st.session_state["new_description"] = None


def optimize_app_description(apps: Apps, bing: Bing, openAi: OpenAi):
    """Function to create rollout groups for an app"""
    st.subheader("Optimize App Description")

    apps.show_load_or_freshen_apps()

    # App Selection
    if st.session_state["apps"]:
        apps.show_app_selection_list()
        if st.session_state["selected_app"]:
            selected_app = copy.copy(st.session_state["selected_app"])

            st.write()
            st.text_area(
                label="## Current description",
                value=f"{selected_app.get('description', 'N/A')}",
                disabled=True,
            )

            if st.button("Optimize description"):
                results = bing.get_search_results(
                    query=selected_app.get("displayName", ""),
                )

                system = """ You are an Senior Intune App Administrator. Your job is to write the best descriptions for an specific app."""
                prompt = f"""The app is called {selected_app.get("displayName", "")}.
It is a {selected_app.get("appType", "")} app.
The current description is: {selected_app.get("description", "")}.
The top web search results for this app are:
{results}.
"""

                st.session_state["new_description"] = openAi.open_ai_run(
                    prompt=prompt, system=system
                )
                # show new description#
                st.text_area(
                    label="## New description",
                    value=st.session_state["new_description"],
                    disabled=True,
                )
            if st.session_state["new_description"]:
                if st.button("Save description"):
                    response = set_description(
                        selected_app=selected_app,
                        description=st.session_state["new_description"],
                        access_token=apps.access_token,
                    )
                    st.success("Description updated successfully")
