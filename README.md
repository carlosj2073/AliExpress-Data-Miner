# AliExpress Product Scraper
This project scrapes product listings from AliExpress to gather useful details like title, price, rating, and more — perfect for product research, tracking trends, or exploring niche opportunities.

## sql folder
- This folder is not needed for the scraper, but it houses the SQL queries needed for the dashboard I made, which you can view here: 
- https://public.tableau.com/views/Aliexpress_dashboard/Dashboard1?:language=en-US&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link

## Tools used
- Python (asyncio, BeautifulSoup, Selenium)
- Scrapfly SDK (optional, for advanced scraping support)
- Loguru for clean logging


## How to Run
- Install dependencies in bash: pip install -r requirements.txt
- Replace file paths and configurations with your own
- Adjustments: By default, it scrapes a sample search like desk lamp. It can be modified to run a different search or a longer search (max pages)

## Notes
- AliExpress changes frequently — scraping may break, so check HTML structure if needed.
- If using Scrapfly, you’ll need an API key. Replace "..." with your actual key in the config.



