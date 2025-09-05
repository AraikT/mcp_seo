import arxiv
import json
import os
from typing import List, Optional
from fastmcp import FastMCP
from topvisor import TopvisorAPI
from ahrefs import AhrefsAPI
from dotenv import load_dotenv

load_dotenv()

PAPER_DIR = "papers"

# Initialize FastMCP server
mcp = FastMCP("research")


@mcp.tool()
def search_papers(topic: str, max_results: int = 5) -> List[str]:
    """
    Search for papers on arXiv based on a topic and store their information.

    Args:
        topic: The topic to search for
        max_results: Maximum number of results to retrieve (default: 5)

    Returns:
        List of paper IDs found in the search
    """

    # Use arxiv to find the papers
    client = arxiv.Client()

    # Search for the most relevant articles matching the queried topic
    search = arxiv.Search(
        query=topic, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance
    )

    papers = client.results(search)

    # Create directory for this topic
    path = os.path.join(PAPER_DIR, topic.lower().replace(" ", "_"))
    os.makedirs(path, exist_ok=True)

    file_path = os.path.join(path, "papers_info.json")

    # Try to load existing papers info
    try:
        with open(file_path, "r") as json_file:
            papers_info = json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        papers_info = {}

    # Process each paper and add to papers_info
    paper_ids = []
    for paper in papers:
        paper_ids.append(paper.get_short_id())
        paper_info = {
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "summary": paper.summary,
            "pdf_url": paper.pdf_url,
            "published": str(paper.published.date()),
        }
        papers_info[paper.get_short_id()] = paper_info

    # Save updated papers_info to json file
    with open(file_path, "w") as json_file:
        json.dump(papers_info, json_file, indent=2)

    print(f"Results are saved in: {file_path}")

    return paper_ids


@mcp.tool()
def extract_info(paper_id: str) -> str:
    """
    Search for information about a specific paper across all topic directories.

    Args:
        paper_id: The ID of the paper to look for

    Returns:
        JSON string with paper information if found, error message if not found
    """

    for item in os.listdir(PAPER_DIR):
        item_path = os.path.join(PAPER_DIR, item)
        if os.path.isdir(item_path):
            file_path = os.path.join(item_path, "papers_info.json")
            if os.path.isfile(file_path):
                try:
                    with open(file_path, "r") as json_file:
                        papers_info = json.load(json_file)
                        if paper_id in papers_info:
                            return json.dumps(papers_info[paper_id], indent=2)
                except (FileNotFoundError, json.JSONDecodeError) as e:
                    print(f"Error reading {file_path}: {str(e)}")
                    continue

    return f"There's no saved information related to paper {paper_id}."


