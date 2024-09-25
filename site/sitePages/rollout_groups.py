"""Page to create rollout groups for an app"""

import random
import streamlit as st

from modules.graph import (
    search_groups,
    add_assignment,
    get_group_members,
    create_group,
)

from modules.functions import show_rollout_config, Apps
from modules.blob import Blob


def show_rollout_groups(apps: Apps, blob: Blob):
    """Function to create rollout groups for an app"""
    st.subheader("Rollout Group creator")
    apps.show_load_or_freshen_apps()

    if st.session_state["apps"]:
        apps.show_app_selection_list()
        if st.session_state["selected_app"]:
            selected_app = st.session_state["selected_app"]
            st.write(f"### Rollout Groups for {selected_app['displayName']}")
            minimum_percentage, num_waves, group_query = show_rollout_config()

            if group_query:
                groups = search_groups(
                    query=group_query,
                    access_token=apps.access_token,
                )
                group_names = [group["displayName"] for group in groups]
                selected_group = st.selectbox("Select Target Group", group_names)

                group_id = next(
                    (
                        group["id"]
                        for group in groups
                        if group["displayName"] == selected_group
                    ),
                    None,
                )

                if group_id:
                    members = get_group_members(
                        group_id=group_id,
                        access_token=apps.access_token,
                    )
                    total_members = len(members)
                    st.write(f"Total members in the group: {total_members}")

                    rollout_percentages = []
                    for i in range(num_waves):
                        remaining_percentage = 100 - sum(rollout_percentages)
                        if i == num_waves - 1:
                            percentage = remaining_percentage
                        else:
                            percentage = st.slider(
                                f"Wave {i+1} Percentage: ",
                                min_value=1,
                                max_value=remaining_percentage,
                                value=remaining_percentage // (num_waves - i),
                            )
                            st.write(
                                f"{round(total_members /100 * percentage)} Members"
                            )
                        rollout_percentages.append(percentage)

                    if sum(rollout_percentages) != 100:
                        st.warning(
                            "The total percentage must equal 100%. Please adjust the percentages."
                        )

                    if st.button("Create Rollout Groups"):
                        st.session_state["rollout_groups"] = []
                        remaining_members = members.copy()
                        random.shuffle(remaining_members)
                        groups = []
                        for i, percentage in enumerate(rollout_percentages):
                            wave_size = int((percentage / 100) * total_members)
                            wave_members = remaining_members[:wave_size]
                            remaining_members = remaining_members[wave_size:]

                            wave_group_name = f"apps-{selected_group}-wave-{i+1}"
                            wave_group_id = create_group(
                                group_name=wave_group_name,
                                access_token=apps.access_token,
                            )
                            print(f"Wave {i+1} - {wave_group_name}")
                            groups.append(
                                {
                                    "id": wave_group_id,
                                    "displayName": wave_group_name,
                                    "waveNumber": i + 1,
                                }
                            )
                            st.session_state["rollout_groups"].append(
                                {
                                    "wave": i + 1,
                                    "group_name": wave_group_name,
                                    "members": wave_members,
                                }
                            )

                        print(groups)
                        final_json = {
                            "displayName": selected_app["displayName"],
                            "appId": selected_app["id"],
                            "rootGroupId": group_id,
                            "minimum_percentage": minimum_percentage,
                            "groups": groups,
                        }
                        print(final_json)
                        blob.upload_blob(
                            blob_name=f"{selected_app['displayName']}.json",
                            data=final_json,
                        )
                        st.rerun()

            if st.session_state["rollout_groups"]:
                st.write("### Rollout Groups Created")
                for rollout_group in st.session_state["rollout_groups"]:
                    st.write(
                        f"**Wave {rollout_group['wave']}** - {rollout_group['group_name']}: {len(rollout_group['members'])} members"
                    )

                st.write("### Assign Rollout Groups to App")
                wave_group_names = [
                    group["group_name"] for group in st.session_state["rollout_groups"]
                ]
                selected_wave_group_name = st.selectbox(
                    "Select Rollout Group to Assign", wave_group_names
                )
                selected_wave_group = next(
                    (
                        group
                        for group in st.session_state["rollout_groups"]
                        if group["group_name"] == selected_wave_group_name
                    ),
                    None,
                )
                if selected_wave_group:
                    group_id = next(
                        (
                            group["id"]
                            for group in groups
                            if group["displayName"] == selected_wave_group["group_name"]
                        ),
                        None,
                    )
                    if group_id and st.button(
                        f"Assign {selected_wave_group_name} to {selected_app['displayName']}"
                    ):
                        add_assignment(
                            app_id=selected_app["id"],
                            group_id=group_id,
                            access_token=apps.access_token,
                        )
                        st.success(
                            f"Assigned {selected_wave_group_name} to {selected_app['displayName']}"
                        )
