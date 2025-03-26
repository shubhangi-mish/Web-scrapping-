import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import random
from config import HEADERS, TIMEOUT 
from utils.error_logger import log_error
from config import get_random_user_agent, get_random_proxy, DELAY, RETRIES

class CostcoScraper:
    def __init__(self, debug_mode=False):
        self.debug_mode = debug_mode
        self.current_proxy = get_random_proxy()
        self.user_agent = get_random_user_agent()

    def get_webdriver(self):
        """Configure Chrome WebDriver with proxy and debugging options"""
        chrome_options = Options()
        
        if not self.debug_mode:
            chrome_options.add_argument("--headless=new")
        
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_argument(f"user-agent={self.user_agent}")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        
        # Proxy settings
        if self.current_proxy:
            chrome_options.add_argument(f"--proxy-server={self.current_proxy}")
        
        # Debugging options
        if self.debug_mode:
            chrome_options.add_argument("--auto-open-devtools-for-tabs")
            chrome_options.add_argument("--window-size=1400,900")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Stealth settings
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": self.user_agent})
        driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        
        return driver

    def scrape_costco(self, product_name, max_retries=RETRIES):
        """Main scraping method with enhanced error handling"""
        # Try API first
        api_result = self.try_costco_api(product_name)
        if not api_result.get('error'):
            return api_result
        
        # Fallback to browser
        return self.try_costco_browser(product_name, max_retries)

    def try_costco_api(self, product_name):
        """API attempt with proxy rotation"""
        try:
            search_term = product_name.replace(' ', '%20')
            url = f"https://www.costco.ca/rest/v2/costco/products/search?query={search_term}&pageSize=1"
            
            headers = {
                **HEADERS,
                "User-Agent": self.user_agent,
                "Accept": "application/json",
                "Referer": "https://www.costco.ca/"
            }
            
            proxies = {"http": self.current_proxy, "https": self.current_proxy} if self.current_proxy else None
            
            response = requests.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=TIMEOUT
            )
            response.raise_for_status()
            
            data = response.json()
            if data.get('products'):
                product = data['products'][0]
                return {
                    "Website": "Costco",
                    "Title": product['name'],
                    "Price": f"${product['price']['value']:.2f}",
                    "PriceValidTill": ""
                }
        except Exception as e:
            log_error("CostcoAPI", product_name, str(e))
            self.rotate_proxy()
        
        return {"error": "API attempt failed"}

    def try_costco_browser(self, product_name, max_retries):
        """Browser automation with enhanced debugging"""
        driver = None
        for attempt in range(max_retries):
            try:
                driver = self.get_webdriver()
                search_term = product_name.replace(' ', '+')
                url = f"https://www.costco.ca/CatalogSearch?keyword={search_term}"
                
                driver.get(url)
                
                # Debugging helpers
                if self.debug_mode:
                    print("Page URL:", driver.current_url)
                    driver.save_screenshot('debug_before_interaction.png')
                    with open('page_source.html', 'w', encoding='utf-8') as f:
                        f.write(driver.page_source)
                
                time.sleep(DELAY)
                
                # Try BeautifulSoup first
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                product = soup.find('div', {'class': 'product-tile'})
                
                if product:
                    title = product.find('span', {'class': 'description'}).text.strip()
                    price = product.find('div', {'class': 'price'}).text.strip()
                    
                    return {
                        "Website": "Costco",
                        "Title": title,
                        "Price": price,
                        "PriceValidTill": ""
                    }
                
                # Selenium fallback
                product = driver.find_element(By.CSS_SELECTOR, 'div.product-tile')
                title = product.find_element(By.CSS_SELECTOR, 'span.description').text
                price = product.find_element(By.CSS_SELECTOR, 'div.price').text
                
                if self.debug_mode:
                    driver.save_screenshot('debug_product_found.png')
                
                return {
                    "Website": "Costco",
                    "Title": title.strip(),
                    "Price": price.strip(),
                    "PriceValidTill": ""
                }
                
            except Exception as e:
                log_error("CostcoBrowser", product_name, f"Attempt {attempt+1}: {str(e)}")
                self.rotate_proxy()
                time.sleep(DELAY * (attempt + 2))  # Exponential backoff
                
                if self.debug_mode:
                    driver.save_screenshot(f'debug_error_attempt_{attempt+1}.png')
                    print(f"Attempt {attempt+1} page source:", driver.page_source[:2000])
                
            finally:
                if driver:
                    driver.quit()
        
        return {"error": f"All {max_retries} browser attempts failed"}

    def rotate_proxy(self):
        """Rotate to a new proxy server"""
        self.current_proxy = get_random_proxy()
        log_error("Proxy", "Rotation", f"Switched to proxy: {self.current_proxy or 'None'}")