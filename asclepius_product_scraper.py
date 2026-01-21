"""
Asclepius Wellness Product Scraper
---------------------------------
Scrapes product catalog pages and extracts:
- Product name
- Price
- Image URL
- Other available details

Usage:
1. Add catalog URLs to URLS list.
2. Adjust CSS selectors in SELECTORS if the site structure changes.
3. Run: python asclepius_product_scraper.py

Output:
- products.json
- images/ (downloaded product images)

DISCLAIMER:
Ensure scraping complies with the website's Terms of Service and robots.txt.
"""

import os
import json
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

# ---------------- CONFIG ---------------- #
URLS = [
    "https://asclepiuswellness.com/product/wellness-product/",
    # Add more catalog URLs here
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; AWPLScraper/1.0)"
}

OUTPUT_JSON = "products.json"
IMAGES_DIR = "images"
REQUEST_DELAY = 2  # seconds between requests

# CSS selectors (update if website changes)
SELECTORS = {
    "product_card": ".product",           # main product container
    "name": ".woocommerce-loop-product__title",
    "price": ".price",
    "image": "img",
    "link": "a"
}
# ---------------------------------------- #


def safe_filename(url: str) -> str:
    path = urlparse(url).path
    return os.path.basename(path.split("?")[0])


def download_image(img_url: str) -> str:
    os.makedirs(IMAGES_DIR, exist_ok=True)
    filename = safe_filename(img_url)
    filepath = os.path.join(IMAGES_DIR, filename)

    if os.path.exists(filepath):
        return filepath

    r = requests.get(img_url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    with open(filepath, "wb") as f:
        f.write(r.content)

    return filepath


def scrape_catalog(url: str) -> list:
    print(f"Scraping: {url}")
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    products = []

    for card in soup.select(SELECTORS["product_card"]):
        try:
            name_el = card.select_one(SELECTORS["name"])
            price_el = card.select_one(SELECTORS["price"])
            img_el = card.select_one(SELECTORS["image"])
            link_el = card.select_one(SELECTORS["link"])

            name = name_el.get_text(strip=True) if name_el else None
            price = price_el.get_text(strip=True) if price_el else None
            img_url = urljoin(url, img_el.get("src")) if img_el else None
            product_url = urljoin(url, link_el.get("href")) if link_el else None

            image_path = download_image(img_url) if img_url else None

            products.append({
                "name": name,
                "price": price,
                "image_url": img_url,
                "image_path": image_path,
                "product_url": product_url
            })
        except Exception as e:
            print(f"Failed to parse product: {e}")

    return products


def main():
    all_products = []

    for url in URLS:
        all_products.extend(scrape_catalog(url))
        time.sleep(REQUEST_DELAY)

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_products, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(all_products)} products to {OUTPUT_JSON}")


if __name__ == "__main__":
    main()
