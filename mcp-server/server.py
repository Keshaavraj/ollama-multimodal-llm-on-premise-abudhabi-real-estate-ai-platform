"""
Real Estate MCP Server  –  100 % FREE, no API key required
===========================================================
Scrapes live property data from PropertyFinder.ae (Abu Dhabi / UAE)
and Numbeo for rental price indices.

Tools exposed
─────────────
  search_properties_for_rent   – Rental listings
  search_properties_for_sale   – Sale listings
  get_rental_prices            – Price summary by bedroom count
  get_property_details         – Full details for one property
  search_locations             – Resolve area names to location IDs
  get_market_overview          – High-level market stats (Numbeo)

Data sources (all free, no registration)
  • propertyfinder.ae  – UAE's top property portal (scrapes __NEXT_DATA__ JSON)
  • numbeo.com         – Crowd-sourced rental index per city
"""

import os
import re
import json
import httpx
from mcp.server.fastmcp import FastMCP

# ── Browser-like headers ──────────────────────────────────────────────────────
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

PF_BASE = "https://www.propertyfinder.ae"

# PropertyFinder location IDs (UAE emirates + major cities)
# Discover more with the search_locations tool.
KNOWN_LOCATIONS: dict[str, str] = {
    "abu dhabi":       "6",
    "dubai":           "1",
    "sharjah":         "4",
    "ajman":           "5",
    "ras al khaimah":  "3",
    "fujairah":        "7",
}

# PropertyFinder property type IDs
PROPERTY_TYPES: dict[str, str] = {
    "apartment":  "1",
    "apartments": "1",
    "villa":      "2",
    "villas":     "2",
    "townhouse":  "3",
    "townhouses": "3",
    "penthouse":  "4",
    "studio":     "1",   # studios are apartments with 0 beds
    "office":     "21",
    "land":       "14",
}

# ── MCP Server ────────────────────────────────────────────────────────────────
mcp = FastMCP(
    "Abu Dhabi Real Estate",
    instructions=(
        "Provides live UAE real estate and rental price data via PropertyFinder.ae "
        "and Numbeo. No API key required."
    ),
)


# ── Low-level helpers ─────────────────────────────────────────────────────────

async def _fetch_html(url: str, params: dict | None = None) -> str:
    async with httpx.AsyncClient(
        headers=HEADERS,
        follow_redirects=True,
        timeout=20,
    ) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.text


def _extract_next_data(html: str) -> dict:
    match = re.search(
        r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>',
        html,
        re.DOTALL,
    )
    if not match:
        return {}
    return json.loads(match.group(1))


def _format_property(p: dict) -> dict:
    """Flatten a PropertyFinder property object to a clean dict."""
    price_obj = p.get("price") or {}
    price_val = price_obj.get("value")
    currency  = price_obj.get("currency", "AED")
    period    = price_obj.get("period", "")
    price_label = (
        f"{currency} {int(price_val):,} / {period}" if price_val
        else "Price on request"
    )

    loc  = p.get("location") or {}
    agent = p.get("agent") or {}
    broker = p.get("broker") or {}

    return {
        "id":                p.get("id") or p.get("listing_id"),
        "title":             p.get("title"),
        "price":             price_label,
        "bedrooms":          p.get("bedrooms"),
        "bathrooms":         p.get("bathrooms"),
        "area_sqft":         p.get("size"),
        "property_type":     p.get("property_type"),
        "offering":          p.get("offering_type"),
        "location":          loc.get("full_name"),
        "community":         loc.get("name"),
        "city":              loc.get("path_name", "").split(",")[-1].strip(),
        "coordinates": {
            "lat": (loc.get("coordinates") or {}).get("lat"),
            "lon": (loc.get("coordinates") or {}).get("lon"),
        },
        "is_verified":       p.get("is_verified"),
        "furnishing":        p.get("furnished"),
        "completion_status": p.get("completion_status"),
        "amenities":         p.get("amenity_names", []),
        "agent_name":        agent.get("name"),
        "agency":            broker.get("name"),
        "reference":         p.get("reference"),
        "url":               PF_BASE + p.get("details_path", ""),
        "listed_date":       p.get("listed_date"),
        "price_per_sqft":    (p.get("price_per_area") or {}).get("value"),
    }


