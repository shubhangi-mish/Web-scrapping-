import requests
from bs4 import BeautifulSoup
from config import HEADERS, DELAY
import logging
from config import HEADERS, TIMEOUT  # Add TIMEOUT import

logger = logging.getLogger(__name__)

def scrape_samsung(product_name):
    result = {
        "Website": "Samsung",
        "Title": "",
        "Price": "",
        "PriceValidTill": "",
        "error": None
    }
    
    try:
        # Samsung Canada store search
        query = product_name.replace(" ", "+")
        url = f"https://www.samsung.com/ca/search/?searchvalue={query}"
        
        response = requests.get(url, headers=HEADERS["default"], timeout=TIMEOUT)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        product = soup.find("div", class_="product-card")
        if not product:
            raise Exception("No products found on search results page")
        
        title = product.find("h4", class_="product-card__title")
        price = product.find("span", class_="product-card__price-current")
        
        if title:
            result["Title"] = title.text.strip()
        if price:
            result["Price"] = price.text.strip()
            
        if not result["Title"] or not result["Price"]:
            raise Exception("Could not extract complete product details")
            
    except Exception as e:
        result["error"] = f"Samsung scraping failed: {str(e)}"
        logger.error(result["error"])
    
    return result