@mcp.tool()
def check_topvisor_setup() -> str:
    """
    Check Topvisor API setup and connection.

    Returns:
        JSON string with setup check results
    """
    try:

        # Check for API key presence
        api_key = os.getenv("TOPVISOR_API_KEY")

        if not api_key:
            return json.dumps(
                {
                    "status": "error",
                    "message": "API key not found",
                    "checks": {
                        "env_file": os.path.exists(".env"),
                        "api_key_set": False,
                        "api_connection": False,
                    },
                    "help": "Create .env file and add TOPVISOR_API_KEY=your_key",
                },
                indent=2,
                ensure_ascii=False,
            )

        # Check API connection
        try:
            topvisor = TopvisorAPI()
            result = topvisor.get_balance_info()

            if result and "error" in result:
                return json.dumps(
                    {
                        "status": "warning",
                        "message": f'API key found, but there is a problem: {result["error"]}',
                        "checks": {
                            "env_file": True,
                            "api_key_set": True,
                            "api_connection": False,
                        },
                        "help": "Check API key validity and account balance",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            elif result and "result" in result:
                # Check data type in result["result"]
                result_data = result["result"]
                balance = "N/A"

                if isinstance(result_data, dict):
                    # If result["result"] is a dictionary
                    balance = result_data.get("balance", "N/A")
                elif isinstance(result_data, list) and len(result_data) > 0:
                    # If result["result"] is a list, take the first element
                    first_item = result_data[0]
                    if isinstance(first_item, dict):
                        balance = first_item.get("balance", "N/A")
                elif hasattr(result_data, "get"):
                    # Additional check for objects with get method
                    balance = result_data.get("balance", "N/A")

                return json.dumps(
                    {
                        "status": "success",
                        "message": f"Everything is set up correctly! Balance: {balance}",
                        "checks": {
                            "env_file": True,
                            "api_key_set": True,
                            "api_connection": True,
                        },
                        "balance": balance,
                        "result_type": type(result_data).__name__,
                        "raw_result": (
                            result_data
                            if len(str(result_data)) < 500
                            else str(result_data)[:500] + "..."
                        ),
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            else:
                return json.dumps(
                    {
                        "status": "error",
                        "message": "Unexpected response from API",
                        "checks": {
                            "env_file": True,
                            "api_key_set": True,
                            "api_connection": False,
                        },
                    },
                    indent=2,
                    ensure_ascii=False,
                )

        except Exception as api_error:
            # Detailed error information for debugging
            error_details = {
                "error_type": type(api_error).__name__,
                "error_message": str(api_error),
            }

            # If this is AttributeError, likely a data type issue
            if isinstance(api_error, AttributeError):
                error_details["likely_cause"] = "Unexpected data format from API"
                error_details["suggestion"] = "API returned data in unexpected format"

            return json.dumps(
                {
                    "status": "error",
                    "message": f"API connection error: {str(api_error)}",
                    "checks": {
                        "env_file": os.path.exists(".env"),
                        "api_key_set": bool(api_key),
                        "api_connection": False,
                    },
                    "error_details": error_details,
                    "help": "Check internet connection and API key validity",
                },
                indent=2,
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "message": f"Setup check error: {str(e)}",
                "help": "See TOPVISOR_SETUP.md file for instructions",
            },
            indent=2,
            ensure_ascii=False,
        )


@mcp.tool()
def get_topvisor_projects() -> str:
    """
    Get a list of all user projects in Topvisor.

    Returns:
        JSON string with a list of projects and their basic information
    """
    try:
        topvisor = TopvisorAPI()
        result = topvisor.get_projects()
        

        # Check for API errors
        if result and "error" in result:
            return json.dumps(
                {
                    "status": "error",
                    "message": f"API error: {result['error']}",
                    "details": result.get(
                        "details", "Check TOPVISOR_SETUP.md file for setup"
                    ),
                },
                indent=2,
                ensure_ascii=False,
            )

        if result and "result" in result:
            projects = result["result"]
            project_info = []

            for project in projects:
                info = {
                    "id": project.get("id"),
                    "name": project.get("name"),
                    "url": project.get("url"),
                    "status": project.get("status"),
                    "created": project.get("date_add"),
                }
                project_info.append(info)

            return json.dumps(
                {
                    "status": "success",
                    "projects": project_info,
                    "total_count": len(project_info),
                },
                indent=2,
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Failed to get project data",
                    "help": "Check TOPVISOR_SETUP.md file for API key setup",
                },
                indent=2,
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "message": f"Error getting projects: {str(e)}",
                "help": "Create .env file with TOPVISOR_API_KEY. See TOPVISOR_SETUP.md",
            },
            indent=2,
            ensure_ascii=False,
        )


@mcp.tool()
def get_topvisor_keywords(
    project_id: int = 4878567,
    folder_id: Optional[int] = None,
    group_id: Optional[int] = None,
) -> str:
    """
    Get project keywords in Topvisor.

    Args:
        project_id: Project ID in Topvisor
        folder_id: Folder ID (optional)
        group_id: Group ID (optional)

    Returns:
        JSON string with project keywords
    """
    try:
        topvisor = TopvisorAPI()
        result = topvisor.get_project_keywords(project_id, folder_id, group_id)

        if result and "result" in result:
            keywords = result["result"]
            keywords_info = []

            for keyword in keywords:
                info = {
                    "id": keyword.get("id"),
                    "name": keyword.get("name"),
                    "folder_id": keyword.get("folder_id"),
                    "group_id": keyword.get("group_id"),
                    "url": keyword.get("url"),
                    "tags": keyword.get("tags", []),
                }
                keywords_info.append(info)

            return json.dumps(
                {
                    "status": "success",
                    "project_id": project_id,
                    "keywords": keywords_info,
                    "total_count": len(keywords_info),
                },
                indent=2,
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Failed to get keyword data",
                },
                indent=2,
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "message": f"Error getting keywords: {str(e)}",
            },
            indent=2,
            ensure_ascii=False,
        )


