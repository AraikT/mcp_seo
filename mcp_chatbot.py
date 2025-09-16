from dotenv import load_dotenv
from anthropic import Anthropic
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack
import json
import asyncio
import nest_asyncio

nest_asyncio.apply()

load_dotenv()


class MCP_ChatBot:
    def __init__(self):
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()
        # Tools list required for Anthropic API
        self.available_tools = []
        # Prompts list for quick display
        self.available_prompts = []
        # Sessions dict maps tool/prompt names or resource URIs to MCP client sessions
        self.sessions = {}

    async def connect_to_server(self, server_name, server_config):
        try:
            server_params = StdioServerParameters(**server_config)
            stdio_transport = await self.exit_stack.enter_async_context(
                stdio_client(server_params)
            )
            read, write = stdio_transport
            session = await self.exit_stack.enter_async_context(
                ClientSession(read, write)
            )
            await session.initialize()

            try:
                # List available tools
                response = await session.list_tools()
                for tool in response.tools:
                    self.sessions[tool.name] = session
                    self.available_tools.append(
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "input_schema": tool.inputSchema,
                        }
                    )

                # List available prompts
                prompts_response = await session.list_prompts()
                if prompts_response and prompts_response.prompts:
                    for prompt in prompts_response.prompts:
                        self.sessions[prompt.name] = session
                        self.available_prompts.append(
                            {
                                "name": prompt.name,
                                "description": prompt.description,
                                "arguments": prompt.arguments,
                            }
                        )
                # List available resources
                resources_response = await session.list_resources()
                if resources_response and resources_response.resources:
                    for resource in resources_response.resources:
                        resource_uri = str(resource.uri)
                        self.sessions[resource_uri] = session

            except Exception as e:
                print(f"Error {e}")

        except Exception as e:
            print(f"Error connecting to {server_name}: {e}")

    async def connect_to_servers(self):
        try:
            with open("server_config.json", "r") as file:
                data = json.load(file)
            servers = data.get("mcpServers", {})
            for server_name, server_config in servers.items():
                await self.connect_to_server(server_name, server_config)
        except Exception as e:
            print(f"Error loading server config: {e}")
            raise

    async def process_query(self, query):
        messages = [{"role": "user", "content": query}]

        while True:
            response = self.anthropic.messages.create(
                max_tokens=2024,
                model="claude-3-7-sonnet-20250219",
                tools=self.available_tools,
                messages=messages,
            )

            assistant_content = []
            has_tool_use = False

            for content in response.content:
                if content.type == "text":
                    print(content.text)
                    assistant_content.append(content)
                elif content.type == "tool_use":
                    has_tool_use = True
                    assistant_content.append(content)
                    messages.append({"role": "assistant", "content": assistant_content})

                    # Get session and call tool
                    session = self.sessions.get(content.name)
                    if not session:
                        print(f"Tool '{content.name}' not found.")
                        break

                    result = await session.call_tool(
                        content.name, arguments=content.input
                    )
                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": content.id,
                                    "content": result.content,
                                }
                            ],
                        }
                    )

            # Exit loop if no tool was used
            if not has_tool_use:
                break

    async def get_resource(self, resource_uri):
        session = self.sessions.get(resource_uri)

        # Fallback for papers URIs - try any papers resource session
        if not session and resource_uri.startswith("papers://"):
            for uri, sess in self.sessions.items():
                if uri.startswith("papers://"):
                    session = sess
                    break

        if not session:
            print(f"Resource '{resource_uri}' not found.")
            return

        try:
            result = await session.read_resource(uri=resource_uri)
            if result and result.contents:
                print(f"\nResource: {resource_uri}")
                print("Content:")
                print(result.contents[0].text)
            else:
                print("No content available.")
        except Exception as e:
            print(f"Error: {e}")

    async def list_prompts(self):
        """List all available prompts."""
        if not self.available_prompts:
            print("No prompts available.")
            return

        print("\nAvailable prompts:")
        for prompt in self.available_prompts:
            print(f"- {prompt['name']}: {prompt['description']}")
            if prompt["arguments"]:
                print(f"  Arguments:")
                for arg in prompt["arguments"]:
                    arg_name = arg.name if hasattr(arg, "name") else arg.get("name", "")
                    print(f"    - {arg_name}")

    async def execute_prompt(self, prompt_name, args):
        """Execute a prompt with the given arguments."""
        session = self.sessions.get(prompt_name)
        if not session:
            print(f"Prompt '{prompt_name}' not found.")
            return

        try:
            result = await session.get_prompt(prompt_name, arguments=args)
            if result and result.messages:
                prompt_content = result.messages[0].content

                # Extract text from content (handles different formats)
                if isinstance(prompt_content, str):
                    text = prompt_content
                elif hasattr(prompt_content, "text"):
                    text = prompt_content.text
                else:
                    # Handle list of content items
                    text = " ".join(
                        item.text if hasattr(item, "text") else str(item)
                        for item in prompt_content
                    )

                print(f"\nExecuting prompt '{prompt_name}'...")
                await self.process_query(text)
        except Exception as e:
            print(f"Error: {e}")

    async def show_topvisor_help(self):
        """Show available Topvisor commands."""
        help_text = """
🔍 Topvisor Commands:
/setup                                 - Check Topvisor API setup
/projects                               - Get all projects
/keywords <project_id> [folder_id] [group_id] - Get project keywords
/positions <project_id> [date_from] [date_to] - Get project positions
/competitors <project_id>               - Get project competitors
/balance                               - Get account balance

📊 Usage examples:
/setup                                - Check API setup
/projects                              - Show all projects
/keywords 12345                        - All keywords for project 12345
/keywords 12345 678                    - Keywords from folder 678
/positions 12345                       - Positions for last 7 days
/positions 12345 2024-01-01 2024-01-31 - Positions for January 2024
/competitors 12345                     - Competitors for project 12345

💡 You can also ask regular questions:
"Show my projects in Topvisor"
"What are the positions for project 12345?"
"How much money is in the balance?"
        """
        print(help_text)

    async def show_ahrefs_help(self):
        """Show available Ahrefs commands."""
        help_text = """
🔗 Ahrefs Commands:
/ahrefs_setup                          - Check Ahrefs API setup
/refdomains <domain> [limit] [order_by] - Get referring domains
/backlinks <domain> [limit] [order_by]  - Get backlinks
/organic <domain> [limit] [order_by] [date] - Get organic keywords

📊 Usage examples:
/ahrefs_setup                          - Check API setup
/refdomains example.com                - Referring domains (100 results)
/refdomains example.com 50             - Referring domains (50 results)
/backlinks example.com                 - Backlinks (100 results)
/backlinks example.com 200 url_rating_source:desc - Backlinks with sorting
/organic example.com                   - Organic keywords
/organic example.com 150 volume:desc   - 150 keywords by volume descending
/organic example.com 100 best_position:asc 2024-01-15 - Keywords for specific date

⚙️ Sorting parameters:
For refdomains: domain_rating:desc, first_seen:asc, last_seen:desc
For backlinks: domain_rating_source:desc, url_rating_source:desc
For organic: best_position:asc, volume:desc, keyword_difficulty:asc

💡 You can also ask regular questions:
"Show referring domains for example.com"
"What are the backlinks for example.com?"
"Find organic keywords for example.com"
        """
        print(help_text)

    async def get_topvisor_projects(self):
        """Quick command to get Topvisor projects."""
        await self.call_topvisor_tool("get_topvisor_projects", {})

    async def get_topvisor_keywords(self, project_id, folder_id=None, group_id=None):
        """Quick command to get keywords."""
        args = {"project_id": project_id}
        if folder_id:
            args["folder_id"] = folder_id
        if group_id:
            args["group_id"] = group_id
        await self.call_topvisor_tool("get_topvisor_keywords", args)

    async def get_topvisor_positions(self, project_id, date_from=None, date_to=None):
        """Quick command to get positions."""
        args = {"project_id": project_id}
        if date_from:
            args["date1"] = date_from
        if date_to:
            args["date2"] = date_to
        await self.call_topvisor_tool("get_topvisor_positions_history", args)

    async def get_topvisor_competitors(self, project_id):
        """Quick command to get competitors."""
        await self.call_topvisor_tool(
            "get_topvisor_competitors", {"project_id": project_id}
        )

    async def get_topvisor_balance(self):
        """Quick command to get balance."""
        await self.call_topvisor_tool("get_topvisor_balance", {})

    async def call_topvisor_tool(self, tool_name, args):
        """Helper method to call Topvisor tools."""
        session = self.sessions.get(tool_name)
        if not session:
            print(
                f"Topvisor tool '{tool_name}' not found. Make sure seo server is running."
            )
            return

        try:
            result = await session.call_tool(tool_name, arguments=args)
            if result and result.content:
                # Try to parse and pretty print JSON
                try:
                    data = json.loads(result.content[0].text)
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                except (json.JSONDecodeError, KeyError, IndexError):
                    print(result.content[0].text if result.content else "No content")
            else:
                print("No result returned")
        except Exception as e:
            print(f"Error calling {tool_name}: {e}")

    async def get_ahrefs_refdomains(
        self, target, limit=100, order_by="domain_rating:desc"
    ):
        """Quick command to get Ahrefs referring domains."""
        args = {"target": target, "limit": limit, "order_by": order_by}
        await self.call_ahrefs_tool("get_ahrefs_refdomains", args)

    async def get_ahrefs_backlinks(
        self, target, limit=100, order_by="domain_rating_source:desc"
    ):
        """Quick command to get Ahrefs backlinks."""
        args = {"target": target, "limit": limit, "order_by": order_by}
        await self.call_ahrefs_tool("get_ahrefs_backlinks", args)

    async def get_ahrefs_organic_keywords(
        self, target, limit=100, order_by="best_position:asc", date=None
    ):
        """Quick command to get Ahrefs organic keywords."""
        args = {"target": target, "limit": limit, "order_by": order_by}
        if date:
            args["date"] = date
        await self.call_ahrefs_tool("get_ahrefs_organic_keywords", args)

    async def call_ahrefs_tool(self, tool_name, args):
        """Helper method to call Ahrefs tools."""
        session = self.sessions.get(tool_name)
        if not session:
            print(
                f"Ahrefs tool '{tool_name}' not found. Make sure seo server is running."
            )
            return

        try:
            result = await session.call_tool(tool_name, arguments=args)
            if result and result.content:
                # Try to parse and pretty print JSON
                try:
                    data = json.loads(result.content[0].text)
                    print(json.dumps(data, indent=2, ensure_ascii=False))
                except (json.JSONDecodeError, KeyError, IndexError):
                    print(result.content[0].text if result.content else "No content")
            else:
                print("No result returned")
        except Exception as e:
            print(f"Error calling {tool_name}: {e}")

    async def chat_loop(self):
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")
        print("Use @folders to see available topics")
        print("Use @<topic> to search papers in that topic")
        print("Use /prompts to list available prompts")
        print("Use /prompt <name> <arg1=value1> to execute a prompt")
        print("Use /topvisor to see Topvisor commands")
        print("Use /ahrefs to see Ahrefs commands")
        print("Use /setup to check Topvisor API configuration")
        print("Use /ahrefs_setup to check Ahrefs API configuration")
        print("Use /projects to get your Topvisor projects")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if not query:
                    continue

                if query.lower() == "quit":
                    break

                # Check for @resource syntax first
                if query.startswith("@"):
                    # Remove @ sign
                    topic = query[1:]
                    if topic == "folders":
                        resource_uri = "papers://folders"
                    else:
                        resource_uri = f"papers://{topic}"
                    await self.get_resource(resource_uri)
                    continue

                # Check for /command syntax
                if query.startswith("/"):
                    parts = query.split()
                    command = parts[0].lower()

                    if command == "/prompts":
                        await self.list_prompts()
                    elif command == "/topvisor":
                        await self.show_topvisor_help()
                    elif command == "/ahrefs":
                        await self.show_ahrefs_help()
                    elif command == "/setup":
                        await self.call_topvisor_tool("check_topvisor_setup", {})
                    elif command == "/ahrefs_setup":
                        await self.call_ahrefs_tool("check_ahrefs_setup", {})
                    elif command == "/projects":
                        await self.get_topvisor_projects()
                    elif command == "/keywords":
                        if len(parts) < 2:
                            print(
                                "Usage: /keywords <project_id> [folder_id] [group_id]"
                            )
                            continue
                        try:
                            project_id = int(parts[1])
                            folder_id = (
                                int(parts[2])
                                if len(parts) > 2 and parts[2].isdigit()
                                else None
                            )
                            group_id = (
                                int(parts[3])
                                if len(parts) > 3 and parts[3].isdigit()
                                else None
                            )
                            await self.get_topvisor_keywords(
                                project_id, folder_id, group_id
                            )
                        except ValueError:
                            print("Error: project_id must be a number")
                    elif command == "/positions":
                        if len(parts) < 2:
                            print(
                                "Usage: /positions <project_id> [date_from] [date_to]"
                            )
                            continue
                        try:
                            project_id = int(parts[1])
                            date_from = parts[2] if len(parts) > 2 else None
                            date_to = parts[3] if len(parts) > 3 else None
                            await self.get_topvisor_positions(
                                project_id, date_from, date_to
                            )
                        except ValueError:
                            print("Error: project_id must be a number")
                    elif command == "/competitors":
                        if len(parts) < 2:
                            print("Usage: /competitors <project_id>")
                            continue
                        try:
                            project_id = int(parts[1])
                            await self.get_topvisor_competitors(project_id)
                        except ValueError:
                            print("Error: project_id must be a number")
                    elif command == "/balance":
                        await self.get_topvisor_balance()
                    elif command == "/refdomains":
                        if len(parts) < 2:
                            print("Usage: /refdomains <domain> [limit] [order_by]")
                            continue
                        domain = parts[1]
                        limit = (
                            int(parts[2])
                            if len(parts) > 2 and parts[2].isdigit()
                            else 100
                        )
                        order_by = parts[3] if len(parts) > 3 else "domain_rating:desc"
                        await self.get_ahrefs_refdomains(domain, limit, order_by)
                    elif command == "/backlinks":
                        if len(parts) < 2:
                            print("Usage: /backlinks <domain> [limit] [order_by]")
                            continue
                        domain = parts[1]
                        limit = (
                            int(parts[2])
                            if len(parts) > 2 and parts[2].isdigit()
                            else 100
                        )
                        order_by = (
                            parts[3] if len(parts) > 3 else "domain_rating_source:desc"
                        )
                        await self.get_ahrefs_backlinks(domain, limit, order_by)
                    elif command == "/organic":
                        if len(parts) < 2:
                            print("Usage: /organic <domain> [limit] [order_by] [date]")
                            continue
                        domain = parts[1]
                        limit = (
                            int(parts[2])
                            if len(parts) > 2 and parts[2].isdigit()
                            else 100
                        )
                        order_by = parts[3] if len(parts) > 3 else "best_position:asc"
                        date = parts[4] if len(parts) > 4 else None
                        await self.get_ahrefs_organic_keywords(
                            domain, limit, order_by, date
                        )
                    elif command == "/prompt":
                        if len(parts) < 2:
                            print("Usage: /prompt <name> <arg1=value1> <arg2=value2>")
                            continue

                        prompt_name = parts[1]
                        args = {}

                        # Parse arguments
                        for arg in parts[2:]:
                            if "=" in arg:
                                key, value = arg.split("=", 1)
                                args[key] = value

                        await self.execute_prompt(prompt_name, args)
                    else:
                        print(f"Unknown command: {command}")
                    continue

                await self.process_query(query)

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def cleanup(self):
        await self.exit_stack.aclose()


async def main():
    chatbot = MCP_ChatBot()
    try:
        await chatbot.connect_to_servers()
        await chatbot.chat_loop()
    finally:
        await chatbot.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
