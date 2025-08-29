import requests
from bs4 import BeautifulSoup
import time
import random
import re
from urllib.parse import urljoin

class AmazonTracker:
    def __init__(self):
        self.session = requests.Session()
        
        # Set up headers to mimic a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'DNT': '1',
            'Upgrade-Insecure-Requests': '1',
        }
        
        self.session.headers.update(self.headers)
    
    def get_product_info(self, asin):
        """
        Get product information from Amazon by ASIN
        Returns dict with title, price, availability, asin, error
        """
        try:
            # Construct Amazon URL
            url = f"https://www.amazon.com/dp/{asin}"
            
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            # Make request
            response = self.session.get(url, headers=self.headers, timeout=10)
            
            if response.status_code != 200:
                return {
                    'title': '',
                    'price': '',
                    'availability': '',
                    'asin': asin,
                    'error': f'HTTP {response.status_code}: Unable to access product page'
                }
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract product information
            product_info = {
                'asin': asin,
                'title': self._extract_title(soup),
                'price': self._extract_price(soup),
                'availability': self._extract_availability(soup),
                'error': None
            }
            
            # Check if we got blocked or page is invalid
            if not product_info['title'] and "Robot Check" in response.text:
                return {
                    'title': '',
                    'price': '',
                    'availability': '',
                    'asin': asin,
                    'error': 'Blocked by Amazon. Please try again later.'
                }
            
            if not product_info['title']:
                return {
                    'title': '',
                    'price': '',
                    'availability': '',
                    'asin': asin,
                    'error': 'Product not found or ASIN invalid'
                }
            
            return product_info
            
        except requests.exceptions.Timeout:
            return {
                'title': '',
                'price': '',
                'availability': '',
                'asin': asin,
                'error': 'Request timeout. Amazon may be slow or blocking requests.'
            }
        except requests.exceptions.RequestException as e:
            return {
                'title': '',
                'price': '',
                'availability': '',
                'asin': asin,
                'error': f'Network error: {str(e)}'
            }
        except Exception as e:
            return {
                'title': '',
                'price': '',
                'availability': '',
                'asin': asin,
                'error': f'Unexpected error: {str(e)}'
            }
    
    def _extract_title(self, soup):
        """Extract product title from soup"""
        title_selectors = [
            '#productTitle',
            '.product-title',
            'h1.a-size-large',
            'h1[data-automation-id="product-title"]',
            '.a-size-large.product-title-word-break'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        
        return ''
    
    def _extract_price(self, soup):
        """Extract product price from soup"""
        price_selectors = [
            '.a-price.a-text-price.a-size-medium.apexPriceToPay .a-offscreen',
            '.a-price-range .a-offscreen',
            '.a-price .a-offscreen',
            '#priceblock_dealprice',
            '#priceblock_ourprice',
            '.a-price-whole',
            '.a-price.a-text-price',
            '.a-price-display'
        ]
        
        for selector in price_selectors:
            element = soup.select_one(selector)
            if element:
                price_text = element.get_text(strip=True)
                if price_text and '$' in price_text:
                    return price_text
        
        # Try to find any element with price-like text
        price_pattern = r'\$[\d,]+\.?\d*'
        price_elements = soup.find_all(text=re.compile(price_pattern))
        if price_elements:
            for price_text in price_elements:
                match = re.search(price_pattern, price_text)
                if match:
                    return match.group()
        
        return 'Price not available'
    
    def _extract_availability(self, soup):
        """Extract availability information from soup"""
        # Look for availability indicators
        availability_selectors = [
            '#availability .a-size-medium',
            '#availability span',
            '.a-size-medium.a-color-success',
            '.a-size-medium.a-color-price',
            '#availability .a-color-success',
            '#availability .a-color-state',
            '.a-spacing-micro .a-color-success',
            '.a-spacing-micro .a-color-price'
        ]
        
        for selector in availability_selectors:
            element = soup.select_one(selector)
            if element:
                availability_text = element.get_text(strip=True)
                if availability_text and len(availability_text) > 0:
                    return availability_text
        
        # Check for common availability indicators
        availability_keywords = [
            'In Stock',
            'out of stock',
            'Currently unavailable',
            'left in stock',
            'Only.*left',
            'Available',
            'Temporarily out of stock'
        ]
        
        page_text = soup.get_text()
        for keyword in availability_keywords:
            pattern = re.compile(keyword, re.IGNORECASE)
            match = pattern.search(page_text)
            if match:
                # Try to get more context around the match
                start = max(0, match.start() - 20)
                end = min(len(page_text), match.end() + 20)
                context = page_text[start:end].strip()
                
                # Clean up the context
                lines = context.split('\n')
                for line in lines:
                    line = line.strip()
                    if keyword.lower() in line.lower() and len(line) < 100:
                        return line
                
                return match.group()
        
        return 'Availability unknown'
