import os
import sys

# Add src to path
sys.path.append(os.path.abspath('src'))

from extract import btg_mobile_scraper

if __name__ == '__main__':
    print("🚀 Starting Live Scraper (Deep History Mode)...")
    PATH_TO_INPUT = os.path.join('in', 'btg_mobile.txt')
    # Force target date to 15/Dez to capture the missing 20/Dez Pixs
    btg_mobile_scraper.init(PATH_TO_INPUT, force_until_date="15/Dez")
    print("✅ Live Scraper Finished.")
