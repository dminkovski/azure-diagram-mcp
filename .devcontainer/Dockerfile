# Python 3.10 on Debian Bookworm with 'vscode' user preconfigured
FROM mcr.microsoft.com/devcontainers/python:3.10-bookworm


# Install GraphViz (needed by the diagrams package)
RUN apt-get update \
&& apt-get install -y --no-install-recommends graphviz \
&& rm -rf /var/lib/apt/lists/*


# (Optional) Pre-create a workspace folder
WORKDIR /workspaces/azure-diagram-mcp