FROM python:3.11-slim

WORKDIR /app

COPY pyproject.toml /app/
COPY shared /app/shared
COPY mcp_server /app/mcp_server

RUN pip install --no-cache-dir .

ENV MCP_TRANSPORT=http \
    MCP_HOST=0.0.0.0 \
    MCP_PORT=8080

EXPOSE 8080

CMD ["python", "-m", "mcp_server.http_entry"]
