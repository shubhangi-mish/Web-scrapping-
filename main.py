import json
import time
import random
from config import DELAY, RETRIES
from scrapers.amazon_scraper import scrape_amazon
from scrapers.bestbuy_scraper import scrape_bestbuy
from scrapers.lg_scraper import scrape_lg_canada  # Added LG Canada scraper
from utils.error_logger import log_error

# ... (keep your existing products list) ...
products = [
    {"name": "LG 50\" UHD 4K Smart LED TV - 50UT7570PUB"},
]

def main():
    output = []
    success_count = 0
    failure_count = 0

    for product in products:
        name = product["name"]
        brand = name.split()[0]
        
        print(f"\nProcessing: {name}")
        
        # Initialize product entry
        product_entry = {
            "Brand": brand,
            "Product": []
        }
        
        # List of all scraper functions to try
        scrapers = [
            ("Best Buy", scrape_bestbuy),
            ("Amazon", scrape_amazon),
            ("LG Canada", scrape_lg_canada)  # Added LG Canada to scrapers list
        ]
        
        for retailer_name, scraper_func in scrapers:
            print(f"  - Trying {retailer_name}...")
            result = None
            for attempt in range(RETRIES):
                try:
                    result = scraper_func(name)
                    if not result.get("error"):
                        product_entry["Product"].append(result)
                        success_count += 1
                        break
                    else:
                        print(f"    Attempt {attempt + 1} failed: {result.get('error')}")
                except Exception as e:
                    log_error(f"Main-{retailer_name}", name, str(e))
                time.sleep(DELAY * (attempt + 1))
        
        # Only add if we got at least one result
        if product_entry["Product"]:
            output.append(product_entry)
        else:
            failure_count += 1
            print(f"  ⚠️ Failed to get any data for {name}")
        
        # Random delay between products
        time.sleep(DELAY + random.uniform(1, 3))
    
    # Save results
    with open("outputs/tv_prices.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nScraping complete! Success: {success_count}, Failures: {failure_count}")
    print("Results saved to outputs/tv_prices.json")

if __name__ == "__main__":
    main()
