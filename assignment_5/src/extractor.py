"""
HTML extractor for book detail pages.
Extracts the 8 raw fields defined in Stage 3 specification.
"""

from typing import Any, Dict, Optional
from bs4 import BeautifulSoup


def extract_raw_record(
    html: str,
    product_url: str,
    source_page: str,
    fetched_at: str,
) -> Dict[str, Any]:
    """
    Extracts the 8 raw fields from a book detail page HTML.
    Selectors are strictly aimed at the product area.
    Missing description stores None (null).
    """
    soup = BeautifulSoup(html, "html.parser")
    product_main = soup.select_one(".product_main")

    title: Optional[str] = None
    price_text: Optional[str] = None
    availability_text: Optional[str] = None
    rating_text: Optional[str] = None

    if product_main:
        h1_tag = product_main.select_one("h1")
        if h1_tag:
            title = h1_tag.get_text(strip=True)

        price_tag = product_main.select_one("p.price_color")
        if price_tag:
            price_text = price_tag.get_text(strip=True)

        avail_tag = product_main.select_one("p.instock.availability")
        if avail_tag:
            availability_text = avail_tag.get_text(strip=True)

        star_tag = product_main.select_one("p.star-rating")
        if star_tag:
            classes = star_tag.get("class", [])
            for cls in classes:
                if cls != "star-rating":
                    rating_text = cls
                    break

    # Description is located below the product_description heading
    description: Optional[str] = None
    desc_header = soup.select_one("#product_description")
    if desc_header:
        p_desc = desc_header.find_next_sibling("p")
        if p_desc:
            desc_text = p_desc.get_text(strip=True)
            if desc_text:
                description = desc_text

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at,
    }
