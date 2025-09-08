import os
from fastmcp import FastMCP
from dotenv import load_dotenv

# Import Topvisor tools from the tools module
from tools.topvisor import (
    check_topvisor_setup,
    get_topvisor_projects,
    get_topvisor_keywords,
    get_topvisor_positions_history,
    get_topvisor_positions_summary,
    get_topvisor_competitors,
    get_topvisor_regions,
    get_topvisor_keyword_folders,
    get_topvisor_keyword_groups,
    get_topvisor_balance,
    get_topvisor_project_keywords,
)

# Import Ahrefs tools from the tools module
from tools.ahrefs import (
    check_ahrefs_setup,
    get_ahrefs_refdomains,
    get_ahrefs_backlinks,
    get_ahrefs_organic_keywords,
)

load_dotenv()

PAPER_DIR = "papers"

# Initialize FastMCP server
mcp = FastMCP("research")

# Register Topvisor tools
mcp.tool(check_topvisor_setup)
mcp.tool(get_topvisor_projects)
mcp.tool(get_topvisor_keywords)
mcp.tool(get_topvisor_positions_history)
mcp.tool(get_topvisor_positions_summary)
mcp.tool(get_topvisor_competitors)
mcp.tool(get_topvisor_regions)
mcp.tool(get_topvisor_keyword_folders)
mcp.tool(get_topvisor_keyword_groups)
mcp.tool(get_topvisor_balance)
mcp.tool(get_topvisor_project_keywords)

# Register Ahrefs tools
mcp.tool(check_ahrefs_setup)
mcp.tool(get_ahrefs_refdomains)
mcp.tool(get_ahrefs_backlinks)
mcp.tool(get_ahrefs_organic_keywords)

if __name__ == "__main__":
    # Initialize and run the server
    mode = os.getenv("MCP_SERVER_TRANSPORT", "stdio")
    if mode == "stdio":
        mcp.run(transport=mode)
    else:
        port = int(os.getenv("MCP_SERVER_PORT", "3000"))
        mcp.run(
            transport=mode,
            port=port
        )
