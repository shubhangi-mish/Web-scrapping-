import requests
from bs4 import BeautifulSoup
from config import HEADERS, TIMEOUT
import logging
import random

logger = logging.getLogger(__name__)

def scrape_staples(product_name):
    result = {
        "Website": "Staples",
        "Title": "",
        "Price": "",
        "PriceValidTill": "",
        "error": None
    }
    
    try:
        query = product_name.replace(" ", "+")
        url = f"https://www.staples.ca/products/search?query={query}"  # Changed endpoint
        
        # Rotate user agents
        headers = HEADERS["Staples"].copy()
        headers["User-Agent"] = random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        ])
        
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        
        if response.status_code == 403:
            raise Exception("Blocked by Staples - try again later or use proxies")
            
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        product = soup.find("div", class_="product-tile")
        if not product:
            raise Exception("No products found on search results page")
        
        title = product.find("h3", class_="product-title")
        price = product.find("span", class_="price__amount")
        
        if title:
            result["Title"] = title.text.strip()
        if price:
            result["Price"] = price.text.strip()
            
        if not result["Title"] or not result["Price"]:
            raise Exception("Could not extract complete product details")
            
    except Exception as e:
        result["error"] = f"Staples scraping failed: {str(e)}"
        logger.error(result["error"])
    
    return result