@mcp.tool()
def get_topvisor_positions_history(
    project_id: int,
    regions_indexes=["33"],
    date1: Optional[str] = None,
    date2: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
) -> str:
    """
    Get keyword position history for a project in Topvisor.

    Args:
        project_id: Project ID in Topvisor
        regions_indexes: Region indexes. For project 23059018 regions_indexes equals ["42"]
        date1: Period start date in YYYY-MM-DD format (default 7 days ago)
        date2: Period end date in YYYY-MM-DD format (default today)
        limit: Number of records (default 100 for speed)
        offset: Pagination offset (default 0)

    Returns:
        JSON string with position history
    """
    try:
        topvisor = TopvisorAPI()
        result = topvisor.get_project_positions(
            project_id, regions_indexes, date1, date2, limit, offset
        )

        # Safe debug information (without full API response)
        debug_info = {
            "sent_params": {
                "project_id": project_id,
                "regions_indexes": regions_indexes,
                "date1": date1,
                "date2": date2,
                "limit": limit,
                "offset": offset,
            },
            "api_response_type": type(result).__name__,
            "api_response_keys": (
                list(result.keys()) if isinstance(result, dict) else "not_dict"
            ),
            # Safe API response version - structure only, no data
            "api_response_summary": {
                "has_result_key": (
                    "result" in result if isinstance(result, dict) else False
                ),
                "has_error_key": (
                    "error" in result if isinstance(result, dict) else False
                ),
                "result_type": (
                    type(result.get("result")).__name__
                    if isinstance(result, dict) and "result" in result
                    else "no_result"
                ),
                "result_length": (
                    len(result.get("result"))
                    if isinstance(result, dict)
                    and "result" in result
                    and hasattr(result.get("result"), "__len__")
                    else "no_length"
                ),
            },
        }

        # Quick check for API errors
        if not result:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Empty response from API",
                    "debug": debug_info,
                },
                ensure_ascii=False,
            )

        if isinstance(result, dict) and "error" in result:
            return json.dumps(
                {
                    "status": "error",
                    "message": f"API error: {result['error']}",
                    "debug": debug_info,
                },
                ensure_ascii=False,
            )

        if isinstance(result, dict) and "result" in result:
            result_data = result["result"]

            # Check that result_data is not None
            if result_data is None:
                return json.dumps(
                    {
                        "status": "error",
                        "message": "API returned result=None (no position data for specified period)",
                        "debug": {
                            **debug_info,
                            "positions_details": {
                                "result_data_type": "NoneType",
                                "result_data_value": None,
                                "reason": "API returned result=None, likely no position data for specified period",
                            },
                        },
                    },
                    ensure_ascii=False,
                )

            positions_info = []

            # Update debug information for new structure
            debug_info["positions_details"] = {
                "result_data_type": type(result_data).__name__,
                "result_data_keys": (
                    list(result_data.keys())
                    if isinstance(result_data, dict)
                    else "not_dict"
                ),
                "has_keywords_key": (
                    "keywords" in result_data
                    if isinstance(result_data, dict)
                    else False
                ),
            }

            # Process new data structure
            if isinstance(result_data, dict) and "keywords" in result_data:
                keywords = result_data["keywords"]
                debug_info["positions_details"]["keywords_count"] = (
                    len(keywords) if hasattr(keywords, "__len__") else "no_length"
                )

                for keyword_data in keywords:
                    if isinstance(keyword_data, dict):
                        keyword_name = keyword_data.get("name", "unknown")
                        positions_data = keyword_data.get("positionsData", {})

                        # Process each date in positionsData
                        for date_key, position_info in positions_data.items():
                            if (
                                isinstance(position_info, dict)
                                and "position" in position_info
                            ):
                                # Parse date key (format: "2025-08-15:19294818:33")
                                parts = date_key.split(":")
                                if len(parts) >= 3:
                                    date = parts[0]
                                    project_id_from_key = parts[1]
                                    region_from_key = parts[2]

                                    position_value = position_info["position"]

                                    positions_info.append(
                                        {
                                            "keyword_name": keyword_name,
                                            "date": date,
                                            "position": position_value,
                                            "project_id": project_id_from_key,
                                            "region": region_from_key,
                                            "position_numeric": (
                                                int(position_value)
                                                if position_value.isdigit()
                                                else None
                                            ),
                                            "is_not_ranking": position_value
                                            == "--",  # Flag for positions outside top
                                        }
                                    )

            return json.dumps(
                {
                    "status": "success",
                    "project_id": project_id,
                    "regions_indexes": regions_indexes,
                    "period": f"{date1 or 'auto'} - {date2 or 'auto'}",
                    "positions": positions_info,
                    "total_count": len(positions_info),
                    "unique_keywords": len(
                        set(pos["keyword_name"] for pos in positions_info)
                    ),
                    "date_range": {
                        "start": min(
                            (pos["date"] for pos in positions_info), default="no_data"
                        ),
                        "end": max(
                            (pos["date"] for pos in positions_info), default="no_data"
                        ),
                    },
                    "limit": limit,
                    "offset": offset,
                    "debug": debug_info,
                },
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Failed to get position data",
                    "debug": debug_info,
                },
                ensure_ascii=False,
            )

    except Exception as e:
        # More detailed error handling
        return json.dumps(
            {
                "status": "error",
                "message": f"Error getting positions: {str(e)}",
                "error_type": type(e).__name__,
                "error_details": str(e),
            },
            ensure_ascii=False,
        )


