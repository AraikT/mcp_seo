import requests
import json
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()


class AhrefsAPI:
    def __init__(
        self,
        api_key=os.getenv("AHREFS_API_KEY"),
    ):
        self.api_key = api_key
        self.base_url = "https://api.ahrefs.com/v3"

        if not self.api_key:
            raise ValueError(
                "API key Ahrefs not found! Please set AHREFS_API_KEY environment variable."
            )

        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    def _make_request(self, endpoint, params=None):
        url = f"{self.base_url}/{endpoint}"

        # Debug request output
        print(f"\nSending request:")
        print(f"URL: {url}")
        print(f"Headers: {json.dumps(self.headers, indent=2, ensure_ascii=False)}")
        print(f"Params: {json.dumps(params, indent=2, ensure_ascii=False)}")

        try:
            response = requests.get(
                url, headers=self.headers, params=params, timeout=60
            )

            # Debug response output
            print(f"\nReceived response:")
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                print(f"Successful API response")
                return data
            elif response.status_code == 401:
                print(f"Authorization error: Check API key")
                print(f"Error text: {response.text}")
                return {"error": "Invalid API key", "status_code": 401}
            elif response.status_code == 403:
                print(f"Access denied: Insufficient permissions or credits")
                return {
                    "error": "Insufficient access permissions or credits",
                    "status_code": 403,
                }
            elif response.status_code == 429:
                print(f"Request limit exceeded")
                return {"error": "Request limit exceeded", "status_code": 429}
            else:
                print(f"API error: {response.status_code}")
                print(f"Error text: {response.text}")
                return {
                    "error": f"API error {response.status_code}",
                    "details": response.text,
                }

        except requests.ConnectionError:
            print(f"Connection error with Ahrefs API")
            return {"error": "No internet connection or API unavailable"}
        except Exception as e:
            print(f"An error occurred while executing request: {str(e)}")
            return {"error": f"Unexpected error: {str(e)}"}

    def get_refdomains(
        self,
        target,
        limit=100,
        order_by="domain_rating:desc",
        select="domain,domain_rating,links_to_target,first_seen,last_seen,traffic_domain",
    ):
        """
        Get list of referring domains for target domain

        Args:
            target (str): Target domain (e.g., "example.com")
            limit (int): Number of results (maximum 1000)
            order_by (str): Field for sorting with direction (e.g.: "domain_rating:desc", "first_seen:asc")
            select (str): Required parameter - fields for selection, comma-separated
        """
        params = {
            "target": target,
            "limit": limit,
            "order_by": order_by,
            "select": select,
        }

        # Temporary debug information
        print(f"🔍 Sending request site-explorer/refdomains:")
        print(f"   Target: {target}")
        print(f"   Limit: {limit}")
        print(f"   Sorting: {order_by}")
        print(f"   Fields: {select}")

        result = self._make_request("site-explorer/refdomains", params)

        print(f"📊 Result site-explorer/refdomains:")
        print(f"   Response type: {type(result)}")
        if isinstance(result, dict):
            print(f"   Keys in response: {list(result.keys())}")
            if "refdomains" in result:
                refdomains = result["refdomains"]
                print(
                    f"   Number of referring domains: {len(refdomains) if hasattr(refdomains, '__len__') else 'unknown'}"
                )
                print(f"   Refdomains data type: {type(refdomains)}")

        return result

    def get_backlinks(
        self,
        target,
        limit=100,
        order_by="domain_rating_source:desc",
        select="url_from,url_to,domain_rating_source,domain_rating_target,traffic,traffic_domain,anchor,name_source,name_target,noindex,page_size,positions,title,url_from,url_rating_source,url_to",
    ):
        """
        Get list of backlinks for target domain

        Args:
            target (str): Target domain (e.g., "example.com")
            limit (int): Number of results (maximum 1000)
            order_by (str): Field for sorting with direction (e.g.: "url_rating:desc")
            select (str): Required parameter - fields for selection, comma-separated
        """
        params = {
            "target": target,
            "limit": limit,
            "order_by": order_by,
            "select": select,
        }

        return self._make_request("site-explorer/all-backlinks", params)

    def get_organic_keywords(
        self,
        target,
        limit=100,
        date=None,
        order_by="best_position:asc",  # desc
        select="keyword,best_position,best_position_url,keyword_country,keyword_difficulty,last_update,sum_traffic,volume,volume_desktop_pct,volume_mobile_pct",
    ):
        """
        Get organic keywords for target domain

        Args:
            target (str): Target domain
            limit (int): Number of results
            date (str): Date in YYYY-MM-DD format (default - current date)
            order_by (str): Field for sorting with direction (e.g.: "traffic:desc")
            select (str): Required parameter - fields for selection, comma-separated
        """
        # Add this logic:
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")

        params = {
            "target": target,
            "limit": limit,
            "date": date,
            "order_by": order_by,
            "select": select,
        }

        return self._make_request("site-explorer/organic-keywords", params)


# Usage example
if __name__ == "__main__":
    ahrefs = AhrefsAPI()

    # Test domain
    test_domain = "vprognoze.kz"

    # # Get referring domains
    # refdomains_data = ahrefs.get_refdomains(target=test_domain, limit=100)
    # print("\n=== REFERRING DOMAINS ===")
    # print(json.dumps(refdomains_data, ensure_ascii=False, indent=2))

    # # Save data to file
    # with open("ahrefs_refdomains.json", "w", encoding="utf-8") as file:
    #     json.dump(refdomains_data, file, ensure_ascii=False, indent=2)

    # backlinks_data = ahrefs.get_backlinks(target=test_domain, limit=100)
    # print("\n=== BACKLINKS ===")
    # print(json.dumps(backlinks_data, ensure_ascii=False, indent=2))

    # # Save data to file
    # with open("ahrefs_backlinks.json", "w", encoding="utf-8") as file:
    #     json.dump(backlinks_data, file, ensure_ascii=False, indent=2)

    organic_keywords = ahrefs.get_organic_keywords(target=test_domain, limit=100)
    print("\n=== Organic keywords ===")
    print(json.dumps(organic_keywords, ensure_ascii=False, indent=2))

    # Save data to file
    with open("organic_keywords.json", "w", encoding="utf-8") as file:
        json.dump(organic_keywords, file, ensure_ascii=False, indent=2)
