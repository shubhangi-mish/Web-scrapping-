import requests
from bs4 import BeautifulSoup
from config import DELAY
import time
from utils.error_logger import log_error
import random

def get_amazon_headers():
    """Generate fresh headers for each request"""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-CA,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml",
        "Referer": "https://www.amazon.ca/",
        "DNT": "1"
    }

def scrape_amazon(product_name, retries=3):
    for attempt in range(retries):
        try:
            # Add random delay between retries
            time.sleep(random.uniform(1, 3))
            
            query = product_name.replace(" ", "+")
            url = f"https://www.amazon.ca/s?k={query}&i=electronics"
            
            response = requests.get(url, headers=get_amazon_headers())
            response.raise_for_status()
            
            if "api-services-support@amazon.com" in response.text:
                raise ValueError("Amazon bot detection triggered")
            
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Check for captcha
            if soup.find("form", {"action": "/errors/validateCaptcha"}):
                raise ValueError("Amazon CAPTCHA encountered")
            
            # Find all result items
            items = soup.find_all("div", {"data-component-type": "s-search-result"})
            if not items:
                raise ValueError("No search results found")
            
            # Get first valid product
            for item in items:
                try:
                    title = item.find("span", class_="a-size-medium").text.strip()
                    price_whole = item.find("span", class_="a-price-whole")
                    price_fraction = item.find("span", class_="a-price-fraction")
                    
                    if price_whole:
                        price = f"${price_whole.text.strip()}"
                        if price_fraction:
                            price += price_fraction.text.strip()
                        
                        return {
                            "Website": "Amazon",
                            "Title": title,
                            "Price": price,
                            "PriceValidTill": ""
                        }
                except AttributeError:
                    continue
            
            raise ValueError("No valid products with prices found")
            
        except Exception as e:
            log_error("Amazon", product_name, str(e))
            if attempt == retries - 1:
                return {"error": f"Failed after {retries} attempts: {str(e)}"}
            
    return {"error": "Unknown error occurred"}