@mcp.tool()
def get_topvisor_positions_summary(
    project_id: int, date1: Optional[str] = None, date2: Optional[str] = None
) -> str:
    """
    Get position summary for a project in Topvisor.

    Args:
        project_id: Project ID in Topvisor
        date1: Period start date in YYYY-MM-DD format (default 7 days ago)
        date2: Period end date in YYYY-MM-DD format (default today)

    Returns:
        JSON string with position summary
    """
    try:
        topvisor = TopvisorAPI()
        result = topvisor.get_positions_summary(project_id, date1, date2)

        if result and "result" in result:
            summary = result["result"]

            return json.dumps(
                {
                    "status": "success",
                    "project_id": project_id,
                    "period": f"{date1 or 'auto'} - {date2 or 'auto'}",
                    "summary": summary,
                },
                indent=2,
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Failed to get position summary",
                },
                indent=2,
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {"status": "error", "message": f"Error getting summary: {str(e)}"},
            indent=2,
            ensure_ascii=False,
        )


@mcp.tool()
def get_topvisor_competitors(project_id: int) -> str:
    """
    Get project competitors list in Topvisor.

    Args:
        project_id: Project ID in Topvisor

    Returns:
        JSON string with competitors list
    """
    try:
        topvisor = TopvisorAPI()
        result = topvisor.get_project_competitors(project_id)

        if result and "result" in result:
            competitors = result["result"]
            competitors_info = []

            for competitor in competitors:
                info = {
                    "id": competitor.get("id"),
                    "name": competitor.get("name"),
                    "url": competitor.get("url"),
                    "status": competitor.get("on"),
                    "enabled": competitor.get("enabled"),
                }
                competitors_info.append(info)

            return json.dumps(
                {
                    "status": "success",
                    "project_id": project_id,
                    "competitors": competitors_info,
                    "total_count": len(competitors_info),
                },
                indent=2,
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Failed to get competitor data",
                },
                indent=2,
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "message": f"Error getting competitors: {str(e)}",
            },
            indent=2,
            ensure_ascii=False,
        )


