import requests
import json
import base64

class AzDevOps:
    """AZDevOps class"""
    def __init__(
        self,
        PAT: str,
        Organization: str,
        Project: str,
        Repository: str,
        Branch: str,
    ):
        self.PAT = PAT
        self.Organization = Organization
        self.Project = Project
        self.Repository = Repository
        self.Branch = Branch
        self.BaseURL = f"https://dev.azure.com/{self.Organization}"
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {base64.b64encode(f":{self.PAT}".encode()).decode()}'
        }

    def get_projects(self):
        """Get projects method"""
        response = requests.get(f"{self.BaseURL}/_apis/projects?api-version=7.1", headers=self.headers)
        json_response = response.json().get("value")
        return json_response
    
    def get_commits(self):
        """Get commits method"""
        response = requests.get(f"{self.BaseURL}/{self.Project}/_apis/git/repositories/{self.Repository}/commits?api-version=7.1", headers=self.headers)
        json_response = response.json().get("value")
        return json_response
    
    def get_latest_commit(self):
        """Get latest commit method"""
        response = requests.get(f"{self.BaseURL}/{self.Project}/_apis/git/repositories/{self.Repository}/commits?api-version=7.1", headers=self.headers)
        json_response = response.json().get("value")[0]
        return json_response
    
    def post_commit(self, commit):
        """Post commit method"""

        base_commit = {
            "refUpdates": [
                {
                    "name": f"refs/heads/{self.Branch}",
                    "oldObjectId": self.get_latest_commit().get("commitId")
                }
            ],
            "commits": [commit]
        }
        # body = json.dumps(base_commit)

        post_response = requests.post(f"{self.BaseURL}/{self.Project}/_apis/git/repositories/{self.Repository}/pushes?api-version=7.1", headers=self.headers, data=json.dumps(base_commit))

        # response = requests.post(f"{self.BaseURL}/{self.Project}/_apis/git/repositories/{self.Repository}/commits?api-version=7.1", headers=self.headers, data=body)
        # # json_response = response.json()
        return post_response




# # Get a client (the "core" client provides access to projects, teams, etc)
# core_client = connection.clients.get_core_client()

# # Get the first page of projects
# get_projects_response = core_client.get_projects()
# index = 0
# while get_projects_response is not None:
#     for project in get_projects_response.value:
#         pprint.pprint("[" + str(index) + "] " + project.name)
#         index += 1
#     if get_projects_response.continuation_token is not None and get_projects_response.continuation_token != "":
#         # Get the next page of projects
#         get_projects_response = core_client.get_projects(continuation_token=get_projects_response.continuation_token)
#     else:
#         # All projects have been retrieved
#         get_projects_response = None