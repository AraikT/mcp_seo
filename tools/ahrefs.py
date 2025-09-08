import json
import os
from typing import Optional
from logic.ahrefs import AhrefsAPI
from dotenv import load_dotenv

load_dotenv()

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


def get_ahrefs_refdomains(
    target: str, limit: int = 100
) -> str:
    """
    Get list of referring domains for target domain via Ahrefs.

    Args:
        target: Target domain (e.g. "example.com")
        limit: Number of results (maximum 1000, default 100)

    Returns:
        JSON string with list of referring domains
    """
    try:
        order_by = "domain_rating:desc"
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


def get_ahrefs_backlinks(
    target: str, limit: int = 100
) -> str:
    """
    Get list of backlinks for target domain via Ahrefs.

    Args:
        target: Target domain (e.g. "example.com")
        limit: Number of results (maximum 1000, default 100)

    Returns:
        JSON string with list of backlinks
    """
    try:
        order_by = "domain_rating_source:desc"
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


def get_ahrefs_organic_keywords(
    target: str,
    limit: int = 100,
    date: Optional[str] = None,
) -> str:
    """
    Get organic keywords for target domain via Ahrefs.

    Args:
        target: Target domain (e.g. "example.com")
        limit: Number of results (maximum 1000, default 100)
        date: Date in YYYY-MM-DD format (default - current date)

    Returns:
        JSON string with list of organic keywords
    """
    try:
        ahrefs = AhrefsAPI()
        order_by = "best_position:asc"
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
