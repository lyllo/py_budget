import os
import sys

# Add src to path
sys.path.append(os.path.abspath('src'))

from extract import btg_mobile_scraper

if __name__ == '__main__':
    print("🚀 Starting Live Scraper...")
    PATH_TO_INPUT = os.path.join('in', 'btg_mobile.txt')
    # Default to dynamic offset (latest non-installment transaction minus 1 day)
    btg_mobile_scraper.init(PATH_TO_INPUT)
    print("✅ Live Scraper Finished.")
