""" """

import base64

import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from loguru import logger

from modules.graph import (
    load_apps,
    get_app_assignments,
    get_installation_status,
    search_groups,
    add_assignment,
    remove_assignment,
    load_app_icon,
)


class Apps:
    """Class to manage the loading and refreshing of apps"""

    def __init__(
        self,
        access_token: str,
    ) -> None:
        self.access_token = access_token

    def show_load_or_freshen_apps(
        self,
    ):
        """Show a button to load or refresh the list of apps"""
        if st.session_state["apps"] is None:
            if st.button("Load Apps"):
                try:
                    st.session_state["apps"] = load_apps(access_token=self.access_token)
                    st.rerun()
                except Exception as e:  # pylint: disable=broad-except
                    st.error(f"An error occurred: {e}")
        else:
            if st.button("Refresh Apps"):
                try:
                    st.session_state["apps"] = load_apps(access_token=self.access_token)
                    st.rerun()
                except Exception as e:  # pylint: disable=broad-except
                    st.error(f"An error occurred: {e}")

    def show_app_selection_list(self):
        """Show a list of apps to select from"""
        app_names = [app["displayName"] for app in st.session_state["apps"]]
        selected_app_name = st.selectbox("Select an App", app_names)

        st.session_state["selected_app"] = next(
            (
                app
                for app in st.session_state["apps"]
                if app["displayName"] == selected_app_name
            ),
            None,
        )

    def get_app_installation_status(self, selected_app_id):
        """Get the installation status of a selected app"""
        return get_installation_status(
            app_id=selected_app_id, access_token=self.access_token
        )

    def show_app_assignments(self, selected_app: dict):
        """Show the details of a selected app"""
        # Display current assignments
        st.write("### Assignments")
        assignments = get_app_assignments(
            app_id=selected_app["id"], access_token=self.access_token
        )
        if assignments:
            for assignment in assignments:
                target_type = assignment["target"].get("@odata.type")
                if target_type == "#microsoft.graph.allLicensedUsersAssignmentTarget":
                    group_name = "All Licensed Users"
                elif target_type == "#microsoft.graph.allDevicesAssignmentTarget":
                    group_name = "All Devices"
                else:
                    group_name = assignment.get("groupName", "N/A")

                group_id = assignment["target"].get("groupId", "N/A")
                st.write(
                    f"**Group Name:** {group_name} (**ID:** {assignment['id']}, **Target Group ID:** {group_id})"
                )
                if st.button(f"Remove {group_name}", key=f"remove_{assignment['id']}"):
                    remove_assignment(
                        app_id=selected_app["id"],
                        assignment_id=assignment["id"],
                        access_token=self.access_token,
                    )
                    st.rerun()
        else:
            st.write("No assignments found.")

    def add_app_assignments(
        self,
        selected_app_id,
    ):
        """Add an app assignment to a group"""
        st.write("### Add Assignment")
        group_query = st.text_input("Search for Group")
        if group_query:
            groups = search_groups(query=group_query, access_token=self.access_token)
            group_names = [group["displayName"] for group in groups]
            selected_group = st.selectbox("Select Group", group_names)
            if st.button("Add Assignment"):
                group_id = next(
                    (
                        group["id"]
                        for group in groups
                        if group["displayName"] == selected_group
                    ),
                    None,
                )
                if group_id:
                    add_assignment(
                        app_id=selected_app_id,
                        group_id=group_id,
                        access_token=self.access_token,
                    )
                    st.rerun()

    def show_picture_description(self, selected_app):
        """Some apps have a large icon that can be displayed"""
        st.write("### Add details")
        app_icon = load_app_icon(
            app_id=selected_app["id"], access_token=self.access_token
        )
        if app_icon:
            large_icon_base64 = app_icon["value"]
            large_icon_data = base64.b64decode(large_icon_base64)
            st.image(large_icon_data, width=100)

        with st.expander("Description"):
            st.write(f"{selected_app.get('description', 'N/A')}")


