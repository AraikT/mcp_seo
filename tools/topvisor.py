import json
import os
from typing import Optional
from logic.topvisor import TopvisorAPI
from dotenv import load_dotenv

load_dotenv()

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

            return json.dumps(
                {
                    "status": "success",
                    "project_id": project_id,
                    "regions": regions,
                    "total_count": len(regions),
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

