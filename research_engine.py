"""
research_engine.py - VideoReach AI Prospect Research Engine
Phase 4: VRA-008 - Web scraping and data enrichment

This module gathers prospect information from websites and enriches with additional data.
Uses real scraping, no fake data.

Requirements:
- pip install beautifulsoup4 playwright requests
- Playwright browsers: playwright install chromium
"""

import os
import sys
import json
import time
import re
from typing import Dict, List, Optional, Any
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
import asyncio
from concurrent.futures import ThreadPoolExecutor

# Fix Windows Unicode issues first
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Try to import Playwright for advanced scraping
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️ Playwright not available - using basic scraping only")

@dataclass
class CompanyResearch:
    """Structured company research data."""
    company_name: str
    website: str
    industry: str = "Unknown"
    company_size: str = "Unknown"
    tech_stack: List[str] = None
    description: str = ""
    social_links: Dict[str, str] = None
    contact_info: Dict[str, str] = None
    key_pages: Dict[str, str] = None
    meta_description: str = ""
    recent_updates: List[str] = None
    
    def __post_init__(self):
        if self.tech_stack is None:
            self.tech_stack = []
        if self.social_links is None:
            self.social_links = {}
        if self.contact_info is None:
            self.contact_info = {}
        if self.key_pages is None:
            self.key_pages = {}
        if self.recent_updates is None:
            self.recent_updates = []