@mcp.tool()
def get_topvisor_regions(project_id: int) -> str:
    """
    Get project regions and search engines in Topvisor.

    Args:
        project_id: Project ID in Topvisor

    Returns:
        JSON string with regions and search engines
    """
    try:
        topvisor = TopvisorAPI()
        result = topvisor.get_project_regions(project_id)

        if result and "result" in result:
            regions = result["result"]
            regions_info = []

            for region in regions:
                info = {
                    "id": region.get("id"),
                    "searcher": region.get("searcher"),
                    "region_key": region.get("region_key"),
                    "region_name": region.get("region_name"),
                    "enabled": region.get("enabled"),
                    "device": region.get("device"),
                }
                regions_info.append(info)

            return json.dumps(
                {
                    "status": "success",
                    "project_id": project_id,
                    "regions": regions_info,
                    "total_count": len(regions_info),
                },
                indent=2,
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {"status": "error", "message": "Failed to get region data"},
                indent=2,
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {"status": "error", "message": f"Error getting regions: {str(e)}"},
            indent=2,
            ensure_ascii=False,
        )


@mcp.tool()
def get_topvisor_keyword_folders(project_id: int) -> str:
    """
    Get project keyword folders in Topvisor.

    Args:
        project_id: Project ID in Topvisor

    Returns:
        JSON string with keyword folders
    """
    try:
        topvisor = TopvisorAPI()
        result = topvisor.get_keyword_folders(project_id)

        if result and "result" in result:
            folders = result["result"]
            folders_info = []

            for folder in folders:
                info = {
                    "id": folder.get("id"),
                    "name": folder.get("name"),
                    "parent_id": folder.get("parent_id"),
                    "keywords_count": folder.get("count_keywords"),
                }
                folders_info.append(info)

            return json.dumps(
                {
                    "status": "success",
                    "project_id": project_id,
                    "folders": folders_info,
                    "total_count": len(folders_info),
                },
                indent=2,
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {"status": "error", "message": "Failed to get folder data"},
                indent=2,
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {"status": "error", "message": f"Error getting folders: {str(e)}"},
            indent=2,
            ensure_ascii=False,
        )


@mcp.tool()
def get_topvisor_keyword_groups(
    project_id: int, folder_id: Optional[int] = None
) -> str:
    """
    Get project keyword groups in Topvisor.

    Args:
        project_id: Project ID in Topvisor
        folder_id: Folder ID (optional)

    Returns:
        JSON string with keyword groups
    """
    try:
        topvisor = TopvisorAPI()
        result = topvisor.get_keyword_groups(project_id, folder_id)

        if result and "result" in result:
            groups = result["result"]
            groups_info = []

            for group in groups:
                info = {
                    "id": group.get("id"),
                    "name": group.get("name"),
                    "folder_id": group.get("folder_id"),
                    "keywords_count": group.get("count_keywords"),
                    "enabled": group.get("on"),
                }
                groups_info.append(info)

            return json.dumps(
                {
                    "status": "success",
                    "project_id": project_id,
                    "folder_id": folder_id,
                    "groups": groups_info,
                    "total_count": len(groups_info),
                },
                indent=2,
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {"status": "error", "message": "Failed to get group data"},
                indent=2,
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {"status": "error", "message": f"Error getting groups: {str(e)}"},
            indent=2,
            ensure_ascii=False,
        )


