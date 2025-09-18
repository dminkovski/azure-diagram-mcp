# Copyright (c) Microsoft Corporation. All rights reserved.
"""azure-diagram-mcp-server implementation.

This server provides tools to generate diagrams using the Python diagrams package, focused on Microsoft Azure services and architecture only.
It accepts Python code as a string and generates PNG diagrams without displaying them.
"""

from azure_diagram_mcp_server.diagrams_tools import (
    generate_diagram,
    get_diagram_examples,
    list_diagram_icons,
)
from azure_diagram_mcp_server.models import DiagramType
from mcp.server.fastmcp import FastMCP
from pydantic import Field
from typing import Optional

# Create the MCP server
mcp = FastMCP(
    'azure-diagram-mcp-server',
    dependencies=[
        'pydantic',
        'diagrams',
    ],
    log_level='ERROR',
    instructions="""Use this server to generate professional diagrams using the Python diagrams package, focused on Microsoft Azure.

WORKFLOW:
1. list_icons:
   - Discover all available icons in the diagrams package for Azure
   - Browse Azure providers, services, and icons organized hierarchically
   - Find the exact import paths for Azure icons you want to use

2. get_diagram_examples:
   - Request example code for the diagram type you need (azure, sequence, flow, class, k8s, onprem, custom, or all)
   - Study the examples to understand the diagram package's syntax and Azure capabilities
   - Use these examples as templates for your own Azure diagrams
   - Each example demonstrates different Azure features and diagram structures

3. generate_diagram:
   - Write Python code using the diagrams package DSL based on the Azure examples
   - Submit your code to generate a PNG diagram
   - Optionally specify a filename
   - The diagram is generated with show=False to prevent automatic display
   - IMPORTANT: Always provide the workspace_dir parameter to save diagrams in the user's current directory
"""
)

@mcp.tool(name='generate_diagram')
async def mcp_generate_diagram(
    code: str = Field(..., description='Python code using the diagrams package DSL'),
    filename: Optional[str] = Field(None, description='Output filename (without extension)'),
    timeout: int = Field(90, description='Timeout in seconds for diagram generation'),
    workspace_dir: Optional[str] = Field(None, description='Workspace directory to save diagrams'),
):
    """Generate a diagram from Python code using the diagrams package (Azure only)."""
    return await generate_diagram(code, filename, timeout, workspace_dir)

@mcp.tool(name='get_diagram_examples')
async def mcp_get_diagram_examples(
    diagram_type: str = Field('all', description='Type of diagram example to return'),
):
    """Get example code for different types of diagrams (Azure only)."""
    return get_diagram_examples(DiagramType(diagram_type))

@mcp.tool(name='list_icons')
async def mcp_list_diagram_icons(
    provider_filter: Optional[str] = Field(None, description='Filter icons by provider name'),
    service_filter: Optional[str] = Field(None, description='Filter icons by service name'),
):
    """List available Azure icons from the diagrams package."""
    return list_diagram_icons(provider_filter, service_filter)

def main():
    """Main entry point for the MCP server."""
    print("Azure Diagram MCP server is running.")
    mcp.run()

if __name__ == "__main__":
    main()
