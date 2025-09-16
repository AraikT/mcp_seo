# MCP SEO - Professional SEO Analysis & Research Toolset

A comprehensive SEO analysis platform built with the **Model Context Protocol (MCP)** that provides professional SEO tools and research capabilities. This project focuses on SEO position tracking, backlink analysis, and competitive research, demonstrating how MCP can integrate multiple SEO APIs and data sources into a single conversational interface.

## 🎯 Project Overview

This project provides:
- **SEO Position Tracking**: Monitor keyword rankings and track search performance via Topvisor API
- **Backlink Analysis**: Analyze domain authority, referring domains, and backlink profiles via Ahrefs API
- **Competitive Research**: Track competitor rankings and analyze their SEO strategies
- **Unified Chat Interface**: Interact with all SEO tools through a single conversational bot
- **MCP Architecture**: Demonstrates modern AI tool integration patterns for SEO workflows

## 🏗️ Architecture

The project uses the **Model Context Protocol (MCP)** to create a modular architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP ChatBot   │◄──►│  SEO Server      │◄──►│   SEO APIs      │
│  (mcp_chatbot)  │    │   (FastMCP)      │    │ • Topvisor      │
│                 │    │                  │    │ • Ahrefs        │
│  • Claude API   │    │ • Position Track │    │                 │
│  • Tool Router  │    │ • Backlink Analy │    └─────────────────┘
│  • Chat Loop    │    │ • SEO Research   │
│                 │    └──────────────────┘
│                 │    ┌─────────────────────────────────────────┐
│                 │◄──►│ MCP Servers:                            │
│                 │    │ mcp-server-fetch                        |
│                 │    │ workspace-mcp                           │
│                 │    | @modelcontextprotocol/server-filesystem │ 
│                 │    └─────────────────────────────────────────┘
│                 │  
└─────────────────┘    
```

## 🚀 Features

### 📊 SEO Position Tracking (Topvisor)
- Project management and monitoring
- Keyword position tracking
- Competitor analysis
- Regional search engine data
- Balance and account information

### 🔗 Backlink Analysis (Ahrefs)
- Referring domains analysis
- Backlink discovery and analysis
- Organic keyword research
- Domain authority metrics
- Traffic and ranking data

### 💬 Interactive Chat Interface
- Natural language queries
- Command-based operations
- Real-time API interactions
- Structured data display

### Google Docs
- Extract document text
- Create new documents
- Modify document text
- Find documents by name
- Find and replace text
- List docs in folder
- Add tables, lists, page breaks
- Insert images from Drive/URLs
- Modify headers and footers
- Execute multiple operations
- Analyze document structure
- Create data tables
- Debug table issues
- Read, Reply, Create, Resolve Comments

### Google Sheets
- Read cell value
- Write/update/clear cells
- Create new spreadsheet
- List accessible spreadsheets
- Get spreadsheet metadata
- Add sheets to existing files
- Read, Reply, Create, Resolve Comments

## 📁 Project Structure

```
mcp_seo/
├── mcp_chatbot.py          # Main chatbot interface
├── seo.py      # FastMCP server with SEO tools
├── server_config.json     # MCP server configuration
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration
├── uv.lock               # Dependency lock file
├── logic/                # Core business logic
│   ├── ahrefs.py         # Ahrefs API wrapper
│   └── topvisor.py       # Topvisor API wrapper
├── tools/                # MCP tool implementations
    ├── ahrefs.py         # Ahrefs MCP tools
    └── topvisor.py       # Topvisor MCP tools

```

## 🛠️ Installation

### Prerequisites
- Python 3.13+
- UV package manager (recommended) or pip
- API keys for Topvisor and Ahrefs (optional)

### Setup Steps

1. **Clone and navigate to the project:**
   ```bash
   cd "mcp_seo"
   ```

2. **Install dependencies:**
   ```bash
   # Using UV (recommended)
   uv sync

   # Or using pip
   pip install -r requirements.txt
   ```

3. **Set up environment variables:**
   Create a `.env` file with your API keys and MCP server configuration:
   ```env
   ANTHROPIC_API_KEY=your_anthropic_key_here
   TOPVISOR_API_KEY=your_topvisor_key_here  # Optional
   TOPVISOR_USER_ID=your_user_id_here       # Optional
   AHREFS_API_KEY=your_ahrefs_key_here      # Optional

   # MCP server mode: stdio, sse, streamable-http
   # Default: stdio
   MCP_SERVER_TRANSPORT=stdio
   # MCP server port (only for sse and streamable-http modes)
   MCP_SERVER_PORT=3000
  ```

4. Google tools configuration

   Google MCP server is based on [taylorwilsdon/google_workspace_mcp](https://github.com/taylorwilsdon/google_workspace_mcp).

   It requires creation of Google project, configuration of access and adding API keys.

   First of all we need to create [Google project](https://console.cloud.google.com/):
   * Open console.cloud.google.com
   * Create new project
   * Note project name

   Then we need to enable [Docs and Sheets APIs](https://console.cloud.google.com/apis/library):
   * Open APIs library
   * Enable Google Sheets API
   * Enable Google Docs API

   Then we need to create [credentials](https://console.cloud.google.com/apis/credentials):
   * Select OAuth client ID
   * Select Application type > Desktop app
   * Name you client
   * Copy Client ID. Set it to `GOOGLE_OAUTH_CLIENT_ID` env variable in the `.env` file
   * Copy Client Secret. Set it to `GOOGLE_OAUTH_CLIENT_SECRET` env variable in the `.env` file

   Set additional env variables:
   ```

   # The default user
   USER_GOOGLE_EMAIL=<your gmail address here> 
   # Allows HTTP redirect URIs (You should not see warning in the browser)
   OAUTHLIB_INSECURE_TRANSPORT=1
   ```

   The first time it may ask you what Google account email you want to use to create the create Document/Spreadsheet.

   The authentication work using OAuth protocol. The first time LLM or Agent will call auth tool. and provide you the link. If you use advanced MCP client(Cursor/Claude Desktop) then you should be able to click on link. It will ask you to allow user to use the application that you have created before. If you use console chat - you will need to copy the URL, open it in browser and confirm login with your Google account.

   Next time you should be already authenticated and no need to repeat the process.

5. **Run the SEO server:**
   ```bash
   # Using UV
   uv run seo_server.py

   # Or using Python
   python seo_server.py
   ```

6. **Run the chatbot (in a new terminal):**
   ```bash
   # Using UV
   uv run mcp_chatbot.py

   # Or using Python
   python mcp_chatbot.py
   ```

7. **Debug and development**
   Set environment variables:
   ```
   MCP_SERVER_TRANSPORT=streamable-http
   MCP_SERVER_PORT=3000
   ```

   Start MCP server by running `python seo.py`.

   Run:
   ```
   npx @modelcontextprotocol/inspector
   ```
   It should open MCP Inspector in browser.
   Connect to transport type `Streamable HTTP` and url `http://127.0.0.1:8000/mcp`

   Navigate to tools and run required tool

