# Homework 5 — Configure MCP Servers

> **Student Name**: Kuchuk Oleksandr  
> **AI Tools Used**: Cursor (Composer / Sonnet 4.5)

---

## Overview

This homework configures **four MCP servers** so that Claude/Cursor can interact with GitHub, the local filesystem, Notion, and a custom lorem-ipsum reader built with FastMCP.

| # | Server | Purpose |
|---|--------|---------|
| 1 | **GitHub MCP** | List PRs, summarize commits, create issues |
| 2 | **Filesystem MCP** | Read/list local project files |
| 3 | **Notion MCP** | Query Notion pages and databases |
| 4 | **Custom Lorem Ipsum MCP** | Return N words from lorem-ipsum.md |

---

## MCP Concepts

**Resources** are URIs that Claude can read from — similar to GET endpoints. They expose data from files, APIs, or databases without side effects.  
Example in this project: `lorem://ipsum/{word_count}` returns a word-limited slice of `lorem-ipsum.md`.

**Tools** are actions Claude can call to perform operations — similar to function calls. They can read files, run commands, call APIs, etc.  
Example in this project: the `read` tool accepts an optional `word_count` parameter and returns the corresponding lorem ipsum excerpt.

---

## Project Structure

```
homework-5/
├── mcp.json                        # MCP server configurations
├── README.md
├── HOWTORUN.md
├── custom-mcp-server/
│   ├── server.py                   # FastMCP server (resource + read tool)
│   ├── lorem-ipsum.md              # Source text
│   └── requirements.txt            # fastmcp dependency
└── docs/
    └── screenshots/
        ├── github-mcp-result.png
        ├── filesystem-mcp-result.png
        ├── notion-mcp-result.png
        └── custom-mcp-read-tool-result.png
```

---

## Quick Start

```powershell
# Install custom server dependencies
cd homework-5/custom-mcp-server
py -m pip install -r requirements.txt

# Test the server directly
py server.py
```

Copy `mcp.json` to your Cursor MCP configuration and replace the placeholder tokens.  
See `HOWTORUN.md` for full setup instructions.

---

*Completed as part of the AI-Assisted Development course.*
