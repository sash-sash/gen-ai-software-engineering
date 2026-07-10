# Research Notes — context7 usage

## Query 1: Python decimal rounding for money
- Search: `python decimal quantize ROUND_HALF_UP`
- context7 library ID: `/python/cpython`
- Applied insight:
  - Used `Decimal` for all monetary values (`amount`, `fee`, `net_amount`).
  - Standardized rounding with `quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)`.
  - Avoided `float` completely in validation, fraud logic, and settlement.

## Query 2: FastMCP tools and resource patterns
- Search: `fastmcp tool decorator resource URI example`
- context7 library ID: `/jlowin/fastmcp`
- Applied insight:
  - Implemented custom MCP server with `@mcp.tool()` for `get_transaction_status` and `list_pipeline_results`.
  - Implemented `@mcp.resource("pipeline://summary")` to expose summary text.
  - Structured tool outputs as JSON-friendly dicts for easy agent consumption.
