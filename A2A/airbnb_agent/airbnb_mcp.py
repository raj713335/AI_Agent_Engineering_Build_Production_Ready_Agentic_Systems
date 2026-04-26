"""
Dummy Airbnb MCP Server (Server A in the architecture diagram).

Exposes Airbnb search tools via stdio MCP transport.
Returns fake listings — no real Airbnb API calls.

Run standalone:  python -m airbnb_agent.airbnb_mcp
"""

import random

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("airbnb")


@mcp.tool()
async def search_listings(
    location: str,
    checkin: str,
    checkout: str,
    guests: int = 2,
) -> dict:
    """Search for Airbnb listings in a given location.

    Args:
        location: City or area (e.g. "Los Angeles, CA")
        checkin: Check-in date (e.g. "2025-04-15")
        checkout: Check-out date (e.g. "2025-04-18")
        guests: Number of guests
    """
    listings = []
    for i in range(1, random.randint(3, 6)):
        price = random.randint(80, 350)
        listings.append({
            "id": f"listing_{random.randint(1000, 9999)}",
            "title": random.choice([
                f"Cozy {random.choice(['Studio', '1-Bed', '2-Bed'])} in {location}",
                f"Modern {random.choice(['Apt', 'Loft', 'Condo'])} near downtown {location}",
                f"Charming {random.choice(['Cottage', 'House', 'Suite'])} in {location}",
            ]),
            "price_per_night_usd": price,
            "rating": round(random.uniform(3.5, 5.0), 1),
            "reviews": random.randint(10, 500),
            "guests_max": random.randint(guests, guests + 4),
            "url": f"https://www.airbnb.com/rooms/{random.randint(10000, 99999)}",
        })
    return {
        "location": location,
        "checkin": checkin,
        "checkout": checkout,
        "guests": guests,
        "results_count": len(listings),
        "listings": listings,
    }


@mcp.tool()
async def get_listing_details(listing_id: str) -> dict:
    """Get detailed information about a specific Airbnb listing.

    Args:
        listing_id: The listing ID (e.g. "listing_1234")
    """
    return {
        "id": listing_id,
        "title": f"Beautiful Stay — {listing_id}",
        "description": "A wonderful place with great amenities and a fantastic location.",
        "price_per_night_usd": random.randint(80, 350),
        "cleaning_fee_usd": random.randint(20, 80),
        "rating": round(random.uniform(4.0, 5.0), 1),
        "amenities": random.sample(
            ["WiFi", "Kitchen", "AC", "Pool", "Parking", "Washer", "Gym", "Hot Tub"],
            k=random.randint(3, 6),
        ),
        "host": {"name": "Alex", "superhost": random.choice([True, False])},
        "url": f"https://www.airbnb.com/rooms/{listing_id.split('_')[-1]}",
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
