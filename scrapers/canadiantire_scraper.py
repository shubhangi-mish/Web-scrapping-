import requests
from bs4 import BeautifulSoup
from config import HEADERS, DELAY
import logging
from config import HEADERS, TIMEOUT  # Add TIMEOUT import

logger = logging.getLogger(__name__)

def scrape_canadiantire(product_name):
    result = {
        "Website": "Canadian Tire",
        "Title": "",
        "Price": "",
        "PriceValidTill": "",
        "error": None
    }
    
    try:
        query = product_name.replace(" ", "+")
        url = f"https://www.canadiantire.ca/en/search-results.html?q={query}"
        
        response = requests.get(url, headers=HEADERS["default"], timeout=TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        product = soup.find("div", class_="product-tile")
        if not product:
            raise Exception("No products found on search results page")
        
        title = product.find("a", class_="link__click")
        price = product.find("span", class_="price__now")
        
        if title:
            result["Title"] = title.text.strip()
        if price:
            result["Price"] = price.text.strip()
            
        if not result["Title"] or not result["Price"]:
            raise Exception("Could not extract complete product details")
            
    except Exception as e:
        result["error"] = f"Canadian Tire scraping failed: {str(e)}"
        logger.error(result["error"])
    
    return result