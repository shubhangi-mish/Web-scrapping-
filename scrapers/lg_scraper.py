from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random
from utils.error_logger import log_error

def get_driver():
    """Initialize the Selenium WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode (no browser window)
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    
    # Use WebDriver Manager to get the latest ChromeDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    return driver

def scrape_lg_canada(product_name, retries=3):
    driver = get_driver()
    
    try:
        query = product_name.replace(" ", "%20")
        url = f"https://www.lg.com/ca_en/search?search={query}"
        
        for attempt in range(retries):
            try:
                driver.get(url)
                time.sleep(random.uniform(3, 5))  # Allow JavaScript to load
                
                soup = BeautifulSoup(driver.page_source, "html.parser")
                
                # Check for bot detection
                if "captcha" in soup.text.lower():
                    raise ValueError("LG Canada CAPTCHA encountered")
                
                # Find product listings
                items = soup.find_all("div", class_="product-list-item")
                
                if not items:
                    raise ValueError("No search results found")
                
                # Extract first valid product
                for item in items:
                    try:
                        title = item.find("h3", class_="model-title").text.strip()
                        price = item.find("span", class_="price-value")
                        
                        if price:
                            return {
                                "Website": "LG Canada",
                                "Title": title,
                                "Price": price.text.strip(),
                                "PriceValidTill": ""
                            }
                    except AttributeError:
                        continue
                
                raise ValueError("No valid products with prices found")
            
            except Exception as e:
                log_error("LG Canada", product_name, str(e))
                if attempt == retries - 1:
                    return {"error": f"Failed after {retries} attempts: {str(e)}"}
    
    finally:
        driver.quit()  # Close the browser instance
    
    return {"error": "Unknown error occurred"}
