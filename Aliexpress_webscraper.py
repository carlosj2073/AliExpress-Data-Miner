import asyncio
import math
import json
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

import jmespath
from loguru import logger as log
from scrapfly import ScrapflyClient, ScrapeConfig
import mysql.connector

# Replace with your scrapfly api key
SCRAPFLY_API_KEY = "..."

# MySQL database connection details — update with your own info
MYSQL_CONFIG = {
    "host": "...",
    "user": "...",
    "password": "...",
    "database": "..."
}

# Initialize Scrapfly client with your API key
client = ScrapflyClient(key=SCRAPFLY_API_KEY)

# Basic settings for each request — country, cookies, etc.
base_config = {
    "asp": True,
    "country": "US",
    "headers": {
        # Cookie helps mimic a real browser session — replace if needed
        "cookie": "..."
    }
}

def update_url_params(url: str, **params):
    """
    Add or update query parameters on a given URL.
    Useful for paginating search results.
    """
    parsed = urlparse(url)
    query = dict(parse_qsl(parsed.query))
    query.update(params)
    new_url = parsed._replace(query=urlencode(query))
    return urlunparse(new_url)

def extract_data_from_page(result):
    """
    Extract the embedded product data JSON from the page's script tag.
    If it’s not found, logs an error and saves the raw page HTML for debugging.
    """
    script = result.selector.xpath('//script[contains(.,"_init_data_=")]')
    if not script:
        log.error("Could not find product data script in page.")
        with open("debug_page.html", "w", encoding="utf-8") as f:
            f.write(result.content.decode())
        return None
    # Use regex to grab the JSON object inside the script
    data_json = script.re(r"_init_data_\s*=\s*{\s*data:\s*({.+}) }")[0]
    data = json.loads(data_json)
    return data["data"]["root"]["fields"]

def parse_products(result):
    """
    Turn the raw JSON data into a list of Python dicts with product details.
    Includes id, title, price, rating, url, and more.
    """
    data = extract_data_from_page(result)
    if not data:
        return []

    products = []
    for item in data["mods"]["itemList"]["content"]:
        p = jmespath.search("""{
            id: productId,
            type: productType,
            thumbnail: image.imgUrl,
            title: title.displayTitle,
            price: prices.salePrice.minPrice,
            currency: prices.salePrice.currencyCode,
            selling_points: sellingPoints[].tagContent.tagText,
            rating: evaluation.starRating,
            trade: trade.tradeDesc
        }""", item)
        # Build the full URL and fix the thumbnail URL
        p['url'] = f"https://www.aliexpress.com/item/{p['id']}.html"
        p['thumbnail'] = f"https:{p['thumbnail']}"
        products.append(p)
    return products

async def scrape_search_results(url, max_pages=2):
    """
    Scrape search results from AliExpress, handling pagination.
    Returns a combined list of products from all pages (up to max_pages).
    """
    log.info(f"Starting scrape for: {url}")
    first_page = await client.async_scrape(ScrapeConfig(url, **base_config))

    data = extract_data_from_page(first_page)
    if not data:
        log.error("Failed to extract data from first page — stopping.")
        return []

    # Calculate how many pages we need to scrape
    page_size = data["pageInfo"]["pageSize"]
    total_results = data["pageInfo"]["totalResults"]
    total_pages = min(math.ceil(total_results / page_size), max_pages)
    log.info(f"Found {total_pages} pages, scraping up to max of {max_pages}")

    all_products = parse_products(first_page)

    # Launch async tasks to scrape additional pages
    tasks = []
    for page_num in range(2, total_pages + 1):
        page_url = update_url_params(first_page.context["url"], page=page_num)
        tasks.append(client.async_scrape(ScrapeConfig(page_url, **base_config)))

    results = await asyncio.gather(*tasks)

    # Parse products from each page and add them to the list
    for res in results:
        all_products.extend(parse_products(res))

    log.info(f"Scraped a total of {len(all_products)} products")
    return all_products

def save_to_mysql(products):
    """
    Save product data into a MySQL database.
    Creates the products table if it doesn’t exist.
    Updates existing entries if the product ID already exists.
    """
    conn = mysql.connector.connect(**MYSQL_CONFIG)
    cursor = conn.cursor()

    # Create table if missing
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id BIGINT PRIMARY KEY,
            type VARCHAR(50),
            thumbnail TEXT,
            title TEXT,
            price FLOAT,
            currency VARCHAR(10),
            selling_points TEXT,
            rating FLOAT,
            trade TEXT,
            url TEXT
        )
    """)

    insert_query = """
        INSERT INTO products (id, type, thumbnail, title, price, currency, selling_points, rating, trade, url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            price = VALUES(price),
            rating = VALUES(rating),
            trade = VALUES(trade),
            selling_points = VALUES(selling_points);
    """

    # Insert or update each product
    for p in products:
        points = ", ".join(p.get("selling_points") or [])
        cursor.execute(insert_query, (
            p["id"],
            p["type"],
            p["thumbnail"],
            p["title"],
            float(p["price"]) if p["price"] else None,
            p["currency"],
            points,
            float(p["rating"]) if p["rating"] else None,
            p["trade"],
            p["url"],
        ))

    conn.commit()
    cursor.close()
    conn.close()
    log.info(f"Saved {len(products)} products to MySQL")

async def main():
    """
    Main entry point:
    Scrapes search results for a sample query and saves to DB.
    """
    start_url = "https://www.aliexpress.com/wholesale?SearchText=desk+lamp&language=en_US"
    products = await scrape_search_results(start_url, max_pages=2)
    save_to_mysql(products)

if __name__ == "__main__":
    asyncio.run(main())
