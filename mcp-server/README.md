# Real Estate MCP Server

Live Abu Dhabi / UAE real estate and rental price data — **100% free, zero API keys needed.**

Data scraped directly from **PropertyFinder.ae** (UAE's #1 property portal) and **Numbeo.com**.

---

## Tools

| Tool | What it does |
|---|---|
| `search_properties_for_rent` | Live rental listings – filter by location, bedrooms, price |
| `search_properties_for_sale` | Live sale listings |
| `get_rental_prices` | Price summary (min/avg/max AED) per bedroom count for an area |
| `get_property_details` | Full details for a single listing by URL path |
| `search_locations` | Find PropertyFinder location IDs for specific communities |
| `get_market_overview` | Monthly rent & buy-price-per-sqm estimates via Numbeo |

---

## Quick Start

```bash
cd mcp-server
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
python3 server.py               # starts the MCP server on stdio
```

---

## Connect to Claude Desktop

Edit your `claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "real-estate": {
      "command": "/full/path/to/Ollama_Project/mcp-server/venv/bin/python3",
      "args": ["/full/path/to/Ollama_Project/mcp-server/server.py"]
    }
  }
}
```

Config file location:
- **macOS**:   `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
- **Linux**:   `~/.config/Claude/claude_desktop_config.json`

Restart Claude Desktop after saving. The "real-estate" server will appear in the tools panel.

---

## Location IDs (UAE Emirates)

| Emirate / City | `location_id` |
|---|---|
| **Abu Dhabi** | **6** (default) |
| Dubai | 1 |
| Sharjah | 4 |
| Ajman | 5 |
| Ras Al Khaimah | 3 |
| Fujairah | 7 |

Use the `search_locations` tool to find IDs for specific communities (Al Reem Island, Saadiyat, Yas Island, etc.).

---

## Example Questions (once connected to Claude)

- *"Search for 2-bedroom apartments for rent in Abu Dhabi under AED 150,000 per year"*
- *"What are the average rental prices for apartments in Abu Dhabi right now?"*
- *"Find villas for sale in Abu Dhabi with at least 4 bedrooms"*
- *"Give me a market overview for Abu Dhabi rental prices"*
- *"Search for the location ID for Saadiyat Island"*
- *"Compare rental prices between Abu Dhabi and Dubai"*
