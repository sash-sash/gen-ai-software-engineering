# How to Run — MCP Servers Setup

## Prerequisites

- Node.js 18+ (for GitHub, Filesystem, Notion MCP servers via `npx`)
- Python 3.11+ (for custom MCP server)
- Cursor IDE with MCP support

---

## Task 4 — Custom Lorem Ipsum MCP Server

### 1. Install dependencies

```powershell
cd homework-5/custom-mcp-server
py -m pip install -r requirements.txt
```

### 2. Test the server directly

```powershell
py server.py
```

Expected output:
```
Starting Custom Lorem Ipsum MCP Server...
```

### 3. Connect to Cursor

Open Cursor Settings → MCP → Add server, or edit `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "custom-lorem-ipsum": {
      "command": "py",
      "args": ["<ABSOLUTE_PATH>/homework-5/custom-mcp-server/server.py"]
    }
  }
}
```

### 4. Use the `read` tool

In Cursor chat, ask Claude:

```
Use the read tool to get 50 words of lorem ipsum.
```

Or with the default (30 words):

```
Call the read tool.
```

---

## Task 1 — GitHub MCP

### 1. Get a GitHub Personal Access Token

Go to https://github.com/settings/tokens → Generate new token (classic) with `repo` and `read:user` scopes.

### 2. Add to mcp.json

```json
"github": {
  "command": "npx",
  "args": ["-y", "@modelcontextprotocol/server-github"],
  "env": {
    "GITHUB_PERSONAL_ACCESS_TOKEN": "ghp_your_token_here"
  }
}
```

### 3. Test interaction

Ask Claude: *"List my last 5 pull requests in the gen-ai-software-engineering repository."*

---

## Task 2 — Filesystem MCP

### 1. Add to mcp.json

```json
"filesystem": {
  "command": "npx",
  "args": [
    "-y",
    "@modelcontextprotocol/server-filesystem",
    "C:/Users/KuchukOleksandr/Desktop/gen_ai2/gen-ai-software-engineering"
  ]
}
```

### 2. Test interaction

Ask Claude: *"List all files in the homework-2/src directory."*

---

## Task 3 — Notion MCP

### 1. Create a Notion Integration

Go to https://www.notion.so/my-integrations → New integration → copy the Internal Integration Token.

Share the Notion pages/databases you want to access with the integration.

### 2. Add to mcp.json

```json
"notion": {
  "command": "npx",
  "args": ["-y", "@notionhq/notion-mcp-server"],
  "env": {
    "OPENAPI_MCP_HEADERS": "{\"Authorization\": \"Bearer secret_your_token\", \"Notion-Version\": \"2022-06-28\"}"
  }
}
```

### 3. Test interaction

Ask Claude: *"Give me the last 5 bug tickets from my Notion project."*

---

## Full mcp.json example

See `homework-5/mcp.json` — replace all `<YOUR_*_TOKEN>` placeholders with real credentials before use.

> **Security note**: Never commit real tokens to the repository. Use environment variables or a secrets manager in production.