@mcp.tool()
def get_topvisor_balance() -> str:
    """
    Get account balance information in Topvisor.

    Returns:
        JSON string with balance information
    """
    try:
        topvisor = TopvisorAPI()
        result = topvisor.get_balance_info()

        if result and "result" in result:
            balance_info = result["result"]

            return json.dumps(
                {
                    "status": "success",
                    "balance": balance_info.get("balance"),
                    "currency": balance_info.get("currency", "RUB"),
                    "xml_limits": balance_info.get("xml_limits", {}),
                    "account_info": balance_info,
                },
                indent=2,
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {"status": "error", "message": "Failed to get balance data"},
                indent=2,
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {"status": "error", "message": f"Error getting balance: {str(e)}"},
            indent=2,
            ensure_ascii=False,
        )


@mcp.tool()
def get_topvisor_project_keywords(project_id: int) -> str:
    """
    Get project keywords for diagnostics.

    Args:
        project_id: Project ID in Topvisor

    Returns:
        JSON string with project keywords list
    """
    try:
        topvisor = TopvisorAPI()
        result = topvisor.get_project_keywords(project_id)

        return json.dumps(
            {"status": "success", "project_id": project_id, "keywords_data": result},
            ensure_ascii=False,
        )
    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "message": f"Error getting keywords: {str(e)}",
            },
            ensure_ascii=False,
        )


@mcp.tool()
def check_ahrefs_setup() -> str:
    """
    Check Ahrefs API setup and connection.

    Returns:
        JSON string with setup check results
    """
    try:
        # Check for API key presence
        api_key = os.getenv("AHREFS_API_KEY")

        if not api_key:
            return json.dumps(
                {
                    "status": "error",
                    "message": "API key not found",
                    "checks": {
                        "env_file": os.path.exists(".env"),
                        "api_key_set": False,
                        "api_connection": False,
                    },
                    "help": "Create .env file and add AHREFS_API_KEY=your_key",
                },
                indent=2,
                ensure_ascii=False,
            )

        # Check API connection
        try:
            ahrefs = AhrefsAPI()
            # Simple test request to get referring domains
            result = ahrefs.get_refdomains("example.com", limit=1)

            if result and "error" in result:
                return json.dumps(
                    {
                        "status": "warning",
                        "message": f'API key found, but there is a problem: {result["error"]}',
                        "checks": {
                            "env_file": True,
                            "api_key_set": True,
                            "api_connection": False,
                        },
                        "help": "Check API key validity and account balance",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            elif result and "refdomains" in result:
                return json.dumps(
                    {
                        "status": "success",
                        "message": "Everything is set up correctly! Ahrefs API is working",
                        "checks": {
                            "env_file": True,
                            "api_key_set": True,
                            "api_connection": True,
                        },
                        "test_result": "Test request successful",
                    },
                    indent=2,
                    ensure_ascii=False,
                )
            else:
                return json.dumps(
                    {
                        "status": "error",
                        "message": "Unexpected response from API",
                        "checks": {
                            "env_file": True,
                            "api_key_set": True,
                            "api_connection": False,
                        },
                        "raw_result": str(result)[:500] if result else "None",
                    },
                    indent=2,
                    ensure_ascii=False,
                )

        except Exception as api_error:
            return json.dumps(
                {
                    "status": "error",
                    "message": f"API connection error: {str(api_error)}",
                    "checks": {
                        "env_file": os.path.exists(".env"),
                        "api_key_set": bool(api_key),
                        "api_connection": False,
                    },
                    "error_type": type(api_error).__name__,
                    "help": "Check internet connection and API key validity",
                },
                indent=2,
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "message": f"Setup check error: {str(e)}",
                "help": "Make sure API key is added to .env file",
            },
            indent=2,
            ensure_ascii=False,
        )


@mcp.tool()
def get_ahrefs_refdomains(
    target: str, limit: int = 100, order_by: str = "domain_rating:desc"
) -> str:
    """
    Get list of referring domains for target domain via Ahrefs.

    Args:
        target: Target domain (e.g. "example.com")
        limit: Number of results (maximum 1000, default 100)
        order_by: Field for sorting with direction (default "domain_rating:desc")

    Returns:
        JSON string with list of referring domains
    """
    try:
        ahrefs = AhrefsAPI()
        result = ahrefs.get_refdomains(target=target, limit=limit, order_by=order_by)

        if result and "error" in result:
            return json.dumps(
                {
                    "status": "error",
                    "message": f"API error: {result['error']}",
                    "details": result.get("details", "Check API key and balance"),
                },
                indent=2,
                ensure_ascii=False,
            )

        if result and "refdomains" in result:
            refdomains = result["refdomains"]

            return json.dumps(
                {
                    "status": "success",
                    "target": target,
                    "refdomains": refdomains,
                    "total_count": len(refdomains),
                    "limit": limit,
                    "order_by": order_by,
                },
                indent=2,
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Failed to get referring domains data",
                    "raw_result": str(result)[:500] if result else "None",
                },
                indent=2,
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "message": f"Error getting referring domains: {str(e)}",
            },
            indent=2,
            ensure_ascii=False,
        )


