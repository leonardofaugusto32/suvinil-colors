import requests
from bs4 import BeautifulSoup
import pandas as pd
from tqdm import tqdm
import time
import random
import json
from typing import Dict, List, Optional, Tuple
import re
import logging
from datetime import datetime
import platform
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'suvinil_crawler_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

class SuvinilColorCrawler:
    def __init__(self):
        self.base_url = "https://www.suvinil.com.br"
        self.colors_url = f"{self.base_url}/cores/leque-cores-digital"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/115.0'
        })
        self.colors = []
        self.setup_selenium()

    def setup_selenium(self):
        """Setup Selenium WebDriver with Firefox."""
        try:
            firefox_options = Options()
            firefox_options.add_argument('--headless')
            
            service = Service(GeckoDriverManager().install())
            self.driver = webdriver.Firefox(service=service, options=firefox_options)
            self.driver.implicitly_wait(10)
            logging.info("Firefox WebDriver initialized successfully")
        except Exception as e:
            logging.error(f"Failed to initialize Firefox WebDriver: {str(e)}")
            raise

    def wait_for_element(self, by: By, selector: str, timeout: int = 10) -> Optional[webdriver.remote.webelement.WebElement]:
        """Wait for an element to be present and return it."""
        try:
            element = WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((by, selector))
            )
            return element
        except TimeoutException:
            logging.warning(f"Timeout waiting for element: {selector}")
            return None

    def get_color_categories(self) -> List[str]:
        """Get all color category links."""
        self.driver.get(self.colors_url)
        time.sleep(5)  # Wait for the page to load
        
        try:
            # First, try to find and click the "Todas" button if it exists
            todas_button = self.wait_for_element(By.XPATH, "//button[contains(text(), 'Todas')]")
            if todas_button:
                todas_button.click()
                time.sleep(2)
            
            # Look for color category links
            categories = self.driver.find_elements(By.CSS_SELECTOR, 'a[href*="/cores/"]')
            valid_categories = []
            for cat in categories:
                href = cat.get_attribute('href')
                if href and '/cores/' in href and 'leque-cores-digital' not in href:
                    valid_categories.append(href)
            
            return list(set(valid_categories))  # Remove duplicates
        except NoSuchElementException as e:
            logging.error(f"Could not find color categories: {str(e)}")
            return []

    def extract_color_info(self, color_element) -> Dict:
        """Extract color information from a color element."""
        try:
            # Try different selectors for color information
            name = None
            code = None
            color_link = None
            rgb = None
            
            try:
                name = color_element.find_element(By.CSS_SELECTOR, 'h3, .color-title, .name').text.strip()
            except:
                try:
                    name = color_element.find_element(By.CSS_SELECTOR, '[class*="name"], [class*="title"]').text.strip()
                except:
                    logging.warning("Could not find color name")
            
            try:
                code = color_element.find_element(By.CSS_SELECTOR, '[class*="code"]').text.strip()
            except:
                logging.warning("Could not find color code")
            
            try:
                link_element = color_element.find_element(By.CSS_SELECTOR, 'a')
                color_link = link_element.get_attribute('href')
            except:
                logging.warning("Could not find color link")
                return None
            
            if color_link:
                # Visit the color detail page to get RGB values
                self.driver.execute_script('window.open("","_blank");')
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.get(color_link)
                time.sleep(2)
                
                try:
                    # Try different methods to find RGB value
                    rgb_element = self.wait_for_element(By.CSS_SELECTOR, '[class*="rgb"], [class*="RGB"], [class*="color-value"]')
                    if rgb_element:
                        rgb = rgb_element.text.strip()
                    else:
                        # Try to find RGB in any element containing 'rgb(' string
                        elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'rgb(')]")
                        for elem in elements:
                            text = elem.text
                            rgb_match = re.search(r'rgb\((.*?)\)', text)
                            if rgb_match:
                                rgb = rgb_match.group(0)
                                break
                except Exception as e:
                    logging.warning(f"Could not find RGB value: {str(e)}")
                
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
            
            return {
                'name': name,
                'code': code,
                'rgb': rgb,
                'url': color_link
            }
        except Exception as e:
            logging.error(f"Error extracting color info: {str(e)}")
            return None

    def crawl_colors(self):
        """Main method to crawl all colors."""
        logging.info("Starting color crawling process...")
        
        try:
            # Get all color categories
            categories = self.get_color_categories()
            logging.info(f"Found {len(categories)} color categories")
            
            for category_url in categories:
                logging.info(f"Processing category: {category_url}")
                self.driver.get(category_url)
                time.sleep(3)  # Wait for colors to load
                
                # Scroll to load all colors
                last_height = self.driver.execute_script("return document.body.scrollHeight")
                while True:
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    new_height = self.driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                    last_height = new_height
                
                # Get all color elements
                color_elements = self.driver.find_elements(By.CSS_SELECTOR, '[class*="color-item"], [class*="colorItem"], .color')
                logging.info(f"Found {len(color_elements)} colors in category")
                
                for element in tqdm(color_elements, desc="Processing colors"):
                    color_info = self.extract_color_info(element)
                    if color_info:
                        self.colors.append(color_info)
                        logging.info(f"Processed color: {color_info['name']} ({color_info['code']})")
                
            # Save results
            self.save_results()
            
        except Exception as e:
            logging.error(f"Error during crawling: {str(e)}")
        finally:
            self.driver.quit()

    def save_results(self):
        """Save results to JSON and CSV files."""
        if not self.colors:
            logging.warning("No colors to save")
            return
            
        # Save to JSON
        with open('suvinil_colors.json', 'w', encoding='utf-8') as f:
            json.dump(self.colors, f, ensure_ascii=False, indent=2)
            
        # Save to CSV
        df = pd.DataFrame(self.colors)
        df.to_csv('suvinil_colors.csv', index=False, encoding='utf-8')
        
        logging.info(f"Finished processing {len(self.colors)} colors")
        logging.info("Results saved to suvinil_colors.json and suvinil_colors.csv")

if __name__ == "__main__":
    crawler = SuvinilColorCrawler()
    crawler.crawl_colors() 