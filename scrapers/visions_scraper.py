import requests
from bs4 import BeautifulSoup
from config import HEADERS, DELAY
import logging
from config import HEADERS, TIMEOUT 

logger = logging.getLogger(__name__)

def scrape_visions(product_name):
    result = {
        "Website": "Visions",
        "Title": "",
        "Price": "",
        "PriceValidTill": "",
        "error": None
    }
    
    try:
        query = product_name.replace(" ", "%20")
        url = f"https://www.visions.ca/search-results?keywords={query}"
        
        response = requests.get(url, headers=HEADERS["default"], timeout=TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        product = soup.find("div", class_="product-tile")
        if not product:
            raise Exception("No products found on search results page")
        
        title = product.find("div", class_="product-name")
        price = product.find("span", class_="price-value")
        
        if title:
            result["Title"] = title.text.strip()
        if price:
            result["Price"] = price.text.strip()
            
        if not result["Title"] or not result["Price"]:
            raise Exception("Could not extract complete product details")
            
    except Exception as e:
        result["error"] = f"Visions scraping failed: {str(e)}"
        logger.error(result["error"])
    
    return result