def show_app_details(selected_app: dict):
    """Show the details of a selected app"""
    st.write("### App info")
    st.write(f"**ID:** {selected_app['id']}")
    st.write(f"**Name:** {selected_app['displayName']}")
    st.write(f"**Publisher:** {selected_app.get('publisher', 'N/A')}")
    st.write(f"**App Version:** {selected_app.get('appVersion', 'N/A')}")
    st.write(
        f"**App Type:** {selected_app.get('@odata.type', 'N/A').replace('#microsoft.graph.', '')}"
    )
    st.write(f"**Created Date:** {selected_app.get('createdDateTime', 'N/A')}")
    st.write(
        f"**Last Modified Date:** {selected_app.get('lastModifiedDateTime', 'N/A')}"
    )
    st.write(f"**Bundle ID:** {selected_app.get('bundleId', 'N/A')}")
    st.write(f"**App Store URL:** {selected_app.get('appStoreUrl', 'N/A')}")
    os_version = selected_app.get("minimumSupportedOperatingSystem", "N/A")
    if os_version != "N/A":
        # find the one with true
        for key, value in os_version.items():
            if value:
                st.write(f"**Minimum Supported OS:** {key}")
                break
    st.write(
        f"**Applicable Device Type:** {selected_app.get('applicableDeviceType', 'N/A')}"
    )
    st.write(f"**Is Assigned:** {selected_app.get('isAssigned', 'N/A')}")

    return_codes = selected_app.get("returnCodes", "N/A")
    if return_codes != "N/A":
        with st.expander("Return codes"):
            for return_code in return_codes:
                try:
                    st.write(
                        f"**Return Code:** {return_code['returnCode']} - **Type:** {return_code['type']}"
                    )
                except TypeError:
                    st.write(f"**Return Code:** {return_code}")
    # detection_rules = selected_app.get("detectionRules", "N/A")
    # st.write("**Detection Rules:**")
    # for detection_rule in detection_rules:
    #     with st.expander(
    #         f"{detection_rule['@odata.type'].replace('#microsoft.graph.', '')}"
    #     ):
    #         for key, value in detection_rule.items():
    #             if key != "@odata.type":
    #                 st.write(f"**{key}:** {value}")
    rules = selected_app.get("rules", "N/A")
    if rules != "N/A":
        st.write("**Rules**")
        for rule in rules:
            with st.expander(f"{rule['ruleType'].replace('#microsoft.graph.', '')}"):
                for key, value in rule.items():
                    if key != "ruleType":
                        st.write(f"**{key}:** {value}")

    st.write(f"**Install Command:** {selected_app.get('installCommandLine', 'N/A')}")
    st.write(
        f"**Uninstall Command:** {selected_app.get('uninstallCommandLine', 'N/A')}"
    )


def plot_status(labels, counts, title):
    """Display installation status as a table, including null values, without index."""
    # Convert all data to DataFrame for display, including counts of 0
    df = pd.DataFrame(zip(labels, counts), columns=["Status", "Count"])
    # Convert DataFrame to HTML, excluding the index
    html = df.to_html(index=False)
    # Display title and table as HTML
    st.write(f"### {title}")
    st.markdown(html, unsafe_allow_html=True)


def process_status(values, start, end, title):
    """Process and plot installation status for devices or users."""
    labels = [
        "Failed",
        "Pending Install",
        "Installed",
        "Not Installed",
        "Not Applicable",
    ]
    counts = values[start:end]
    plot_status(labels, counts, title)


def show_installation_status(installation_status):
    """Show the installation status of a selected app."""
    st.write("### Installation Status")
    if (
        installation_status.get("Values")
        and len(installation_status["Values"][0]) >= 11
    ):
        values = installation_status["Values"][0]
        process_status(values, 1, 6, "Device Status")
        process_status(values, 6, 11, "User Status")
    else:
        st.write("No complete installation status data available.")


def show_rollout_config():
    """Show the configuration options for a rollout"""
    minimum_percentage = st.slider(
        "Minimum percentage for next wave",
        min_value=1,
        max_value=100,
        value=80,
    )

    num_waves = st.number_input("Number of Waves", min_value=1, step=1, value=2)
    group_query = st.text_input("Search for Target Group")
    return minimum_percentage, num_waves, group_query