def _build_search_params(
    category: str,          # "2"=rent "1"=sale
    location_id: str,
    property_type: str,
    min_bedrooms: int,
    max_bedrooms: int,
    min_price: int,
    max_price: int,
    page: int,
    rent_period: str,
) -> dict:
    params: dict = {
        "c": category,
        "l": location_id,
        "page[number]": page,
        "sort": "mr",       # most recent
    }
    if property_type:
        type_id = PROPERTY_TYPES.get(property_type.lower(), "")
        if type_id:
            params["t"] = type_id
    if min_bedrooms:
        params["bmin"] = min_bedrooms
    if max_bedrooms:
        params["bmax"] = max_bedrooms
    if min_price:
        params["pmin"] = min_price
    if max_price:
        params["pmax"] = max_price
    if category == "2" and rent_period:          # rent only
        params["rp"] = rent_period[0]            # y/m/w/d
    return params


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool()
async def search_properties_for_rent(
    location: str = "Abu Dhabi",
    location_id: str = "6",
    property_type: str = "",
    min_bedrooms: int = 0,
    max_bedrooms: int = 0,
    min_price: int = 0,
    max_price: int = 0,
    rent_period: str = "yearly",
    page: int = 1,
) -> dict:
    """
    Search live RENTAL listings on PropertyFinder.ae for Abu Dhabi / UAE.

    Parameters
    ----------
    location      : Human-readable city / area name (just for display).
    location_id   : PropertyFinder location ID.
                    6=Abu Dhabi, 1=Dubai, 4=Sharjah, 3=RAK, 5=Ajman, 7=Fujairah.
                    Use search_locations to find IDs for specific communities.
    property_type : "apartment", "villa", "townhouse", "penthouse", or "" (all).
    min_bedrooms  : 0 = studio/any.
    max_bedrooms  : 0 = no upper limit.
    min_price     : Minimum price in AED (0 = no limit).
    max_price     : Maximum price in AED (0 = no limit).
    rent_period   : "yearly" (default), "monthly", "weekly", "daily".
    page          : Page number, 1-based.
    """
    params = _build_search_params(
        "2", location_id, property_type,
        min_bedrooms, max_bedrooms,
        min_price, max_price,
        page, rent_period,
    )
    url = f"{PF_BASE}/en/search"

    try:
        html = await _fetch_html(url, params)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code} – {url}"}
    except Exception as e:
        return {"error": str(e)}

    data = _extract_next_data(html)
    page_props = data.get("props", {}).get("pageProps", {})
    sr = page_props.get("searchResult", {})
    properties = sr.get("properties", [])
    meta = sr.get("meta", {})

    return {
        "source": "propertyfinder.ae",
        "purpose": "for-rent",
        "location": location,
        "location_id": location_id,
        "rent_period": rent_period,
        "page": page,
        "total_results": meta.get("total"),
        "total_pages": meta.get("pages"),
        "properties_on_page": len(properties),
        "properties": [_format_property(p) for p in properties],
    }


@mcp.tool()
async def search_properties_for_sale(
    location: str = "Abu Dhabi",
    location_id: str = "6",
    property_type: str = "",
    min_bedrooms: int = 0,
    max_bedrooms: int = 0,
    min_price: int = 0,
    max_price: int = 0,
    page: int = 1,
) -> dict:
    """
    Search live SALE listings on PropertyFinder.ae for Abu Dhabi / UAE.

    Parameters
    ----------
    location      : Human-readable city / area name (just for display).
    location_id   : PropertyFinder location ID.
                    6=Abu Dhabi, 1=Dubai, 4=Sharjah, 3=RAK, 5=Ajman, 7=Fujairah.
    property_type : "apartment", "villa", "townhouse", or "" (all).
    min_bedrooms  : Minimum bedrooms (0 = any).
    max_bedrooms  : Maximum bedrooms (0 = no limit).
    min_price     : Minimum price in AED (0 = no limit).
    max_price     : Maximum price in AED (0 = no limit).
    page          : Page number, 1-based.
    """
    params = _build_search_params(
        "1", location_id, property_type,
        min_bedrooms, max_bedrooms,
        min_price, max_price,
        page, "",
    )
    url = f"{PF_BASE}/en/search"

    try:
        html = await _fetch_html(url, params)
    except httpx.HTTPStatusError as e:
        return {"error": f"HTTP {e.response.status_code} – {url}"}
    except Exception as e:
        return {"error": str(e)}

    data = _extract_next_data(html)
    page_props = data.get("props", {}).get("pageProps", {})
    sr = page_props.get("searchResult", {})
    properties = sr.get("properties", [])
    meta = sr.get("meta", {})

    return {
        "source": "propertyfinder.ae",
        "purpose": "for-sale",
        "location": location,
        "location_id": location_id,
        "page": page,
        "total_results": meta.get("total"),
        "total_pages": meta.get("pages"),
        "properties_on_page": len(properties),
        "properties": [_format_property(p) for p in properties],
    }