class ResearchEngine:
    """Main research engine for prospect data gathering."""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.tech_patterns = self._load_tech_patterns()
    
    def _load_tech_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for detecting technology stack."""
        return {
            'wordpress': ['wp-content', 'wp-includes', 'wordpress'],
            'shopify': ['cdn.shopify.com', 'shopify', 'myshopify.com'],
            'react': ['react', '_next', 'React'],
            'angular': ['ng-version', 'angular'],
            'vue': ['vue', 'Vue.js'],
            'hubspot': ['hubspot', 'hs-scripts', 'hsforms'],
            'salesforce': ['salesforce', 'force.com'],
            'google_analytics': ['google-analytics', 'ga.js', 'gtag'],
            'stripe': ['stripe', 'stripe.com'],
            'intercom': ['intercom', 'intercom.io'],
            'zendesk': ['zendesk', 'zdassets'],
            'mailchimp': ['mailchimp', 'mc.js'],
            'aws': ['amazonaws.com', 'aws'],
            'cloudflare': ['cloudflare', 'cf-'],
        }
    
    def research_company(self, url: str) -> CompanyResearch:
        """
        Main research function - gathers all available data about a company.
        
        Args:
            url: Company website URL
            
        Returns:
            CompanyResearch object with all gathered data
        """
        print(f"🔍 Researching: {url}")
        
        # Normalize URL
        if not url.startswith(('http://', 'https://')):
            url = f'https://{url}'
        
        # Parse domain
        parsed = urlparse(url)
        domain = parsed.netloc
        
        # Initialize research object
        research = CompanyResearch(
            company_name=self._extract_company_name(domain),
            website=url
        )
        
        try:
            # Basic scraping with requests/BeautifulSoup
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract basic information
            research.meta_description = self._extract_meta_description(soup)
            research.tech_stack = self._detect_tech_stack(response.text, soup)
            research.social_links = self._extract_social_links(soup, url)
            research.contact_info = self._extract_contact_info(soup)
            research.key_pages = self._find_key_pages(soup, url)
            research.description = self._extract_description(soup)
            research.industry = self._infer_industry(soup, response.text)
            research.company_size = self._infer_company_size(soup)
            
            print(f"✅ Research complete for {research.company_name}")
            
        except requests.RequestException as e:
            print(f"❌ Failed to research {url}: {e}")
            research.description = f"Unable to access website: {str(e)}"
        
        return research
    
    def _extract_company_name(self, domain: str) -> str:
        """Extract company name from domain."""
        # Remove common TLDs and subdomains
        name = domain.replace('www.', '')
        name = name.split('.')[0]
        # Capitalize properly
        return name.replace('-', ' ').replace('_', ' ').title()
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta:
            return meta.get('content', '')
        return ''
    
    def _detect_tech_stack(self, html: str, soup: BeautifulSoup) -> List[str]:
        """Detect technology stack from HTML patterns."""
        detected = []
        
        # Check HTML content for patterns
        html_lower = html.lower()
        for tech, patterns in self.tech_patterns.items():
            for pattern in patterns:
                if pattern.lower() in html_lower:
                    detected.append(tech)
                    break
        
        # Check meta generators
        generator = soup.find('meta', attrs={'name': 'generator'})
        if generator:
            content = generator.get('content', '').lower()
            if 'wordpress' in content:
                detected.append('wordpress')
            elif 'drupal' in content:
                detected.append('drupal')
            elif 'joomla' in content:
                detected.append('joomla')
        
        # Check for specific script tags
        scripts = soup.find_all('script', src=True)
        for script in scripts:
            src = script.get('src', '').lower()
            if 'jquery' in src:
                detected.append('jquery')
            elif 'bootstrap' in src:
                detected.append('bootstrap')
            elif 'tailwind' in src:
                detected.append('tailwind')
        
        return list(set(detected))  # Remove duplicates
    
    def _extract_social_links(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """Extract social media links."""
        social = {}
        social_patterns = {
            'linkedin': ['linkedin.com/company', 'linkedin.com/in'],
            'twitter': ['twitter.com/', 'x.com/'],
            'facebook': ['facebook.com/'],
            'instagram': ['instagram.com/'],
            'youtube': ['youtube.com/'],
        }
        
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href'].lower()
            for platform, patterns in social_patterns.items():
                for pattern in patterns:
                    if pattern in href:
                        social[platform] = link['href']
                        break
        
        return social
    
    def _extract_contact_info(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract contact information."""
        contact = {}
        
        # Look for email
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        emails = re.findall(email_pattern, str(soup))
        if emails:
            # Filter out common non-contact emails
            for email in emails:
                if not any(x in email.lower() for x in ['example', 'domain', 'email']):
                    contact['email'] = email
                    break
        
        # Look for phone
        phone_pattern = r'[\+]?[(]?[0-9]{1,3}[)]?[-\s\.]?[(]?[0-9]{1,3}[)]?[-\s\.]?[0-9]{3,5}[-\s\.]?[0-9]{3,5}'
        phones = re.findall(phone_pattern, str(soup))
        if phones:
            contact['phone'] = phones[0]
        
        # Look for address
        address_tags = soup.find_all(['address', 'div'], class_=re.compile('address|location', re.I))
        if address_tags:
            contact['address'] = address_tags[0].get_text(strip=True)[:200]
        
        return contact
    
    def _find_key_pages(self, soup: BeautifulSoup, base_url: str) -> Dict[str, str]:
        """Find key pages like about, contact, pricing."""
        pages = {}
        key_words = ['about', 'contact', 'pricing', 'products', 'services', 'team', 'careers', 'blog']
        
        links = soup.find_all('a', href=True)
        for link in links:
            href = link['href']
            text = link.get_text(strip=True).lower()
            
            for key in key_words:
                if key in text or key in href.lower():
                    full_url = urljoin(base_url, href)
                    pages[key] = full_url
                    break
        
        return pages
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract company description from various sources."""
        # Try to find about section
        about_sections = soup.find_all(['div', 'section'], class_=re.compile('about|description', re.I))
        if about_sections:
            text = about_sections[0].get_text(strip=True)
            return text[:500]  # Limit length
        
        # Try hero section
        hero = soup.find(['div', 'section'], class_=re.compile('hero|banner|header', re.I))
        if hero:
            text = hero.get_text(strip=True)
            return text[:500]
        
        # Fallback to first paragraph
        paragraphs = soup.find_all('p')
        for p in paragraphs:
            text = p.get_text(strip=True)
            if len(text) > 50:  # Skip short paragraphs
                return text[:500]
        
        return "No description found"
    
    def _infer_industry(self, soup: BeautifulSoup, html: str) -> str:
        """Infer industry from content."""
        content = str(soup).lower()
        
        industry_keywords = {
            'Technology': ['software', 'saas', 'cloud', 'api', 'platform', 'tech'],
            'E-commerce': ['shop', 'store', 'buy', 'cart', 'product', 'ecommerce'],
            'Healthcare': ['health', 'medical', 'clinic', 'patient', 'doctor', 'hospital'],
            'Finance': ['finance', 'bank', 'investment', 'trading', 'payment', 'fintech'],
            'Education': ['education', 'learning', 'course', 'training', 'school', 'university'],
            'Marketing': ['marketing', 'advertising', 'seo', 'content', 'digital', 'agency'],
            'Real Estate': ['real estate', 'property', 'realty', 'housing', 'apartment'],
            'Legal': ['law', 'legal', 'attorney', 'lawyer', 'firm'],
            'Consulting': ['consulting', 'advisory', 'strategy', 'management'],
        }
        
        scores = {}
        for industry, keywords in industry_keywords.items():
            score = sum(1 for keyword in keywords if keyword in content)
            if score > 0:
                scores[industry] = score
        
        if scores:
            return max(scores, key=scores.get)
        
        return "General Business"
    
    def _infer_company_size(self, soup: BeautifulSoup) -> str:
        """Infer company size from content."""
        content = str(soup).lower()
        
        # Look for employee count mentions
        employee_patterns = [
            r'(\d+)\+?\s*employees?',
            r'team of\s*(\d+)',
            r'(\d+)\s*people',
        ]
        
        for pattern in employee_patterns:
            matches = re.findall(pattern, content)
            if matches:
                try:
                    count = int(matches[0])
                    if count < 10:
                        return "1-10 employees"
                    elif count < 50:
                        return "11-50 employees"
                    elif count < 200:
                        return "51-200 employees"
                    elif count < 1000:
                        return "201-1000 employees"
                    else:
                        return "1000+ employees"
                except:
                    pass
        
        # Look for size indicators
        if any(word in content for word in ['enterprise', 'fortune 500', 'global']):
            return "1000+ employees"
        elif any(word in content for word in ['startup', 'small team', 'boutique']):
            return "1-10 employees"
        elif any(word in content for word in ['growing', 'mid-size', 'midsize']):
            return "51-200 employees"
        
        return "Unknown"

async def scrape_with_playwright(url: str) -> Optional[Dict[str, Any]]:
    """
    Advanced scraping using Playwright for JavaScript-heavy sites.
    Returns additional data that requires browser rendering.
    """
    if not PLAYWRIGHT_AVAILABLE:
        return None
    
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Set a reasonable viewport
            await page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Navigate to the page
            await page.goto(url, wait_until='networkidle')
            
            # Wait for content to load
            await page.wait_for_timeout(2000)
            
            # Extract additional data
            data = {}
            
            # Get rendered HTML
            data['html'] = await page.content()
            
            # Take screenshot for later analysis
            # data['screenshot'] = await page.screenshot()
            
            # Get all text content
            data['text'] = await page.inner_text('body')
            
            # Check for specific elements
            data['has_chat'] = await page.locator('[class*="chat"], [id*="chat"]').count() > 0
            data['has_booking'] = await page.locator('[class*="calendar"], [class*="booking"], [class*="schedule"]').count() > 0
            data['has_video'] = await page.locator('video, iframe[src*="youtube"], iframe[src*="vimeo"]').count() > 0
            
            await browser.close()
            
            return data
            
    except Exception as e:
        print(f"❌ Playwright scraping failed: {e}")
        return None

def enrich_with_external_apis(research: CompanyResearch) -> CompanyResearch:
    """
    Enrich research with external APIs if available.
    Currently placeholder - would integrate with Clearbit, Apollo, etc.
    """
    # This would connect to real enrichment APIs
    # For now, we're using only public scraping
    
    # Example structure for future API integration:
    # if CLEARBIT_API_KEY:
    #     clearbit_data = clearbit.enrich(research.website)
    #     research.company_size = clearbit_data.get('employees')
    #     research.industry = clearbit_data.get('industry')
    
    return research

def research_prospect(url: str) -> Dict[str, Any]:
    """
    Main function to research a prospect.
    
    Args:
        url: Company website URL
        
    Returns:
        Dictionary with all research data
    """
    engine = ResearchEngine()
    research = engine.research_company(url)
    
    # Enrich with external APIs if available
    research = enrich_with_external_apis(research)
    
    # Convert to dictionary
    return asdict(research)

def main():
    """Test the research engine."""
    test_urls = [
        'https://www.ycombinator.com',
        'https://www.stripe.com',
        'https://www.notion.so',
    ]
    
    for url in test_urls:
        print("\n" + "=" * 60)
        print(f"Researching: {url}")
        print("=" * 60)
        
        data = research_prospect(url)
        
        print(f"\n📊 Research Results:")
        print(f"Company: {data['company_name']}")
        print(f"Industry: {data['industry']}")
        print(f"Size: {data['company_size']}")
        print(f"Tech Stack: {', '.join(data['tech_stack']) if data['tech_stack'] else 'None detected'}")
        print(f"Social: {', '.join(data['social_links'].keys()) if data['social_links'] else 'None found'}")
        print(f"Description: {data['description'][:200]}...")

if __name__ == '__main__':
    main()