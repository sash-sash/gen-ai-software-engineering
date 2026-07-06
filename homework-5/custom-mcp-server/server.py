"""
Custom MCP Server — Lorem Ipsum Reader
Built with FastMCP.

Concepts:
  Resources  — URIs that Claude can read from (e.g. files, APIs).
               This server exposes lorem://ipsum/{word_count} so Claude
               can fetch a snippet of lorem-ipsum.md by word count.
  Tools      — Actions Claude can call to perform operations.
               The `read` tool wraps the resource and is the primary
               way Claude interacts with this server.
"""

from pathlib import Path

from fastmcp import FastMCP

LOREM_IPSUM_PATH = Path(__file__).parent / "lorem-ipsum.md"

mcp = FastMCP(
    name="Custom Lorem Ipsum MCP Server",
    instructions=(
        "Use the `read` tool to fetch a word-limited excerpt from the "
        "built-in lorem-ipsum text. Pass `word_count` to control how many "
        "words are returned (default: 30)."
    ),
)


# ---------------------------------------------------------------------------
# Resource — readable URI
# ---------------------------------------------------------------------------

@mcp.resource("lorem://ipsum/{word_count}")
def lorem_resource(word_count: int = 30) -> str:
    """
    Returns the first *word_count* words from lorem-ipsum.md.

    URI example: lorem://ipsum/50
    """
    text = LOREM_IPSUM_PATH.read_text(encoding="utf-8")
    words = text.split()
    return " ".join(words[:word_count])


# ---------------------------------------------------------------------------
# Tool — callable action
# ---------------------------------------------------------------------------

@mcp.tool()
def read(word_count: int = 30) -> str:
    """
    Read the first `word_count` words from the lorem-ipsum resource.

    Args:
        word_count: Number of words to return (default: 30).

    Returns:
        A string containing exactly `word_count` words from lorem-ipsum.md.
    """
    text = LOREM_IPSUM_PATH.read_text(encoding="utf-8")
    words = text.split()
    return " ".join(words[:word_count])


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
