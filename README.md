# MCP SEO - Professional SEO Analysis & Research Toolset

A comprehensive SEO analysis platform built with the **Model Context Protocol (MCP)** that provides professional SEO tools and research capabilities. This project focuses on SEO position tracking, backlink analysis, and competitive research, demonstrating how MCP can integrate multiple SEO APIs and data sources into a single conversational interface.

## 🎯 Project Overview

This project provides:
- **SEO Position Tracking**: Monitor keyword rankings and track search performance via Topvisor API
- **Backlink Analysis**: Analyze domain authority, referring domains, and backlink profiles via Ahrefs API
- **Competitive Research**: Track competitor rankings and analyze their SEO strategies
- **Academic Research**: Access SEO-related research papers and studies from arXiv
- **Unified Chat Interface**: Interact with all SEO tools through a single conversational bot
- **MCP Architecture**: Demonstrates modern AI tool integration patterns for SEO workflows

## 🏗️ Architecture

The project uses the **Model Context Protocol (MCP)** to create a modular architecture:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   MCP ChatBot   │◄──►│  SEO Server      │◄──►│   SEO APIs      │
│  (mcp_chatbot)  │    │   (FastMCP)      │    │ • Topvisor     │
│                 │    │                  │    │ • Ahrefs       │
│  • Claude API   │    │ • Position Track │    │ • arXiv        │
│  • Tool Router  │    │ • Backlink Analy │    └─────────────────┘
│  • Chat Loop    │    │ • SEO Research   │
└─────────────────┘    └──────────────────┘
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

### 📚 Research Support (Optional)
- Search SEO-related papers from arXiv
- Organize research by SEO topics
- Extract detailed paper information
- Generate research summaries
- Access papers via `@topic` syntax

## 📁 Project Structure

```
mcp_seo/
├── mcp_chatbot.py          # Main chatbot interface
├── research_server.py      # FastMCP server with SEO tools
├── server_config.json     # MCP server configuration
├── requirements.txt       # Python dependencies
├── pyproject.toml         # Project configuration
├── uv.lock               # Dependency lock file
├── logic/                # Core business logic
│   ├── ahrefs.py         # Ahrefs API wrapper
│   └── topvisor.py       # Topvisor API wrapper
├── tools/                # MCP tool implementations
│   ├── ahrefs.py         # Ahrefs MCP tools
│   └── topvisor.py       # Topvisor MCP tools
└── papers/               # SEO research paper storage (optional)
    └── {topic}/
        └── papers_info.json
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

4. **Run the research server:**
   ```bash
   # Using UV
   uv run research_server.py

   # Or using Python
   python research_server.py
   ```

5. **Run the chatbot (in a new terminal):**
   ```bash
   # Using UV
   uv run mcp_chatbot.py

   # Or using Python
   python mcp_chatbot.py
   ```

6. **Debug and development**
   Set environment variables:
   ```
   MCP_SERVER_TRANSPORT=streamable-http
   MCP_SERVER_PORT=3000
   ```

   Start MCP server by running `python research_server.py`.

   Run:
   ```
   npx @modelcontextprotocol/inspector
   ```
   It should open MCP Inspector in browser.
   Connect to transport type `Streamable HTTP` and url `http://127.0.0.1:8000/mcp`

   Navigate to tools and run required tool

## 🎮 Usage Guide

### Basic Commands

#### SEO Research Commands
```bash
# Search for SEO papers
search_papers("search engine optimization", max_results=5)

# Browse SEO topics
@folders                    # List available topics
@seo_strategies            # View SEO papers in topic

# Prompts
/prompts                   # List available prompts
/prompt generate_search_prompt topic="SEO" num_papers=10
```

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
"Find SEO research papers about link building"
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

### SEO Research Workflow
```bash
# 1. Search for SEO papers
search_papers("keyword optimization strategies", max_results=8)

# 2. Browse results
@keyword_optimization_strategies

# 3. Get specific paper details
extract_info("2301.12345")

# 4. Generate comprehensive analysis
/prompt generate_search_prompt topic="SEO optimization" num_papers=10
```

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
   - Ensure research server is running
   - Check MCP server configuration

4. **Import errors**
   - Install all dependencies: `uv sync` or `pip install -r requirements.txt`
   - Check Python version (3.13+ required)

### Getting Help

- Check `/setup` and `/ahrefs_setup` for API configuration
- Use `/topvisor` and `/ahrefs` for command help
- Review console output for detailed error messages

---

**Built with**: Python, MCP, FastMCP, Anthropic Claude, arXiv API, Topvisor API, Ahrefs API

*This project showcases the power of MCP for building integrated AI SEO analysis and competitive research tools.*
