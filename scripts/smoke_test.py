"""Start the installed server over stdio and exercise the MCP handshake."""

import asyncio
import sys

from mcp import ClientSession, StdioServerParameters, stdio_client


async def smoke() -> None:
    server = StdioServerParameters(command=sys.executable, args=["-m", "data_engineering_mcp.server"])
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            initialized = await session.initialize()
            tools = await session.list_tools()
            listed = await session.call_tool("listar_tabelas", {})
            status = await session.call_tool("status_catalogo", {})
            print(f"server={initialized.server_info.name} version={initialized.server_info.version}")
            print(f"tools={len(tools.tools)} names={','.join(tool.name for tool in tools.tools)}")
            print(f"listar_tabelas_error={listed.is_error} content={listed.content}")
            print(f"status_catalogo_error={status.is_error} content={status.content}")


if __name__ == "__main__":
    asyncio.run(smoke())