## 🎮 Usage Guide

### Basic Commands

#### Topvisor SEO Commands
```bash
/topvisor                  # Show all Topvisor commands
/setup                     # Check API setup
/projects                  # Get all projects
/keywords 12345            # Get project keywords
/positions 12345           # Get keyword positions
/competitors 12345         # Get competitors
/balance                   # Check account balance
```

#### Ahrefs Commands
```bash
/ahrefs                    # Show all Ahrefs commands
/ahrefs_setup             # Check API setup
/refdomains example.com    # Get referring domains
/backlinks example.com     # Get backlinks
/organic example.com       # Get organic keywords
```

### Natural Language Queries

You can also use natural language:
```bash
"Show me the keyword positions for project 12345"
"What are the referring domains for example.com?"
"Check my Topvisor account balance"
"Analyze backlinks for competitor sites"
```

## 🔧 API Configuration

### Topvisor Setup
1. Register at [Topvisor](https://topvisor.com)
2. Get API key from your account settings
3. Add to `.env` file
4. Test with `/setup` command

### Ahrefs Setup
1. Get API access from [Ahrefs](https://ahrefs.com/api)
2. Obtain API key
3. Add to `.env` file
4. Test with `/ahrefs_setup` command

### Anthropic Setup
1. Get API key from [Anthropic](https://console.anthropic.com)
2. Add to `.env` file for Claude AI functionality

## 🔍 Example Workflows

### SEO Analysis Workflow
```bash
# 1. Check setup
/setup

# 2. Get projects
/projects

# 3. Analyze keywords
/keywords 12345

# 4. Check positions
/positions 12345 2024-01-01 2024-01-31

# 5. Analyze competitors
/competitors 12345
```

### Backlink Analysis Workflow
```bash
# 1. Check setup
/ahrefs_setup

# 2. Get referring domains
/refdomains example.com 100 domain_rating:desc

# 3. Analyze backlinks
/backlinks example.com 200

# 4. Research organic keywords
/organic example.com 150 volume:desc
```

## 🧠 Project Benefits

This project demonstrates:

1. **MCP Integration**: How to build modular AI systems for SEO
2. **SEO API Orchestration**: Managing multiple SEO service APIs
3. **Conversational SEO Tools**: Natural language interaction with SEO platforms
4. **SEO Data Management**: Organizing and analyzing SEO metrics and research
5. **Professional SEO Workflow**: Real-world SEO analysis and competitive research

## 🤝 Contributing

This is a professional SEO toolset. Feel free to:
- Fork and experiment with SEO workflows
- Add new SEO API integrations
- Improve the chat interface
- Extend the SEO analysis capabilities
- Add new competitive research features

## 📄 License

This project is for educational purposes. Check individual API terms for commercial usage.

## 🆘 Troubleshooting

### Common Issues

1. **"API key not found"**
   - Check your `.env` file
   - Ensure proper environment variable names

2. **"Connection error"**
   - Check internet connection
   - Verify API endpoints are accessible

3. **"Tool not found"**
   - Ensure seo server is running
   - Check MCP server configuration

4. **Import errors**
   - Install all dependencies: `uv sync` or `pip install -r requirements.txt`
   - Check Python version (3.13+ required)

### Getting Help

- Check `/setup` and `/ahrefs_setup` for API configuration
- Use `/topvisor` and `/ahrefs` for command help
- Review console output for detailed error messages

---

**Built with**: Python, MCP, FastMCP, Anthropic Claude, Topvisor API, Ahrefs API

*This project showcases the power of MCP for building integrated AI SEO analysis and competitive research tools.*