@mcp.tool()
async def get_rental_prices(
    location: str = "Abu Dhabi",
    location_id: str = "6",
    property_type: str = "apartment",
    rent_period: str = "yearly",
) -> dict:
    """
    Fetch a live rental price summary (min / avg / max) broken down by
    bedroom count for a specific area.

    Parameters
    ----------
    location      : Human-readable name (for display).
    location_id   : PropertyFinder location ID (6 = Abu Dhabi).
    property_type : "apartment" (default), "villa", "townhouse".
    rent_period   : "yearly" (default), "monthly".
    """
    params = _build_search_params(
        "2", location_id, property_type,
        0, 0, 0, 0, 1, rent_period,
    )
    url = f"{PF_BASE}/en/search"

    try:
        html = await _fetch_html(url, params)
    except Exception as e:
        return {"error": str(e)}

    data = _extract_next_data(html)
    sr = data.get("props", {}).get("pageProps", {}).get("searchResult", {})
    properties = sr.get("properties", [])

    buckets: dict[str, list[float]] = {}
    for p in properties:
        price_val = (p.get("price") or {}).get("value")
        beds = p.get("bedrooms_value") or p.get("bedrooms")
        if price_val is None:
            continue
        beds_str = str(beds).lower() if beds is not None else ""
        key = "Studio" if beds == 0 or beds_str == "studio" else (f"{beds} BR" if beds is not None else "Unknown")
        buckets.setdefault(key, []).append(float(price_val))

    summary: dict = {}
    for key in sorted(buckets):
        prices = buckets[key]
        summary[key] = {
            "listings_sampled": len(prices),
            "min_aed":  int(min(prices)),
            "avg_aed":  int(sum(prices) / len(prices)),
            "max_aed":  int(max(prices)),
        }

    meta = sr.get("meta", {})
    return {
        "source": "propertyfinder.ae",
        "location": location,
        "location_id": location_id,
        "property_type": property_type,
        "rent_period": rent_period,
        "total_listings": meta.get("total"),
        "listings_on_page": len(properties),
        "price_summary_by_bedrooms": summary,
    }


@mcp.tool()
async def get_property_details(property_path: str) -> dict:
    """
    Fetch full details for a specific PropertyFinder listing.

    Parameters
    ----------
    property_path : The URL path shown in search results' `url` field,
                    e.g. "/en/property/apartments-for-rent/apartment/
                    abu-dhabi--al-reem-island--shams-abu-dhabi--
                    sun-tower/sale-52396507-Bz37DP7b/"
                    You can also pass the full URL.
    """
    if property_path.startswith("http"):
        url = property_path
    else:
        url = PF_BASE + property_path

    try:
        html = await _fetch_html(url)
    except Exception as e:
        return {"error": str(e)}

    data = _extract_next_data(html)
    page_props = data.get("props", {}).get("pageProps", {})

    # PropertyFinder puts the listing under "listing" or "property"
    prop = page_props.get("listing") or page_props.get("property")
    if not prop:
        return {"error": "Could not parse property details from page.", "url": url}

    return _format_property(prop)


