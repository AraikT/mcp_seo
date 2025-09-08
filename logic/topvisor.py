import requests
import json
import csv
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class TopvisorAPI:
    def __init__(
        self,
        user_id=os.getenv("TOPVISOR_USER_ID"),
        api_key=os.getenv("TOPVISOR_API_KEY"),
    ):
        self.user_id = user_id
        self.api_key = api_key
        self.base_url = "https://api.topvisor.com/v2/json/get"

        if not self.api_key:
            raise ValueError("API key Topvisor not found! ")

        self.headers = {
            "Content-Type": "application/json",
            "User-Id": self.user_id,
            "Authorization": f"bearer {self.api_key}",
        }

    def _make_request(self, endpoint, payload=None, csv=False):
        url = f"{self.base_url}/{endpoint}"

        # Debug request output
        print(f"\nSending request:")
        print(f"URL: {url}")
        print(f"Headers: {json.dumps(self.headers, indent=2, ensure_ascii=False)}")
        print(f"Payload: {json.dumps(payload, indent=2, ensure_ascii=False)}")

        try:
            response = requests.post(
                url, headers=self.headers, json=payload, timeout=60
            )

            # Debug response output
            print(f"\nReceived response:")
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                # response.text is CSV formatted string with semicolon delimiter
                if csv:
                    return {"result": response.text, "status_code": 200}
                else:
                    print(f"Successful API response")
                    return response.json()
            elif response.status_code == 401:
                print(f"Authorization error: Check API key")
                print(f"Error text: {response.text}")
                return {"error": "Invalid API key", "status_code": 401}
            elif response.status_code == 403:
                print(f"Access denied: Insufficient permissions")
                return {"error": "Insufficient access permissions", "status_code": 403}
            else:
                print(f"API error: {response.status_code}")
                print(f"Error text: {response.text}")
                return {
                    "error": f"API error {response.status_code}",
                    "details": response.text,
                }

        except requests.ConnectionError:
            print(f"Connection error with Topvisor API")
            return {"error": "No internet connection or API unavailable"}
        except Exception as e:
            print(f"An error occurred while executing request: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    def get_projects(self):
        """Get user's projects list"""
        payload = {}
        return self._make_request("projects_2/projects")

    def get_project_keywords(self, project_id, folder_id=None, group_id=None):
        """Get project keywords"""
        payload = {
            "project_id": project_id
        }  # Initialize payload dict with required project ID
        if folder_id:  # Check if folder_id parameter was provided
            payload["folder_id"] = (
                folder_id  # Add folder_id to payload for filtering by folder
            )
        if group_id:  # Check if group_id parameter was provided
            payload["group_id"] = group_id
        return self._make_request("keywords_2/keywords", payload)

    def get_project_positions(
        self,
        project_id=4878567,
        regions_indexes=["33"],
        date1=None,
        date2=None,
        limit=1000,
        offset=0,
    ):
        """Get project keyword position history"""
        if date1 is None:
            date1 = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if date2 is None:
            date2 = datetime.now().strftime("%Y-%m-%d")

        payload = {
            "project_id": project_id,
            "regions_indexes": regions_indexes,
            "date1": date1,
            "date2": date2,
            "limit": limit,
            "offset": offset,
        }

        # Temporary debug information
        print(f"🔍 Sending request positions_2/history:")
        print(f"   Project ID: {project_id}")
        print(f"   Period: {date1} - {date2}")
        print(f"   Regions: {regions_indexes}")
        print(f"   Limit: {limit}")

        result = self._make_request("positions_2/history", payload)

        print(f"📊 Result positions_2/history:")
        print(f"   Response type: {type(result)}")
        if isinstance(result, dict):
            print(f"   Keys in response: {list(result.keys())}")
            if "result" in result:
                positions = result["result"]
                print(
                    f"   Number of positions: {len(positions) if hasattr(positions, '__len__') else 'unknown'}"
                )
                print(f"   Position data type: {type(positions)}")

        return result

    def get_positions_summary(self, project_id, date1=None, date2=None):
        """Get project position summary"""
        if date1 is None:
            date1 = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        if date2 is None:
            date2 = datetime.now().strftime("%Y-%m-%d")

        payload = {"project_id": project_id, "date1": date1, "date2": date2}
        return self._make_request("positions_2/summary", payload)

    def get_project_competitors(self, project_id):
        """Get project competitors list"""
        payload = {"project_id": project_id}
        return self._make_request("projects_2/competitors", payload)

    def get_project_regions(self, project_id):
        """Get project regions and search engines"""
        payload = {"project_id": project_id}
        
        response = self._make_request("positions_2/searchers_regions/export", payload, csv=True)
        data = []
        for row in csv.reader(response["result"].splitlines(), delimiter=';'):
            data.append(
                {
                    "search_engine_key": row[0],
                    "name": row[1],
                    "country_code": row[2],
                    "language": row[3],
                    "region_device": row[4],
                    "depth": row[5],
                }
            )
        
        return {"result": data, "status_code": response.get("status_code", 200)}

    def get_keyword_folders(self, project_id):
        """Get project keyword folders"""
        payload = {"project_id": project_id}
        return self._make_request("keywords_2/folders", payload)

    def get_keyword_groups(self, project_id, folder_id=None):
        """Get project keyword groups"""
        payload = {"project_id": project_id}
        if folder_id:
            payload["folder_id"] = folder_id

        return self._make_request("keywords_2/groups", payload)

    def get_balance_info(self):
        """Get balance information"""
        payload = {}
        return self._make_request("bank_2/info", payload)


# if __name__ == "__main__":
#     topvisor = TopvisorAPI()
#     print(topvisor.get_project_keywords(project_id=18788866, folder_id=None, group_id=50348785))

# if __name__ == "__main__":
#     topvisor = TopvisorAPI()
#     print(topvisor.get_project_regions(23059018))

if __name__ == "__main__":
    topvisor = TopvisorAPI()
    a = topvisor.get_project_positions(project_id=23059018, regions_indexes=["42"])
    print(a)
    # save the received data into a local file
    with open("project_keywords_history.json", "w", encoding="utf-8") as file:
        json.dump(a, file, ensure_ascii=False, indent=2)