@mcp.tool()
def get_ahrefs_backlinks(
    target: str, limit: int = 100, order_by: str = "domain_rating_source:desc"
) -> str:
    """
    Get list of backlinks for target domain via Ahrefs.

    Args:
        target: Target domain (e.g. "example.com")
        limit: Number of results (maximum 1000, default 100)
        order_by: Field for sorting with direction (default "domain_rating_source:desc")

    Returns:
        JSON string with list of backlinks
    """
    try:
        ahrefs = AhrefsAPI()
        result = ahrefs.get_backlinks(target=target, limit=limit, order_by=order_by)

        if result and "error" in result:
            return json.dumps(
                {
                    "status": "error",
                    "message": f"API error: {result['error']}",
                    "details": result.get("details", "Check API key and balance"),
                },
                indent=2,
                ensure_ascii=False,
            )

        if result and "backlinks" in result:
            backlinks = result["backlinks"]

            return json.dumps(
                {
                    "status": "success",
                    "target": target,
                    "backlinks": backlinks,
                    "total_count": len(backlinks),
                    "limit": limit,
                    "order_by": order_by,
                },
                indent=2,
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Failed to get backlinks data",
                    "raw_result": str(result)[:500] if result else "None",
                },
                indent=2,
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "message": f"Error getting backlinks: {str(e)}",
            },
            indent=2,
            ensure_ascii=False,
        )


@mcp.tool()
def get_ahrefs_organic_keywords(
    target: str,
    limit: int = 100,
    order_by: str = "best_position:asc",
    date: Optional[str] = None,
) -> str:
    """
    Get organic keywords for target domain via Ahrefs.

    Args:
        target: Target domain (e.g. "example.com")
        limit: Number of results (maximum 1000, default 100)
        order_by: Field for sorting with direction (default "best_position:asc")
        date: Date in YYYY-MM-DD format (default - current date)

    Returns:
        JSON string with list of organic keywords
    """
    try:
        ahrefs = AhrefsAPI()
        result = ahrefs.get_organic_keywords(
            target=target, limit=limit, order_by=order_by, date=date
        )

        if result and "error" in result:
            return json.dumps(
                {
                    "status": "error",
                    "message": f"API error: {result['error']}",
                    "details": result.get("details", "Check API key and balance"),
                },
                indent=2,
                ensure_ascii=False,
            )

        if result and "keywords" in result:
            keywords = result["keywords"]

            return json.dumps(
                {
                    "status": "success",
                    "target": target,
                    "keywords": keywords,
                    "total_count": len(keywords),
                    "limit": limit,
                    "order_by": order_by,
                    "date": date,
                },
                indent=2,
                ensure_ascii=False,
            )
        else:
            return json.dumps(
                {
                    "status": "error",
                    "message": "Failed to get organic keywords data",
                    "raw_result": str(result)[:500] if result else "None",
                },
                indent=2,
                ensure_ascii=False,
            )

    except Exception as e:
        return json.dumps(
            {
                "status": "error",
                "message": f"Error getting organic keywords: {str(e)}",
            },
            indent=2,
            ensure_ascii=False,
        )


