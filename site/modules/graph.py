"""Helper functions for working with the Microsoft Graph API"""

import requests


GRAPH_BASE = "https://graph.microsoft.com"


def load_apps(access_token):
    """Load all apps from the Microsoft Graph API"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        "{GRAPH_BASE}/beta/deviceAppManagement/mobileApps?$filter=(microsoft.graph.managedApp/appAvailability%20eq%20null%20or%20microsoft.graph.managedApp/appAvailability%20eq%20%27lineOfBusiness%27%20or%20isAssigned%20eq%20true)&$orderby=displayName&",
        headers=headers,
    )
    response.raise_for_status()
    return response.json()["value"]


def load_app_icon(app_id, access_token):
    """Load the icon for a given app ID"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"{GRAPH_BASE}/beta/deviceAppManagement/mobileApps/{app_id}",
        headers=headers,
    )
    response.raise_for_status()
    return response.json().get("largeIcon", None)


def get_group_name(group_id, access_token):
    """Get the display name of a group given its ID"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(f"{GRAPH_BASE}/v1.0/groups/{group_id}", headers=headers)
    response.raise_for_status()
    return response.json().get("displayName", "Unknown Group")


def get_app_assignments(app_id, access_token):
    """Get the assignments for a given app ID"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    response = requests.get(
        f"{GRAPH_BASE}/v1.0/deviceAppManagement/mobileApps/{app_id}/assignments",
        headers=headers,
    )
    response.raise_for_status()
    assignments = response.json()["value"]
    for assignment in assignments:
        group_id = assignment["target"].get("groupId", "N/A")
        if group_id != "N/A":
            try:
                assignment["groupName"] = get_group_name(group_id, access_token)
            except requests.exceptions.HTTPError:
                assignment["groupName"] = "Deleted Group"
        else:
            assignment["groupName"] = "N/A"
    return assignments


def get_installation_status(app_id, access_token):
    """Get the installation status for a given app ID"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    url = "{GRAPH_BASE}/beta/deviceManagement/reports/getAppStatusOverviewReport"
    body = {"filter": f"(ApplicationId eq '{app_id}')"}
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json()


def search_groups(query, access_token):
    """Search for groups by name"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    url = f"{GRAPH_BASE}/v1.0/groups?$filter=startswith(displayName,'{query}')"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["value"]


def add_assignment(app_id, group_id, access_token):
    """Add an assignment for a given app ID and group ID"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    url = f"{GRAPH_BASE}/v1.0/deviceAppManagement/mobileApps/{app_id}/assignments"
    body = {
        "target": {
            "@odata.type": "#microsoft.graph.groupAssignmentTarget",
            "groupId": group_id,
        }
    }
    response = requests.post(url, headers=headers, json=body)
    try:
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        raise ValueError(f"Error adding assignment: {e.response.text}") from e


def remove_assignment(app_id, assignment_id, access_token):
    """Remove an assignment for a given app ID and assignment ID"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    url = f"{GRAPH_BASE}/v1.0/deviceAppManagement/mobileApps/{app_id}/assignments/{assignment_id}"
    response = requests.delete(url, headers=headers)
    response.raise_for_status()
    return response.status_code


def get_group_members(group_id, access_token):
    """Get the members of a group given its ID"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    url = f"{GRAPH_BASE}/v1.0/groups/{group_id}/members"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()["value"]


def create_group(group_name, access_token):  #
    """Create a new security group with the given name"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    body = {
        "displayName": group_name,
        "mailEnabled": False,
        "securityEnabled": True,
        "mailNickname": group_name.replace(" ", "_"),
    }
    url = "{GRAPH_BASE}/v1.0/groups"
    response = requests.post(url, headers=headers, json=body)
    response.raise_for_status()
    return response.json()["id"]


def set_description(selected_app, description, access_token):
    """Set the description for a given app ID"""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    selected_app["description"] = description
    id_nr = selected_app.pop("id")
    body = {
        "@odata.type": selected_app.pop("@odata.type"),
        "description": description,
    }
    url = f"{GRAPH_BASE}/beta/deviceAppManagement/mobileApps/{id_nr}"
    response = requests.patch(url, headers=headers, json=body)
    print(response.status_code)
    response.raise_for_status()
    return response