@mcp.tool()
async def search_locations(query: str, purpose: str = "rent") -> list[dict]:
    """
    Search PropertyFinder for location IDs matching an area or community name.

    Use the returned `id` in other tools' `location_id` parameter.

    Parameters
    ----------
    query   : Area name, e.g. "Al Reem Island", "Saadiyat", "Khalidiyah".
    purpose : "rent" (default) or "sale".
    """
    cat = "2" if purpose == "rent" else "1"
    url = f"{PF_BASE}/en/search"
    params = {"c": cat, "q": query, "l": "6"}   # start within Abu Dhabi scope

    try:
        html = await _fetch_html(url, params)
    except Exception as e:
        return [{"error": str(e)}]

    data = _extract_next_data(html)
    page_props = data.get("props", {}).get("pageProps", {})
    fvq = page_props.get("filtersValueFromQuery", {})
    location_ids = fvq.get("filter[locations_ids]", [])

    # Collect unique locations from search results too
    sr_props = page_props.get("searchResult", {}).get("properties", [])
    seen: set[str] = set()
    results: list[dict] = []

    for loc_entry in location_ids:
        lid = str(loc_entry.get("id", ""))
        if lid not in seen:
            seen.add(lid)
            results.append({
                "id":        lid,
                "name":      loc_entry.get("n"),
                "slug":      loc_entry.get("s"),
                "type":      loc_entry.get("l_t"),
            })

    for p in sr_props:
        loc = p.get("location") or {}
        path = loc.get("path", "")
        lid  = path.split(".")[-1] if path else ""
        if lid and lid not in seen:
            seen.add(lid)
            results.append({
                "id":    lid,
                "name":  loc.get("name"),
                "slug":  loc.get("slug"),
                "type":  loc.get("type"),
                "full":  loc.get("full_name"),
            })

    return results if results else [{"note": f"No locations found for '{query}'"}]


@mcp.tool()
async def get_market_overview(city: str = "Abu Dhabi") -> dict:
    """
    Return a live market overview combining:
    - Monthly rent estimates from Numbeo (crowd-sourced, free)
    - Buy price per sqm from Numbeo

    Parameters
    ----------
    city : City name, e.g. "Abu Dhabi", "Dubai", "Sharjah".
    """
    url = "https://www.numbeo.com/cost-of-living/in/" + city.replace(" ", "-")

    try:
        html = await _fetch_html(url)
    except Exception as e:
        return {"error": str(e)}

    # Rent rows: "1 Bedroom Apartment in City Centre", "3 Bedroom Apartment..."
    rent_pattern = re.compile(
        r'<tr[^>]*>\s*<td[^>]*>\s*((?:\d+ Bedroom|Studio)[^<]*)'
        r'.*?<span class="first_currency">([\d,\.]+)&nbsp;AED</span>',
        re.DOTALL | re.IGNORECASE,
    )
    rent_rows: dict = {}
    for m in rent_pattern.finditer(html):
        label = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        value = m.group(2).replace(",", "")
        rent_rows[label] = f"AED {float(value):,.0f} / month"

    # Buy price per sqm rows
    buy_pattern = re.compile(
        r'<td[^>]*>\s*(Price per Square Meter[^<]*)'
        r'.*?<span class="first_currency">([\d,\.]+)&nbsp;AED</span>',
        re.DOTALL | re.IGNORECASE,
    )
    buy_rows: dict = {}
    for m in buy_pattern.finditer(html):
        label = re.sub(r"<[^>]+>", "", m.group(1)).strip()
        value = m.group(2).replace(",", "")
        buy_rows[label] = f"AED {float(value):,.0f} / sqm"

    if not rent_rows and not buy_rows:
        return {
            "city": city,
            "source": "numbeo.com",
            "note": "Could not parse price table. Try the URL directly.",
            "url": url,
        }

    result: dict = {
        "city": city,
        "source": "numbeo.com",
        "currency": "AED",
        "monthly_rent_estimates": rent_rows,
        "note": "Crowd-sourced averages. Prices vary by area and quality.",
        "url": url,
    }
    if buy_rows:
        result["buy_price_per_sqm"] = buy_rows
    return result


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    transport = os.getenv("MCP_TRANSPORT", "stdio")   # "stdio" for Claude Desktop
    host      = os.getenv("MCP_HOST", "127.0.0.1")   # "0.0.0.0" in Docker
    port      = int(os.getenv("MCP_PORT", "8080"))    # HTTP port when not stdio

    if transport == "stdio":
        mcp.run(transport="stdio")
    else:
        mcp.run(transport=transport, host=host, port=port)