@mcp.resource("papers://folders")
def get_available_folders() -> str:
    """
    List all available topic folders in the papers directory.

    This resource provides a simple list of all available topic folders.
    """
    folders = []

    # Get all topic directories
    if os.path.exists(PAPER_DIR):
        for topic_dir in os.listdir(PAPER_DIR):
            topic_path = os.path.join(PAPER_DIR, topic_dir)
            if os.path.isdir(topic_path):
                papers_file = os.path.join(topic_path, "papers_info.json")
                if os.path.exists(papers_file):
                    folders.append(topic_dir)

    # Create a simple markdown list
    content = "# Available Topics\n\n"
    if folders:
        for folder in folders:
            content += f"- {folder}\n"
        content += f"\nUse @{folder} to access papers in that topic.\n"
    else:
        content += "No topics found.\n"

    return content


@mcp.resource("papers://{topic}")
def get_topic_papers(topic: str) -> str:
    """
    Get detailed information about papers on a specific topic.

    Args:
        topic: The research topic to retrieve papers for
    """
    topic_dir = topic.lower().replace(" ", "_")
    papers_file = os.path.join(PAPER_DIR, topic_dir, "papers_info.json")

    if not os.path.exists(papers_file):
        return f"# No papers found for topic: {topic}\n\nTry searching for papers on this topic first."

    try:
        with open(papers_file, "r") as f:
            papers_data = json.load(f)

        # Create markdown content with paper details
        content = f"# Papers on {topic.replace('_', ' ').title()}\n\n"
        content += f"Total papers: {len(papers_data)}\n\n"

        for paper_id, paper_info in papers_data.items():
            content += f"## {paper_info['title']}\n"
            content += f"- **Paper ID**: {paper_id}\n"
            content += f"- **Authors**: {', '.join(paper_info['authors'])}\n"
            content += f"- **Published**: {paper_info['published']}\n"
            content += (
                f"- **PDF URL**: [{paper_info['pdf_url']}]({paper_info['pdf_url']})\n\n"
            )
            content += f"### Summary\n{paper_info['summary'][:500]}...\n\n"
            content += "---\n\n"

        return content
    except json.JSONDecodeError:
        return f"# Error reading papers data for {topic}\n\nThe papers data file is corrupted."


@mcp.prompt()
def generate_search_prompt(topic: str, num_papers: int = 5) -> str:
    """Generate a prompt for Claude to find and discuss academic papers on a specific topic."""
    return f"""Search for {num_papers} academic papers about '{topic}' using the search_papers tool. 

Follow these instructions:
1. First, search for papers using search_papers(topic='{topic}', max_results={num_papers})
2. For each paper found, extract and organize the following information:
   - Paper title
   - Authors
   - Publication date
   - Brief summary of the key findings
   - Main contributions or innovations
   - Methodologies used
   - Relevance to the topic '{topic}'

3. Provide a comprehensive summary that includes:
   - Overview of the current state of research in '{topic}'
   - Common themes and trends across the papers
   - Key research gaps or areas for future investigation
   - Most impactful or influential papers in this area

4. Organize your findings in a clear, structured format with headings and bullet points for easy readability.

Please present both detailed information about each paper and a high-level synthesis of the research landscape in {topic}."""


if __name__ == "__main__":
    # Initialize and run the server
    mcp.run(transport="http")


# topvisor = TopvisorAPI()
# result = topvisor.get_project_keywords(
#     project_id=23059018, folder_id=None, group_id=None
# )
# print(result)

# topvisor = TopvisorAPI()
# result = topvisor.get_project_positions(project_id=19294818, date1="2025-08-15", date2="2025-08-21")
# print(result)
