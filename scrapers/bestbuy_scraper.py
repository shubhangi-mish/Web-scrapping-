import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random
from config import HEADERS
from utils.error_logger import log_error

def scrape_bestbuy(product_name, max_retries=3):
    """Scrape Best Buy using API first, then fallback to web scraping if needed"""
    
    # Step 1: Attempt API-based scraping
    for attempt in range(max_retries):
        try:
            search_term = product_name.replace(' ', '%20')
            url = f"https://www.bestbuy.ca/api/v2/json/search?query={search_term}&page=1&pageSize=5"
            
            request_headers = {
                **HEADERS,
                "Accept": "application/json",
                "Referer": "https://www.bestbuy.ca/en-ca",
                "sec-ch-ua": '"Google Chrome";v="123", "Not:A-Brand";v="8", "Chromium";v="123"',
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": '"Windows"'
            }
            
            time.sleep(random.uniform(1, 3))  # Add delay to avoid detection
            
            response = requests.get(url, headers=request_headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            
            if not data.get('products'):
                log_error("BestBuyAPI", product_name, "No products found in API response")
                continue  
                
            model_number = extract_model_number(product_name)
            for product in data['products']:
                if (model_number and model_number.lower() in product['name'].lower()) or \
                   (product_name.lower() in product['name'].lower()):
                    return format_product_data(product)
            
            for product in data['products']:  # Return first product with price if no exact match
                if product.get('salePrice'):
                    return format_product_data(product)
            
            return {"error": "No matching products with prices found"}
        
        except requests.exceptions.RequestException as e:
            log_error("BestBuyAPI", product_name, f"Request failed: {str(e)}")
            if attempt == max_retries - 1:
                break  # If all retries fail, move to web scraping
            
        except Exception as e:
            log_error("BestBuyAPI", product_name, str(e))
            return {"error": str(e)}

    # Step 2: Fallback to Web Scraping using Selenium + BeautifulSoup
    try:
        query = product_name.replace(" ", "+")
        url = f"https://www.bestbuy.ca/en-ca/search?search={query}"
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.get(url)
        time.sleep(3)  # Wait for page to load
        
        soup = BeautifulSoup(driver.page_source, "html.parser")
        price_element = soup.find("div", class_="price_FHDfG")
        title_element = soup.find("div", class_="productItemName_3n3gD")
        
        driver.quit()

        if not price_element or not title_element:
            return {"error": "Product details not found on webpage"}
        
        return {
            "Website": "Best Buy",
            "Title": title_element.text.strip(),
            "Price": price_element.text.strip(),
            "PriceValidTill": ""  # Best Buy often shows promo dates in a separate element
        }
    
    except Exception as e:
        log_error("BestBuyScraper", product_name, str(e))
        return {"error": str(e)}

def extract_model_number(product_name):
    """Extract model number from product name (e.g., 50A68N)"""
    parts = product_name.split('-')
    return parts[-1].strip() if len(parts) > 1 else None

def format_product_data(product):
    """Format product data into a structured format"""
    return {
        "Website": "Best Buy",
        "Title": product['name'],
        "Price": f"${product['salePrice']:.2f}",
        "PriceValidTill": product.get('priceExpiry', '')
    }
