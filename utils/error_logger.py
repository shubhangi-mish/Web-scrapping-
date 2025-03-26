import logging
from datetime import datetime

logging.basicConfig(
    filename='scraping_errors.log',
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def log_error(retailer, product, error):
    logging.error(f"{retailer} | {product} | {error}")