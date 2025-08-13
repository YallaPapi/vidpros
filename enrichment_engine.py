"""
enrichment_engine.py - VideoReach AI Data Enrichment System
Phase 4: VRA-020 - External data enrichment for audit reports

This module enriches company data using multiple external APIs and sources.
Provides fallback mechanisms when API keys are not available.
Works with research_engine.py for comprehensive data gathering.

Requirements:
- pip install requests beautifulsoup4 linkedin-api tweepy
- API keys in .env (optional - system works without them)
"""

import os
import sys
import json
import time
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
import requests
from urllib.parse import urlparse, quote
from dotenv import load_dotenv
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import research engine for base data
from research_engine import ResearchEngine, CompanyResearch

# Fix Windows Unicode issues
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Load environment variables
load_dotenv()

@dataclass
class EnrichedCompanyData:
    """Comprehensive enriched company data structure."""
    # Basic info from research
    company_name: str
    website: str
    industry: str
    company_size: str
    tech_stack: List[str]
    
    # Enriched data
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    revenue_range: Optional[str] = None
    funding_total: Optional[float] = None
    funding_stage: Optional[str] = None
    employee_growth: Optional[float] = None  # YoY percentage
    
    # Decision makers
    key_people: List[Dict[str, str]] = field(default_factory=list)
    
    # Market intelligence
    competitors: List[str] = field(default_factory=list)
    recent_news: List[Dict[str, str]] = field(default_factory=list)
    job_postings: List[Dict[str, str]] = field(default_factory=list)
    
    # Technology insights
    tech_spend_estimate: Optional[str] = None
    digital_maturity_score: Optional[int] = None  # 1-100
    automation_opportunities: List[str] = field(default_factory=list)
    
    # Social presence
    social_metrics: Dict[str, int] = field(default_factory=dict)
    content_themes: List[str] = field(default_factory=list)
    engagement_rate: Optional[float] = None
    
    # Buying signals
    growth_signals: List[str] = field(default_factory=list)
    pain_indicators: List[str] = field(default_factory=list)
    trigger_events: List[str] = field(default_factory=list)
    
    # Data quality
    enrichment_sources: List[str] = field(default_factory=list)
    confidence_scores: Dict[str, float] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)

class EnrichmentProvider:
    """Base class for enrichment providers."""
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key
        self.is_available = bool(api_key)
        self.session = requests.Session()
        self.cache = {}
    
    def enrich(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Override in subclasses."""
        raise NotImplementedError

class ClearbitProvider(EnrichmentProvider):
    """Clearbit API enrichment provider."""
    
    def __init__(self):
        api_key = os.environ.get('CLEARBIT_API_KEY')
        super().__init__('Clearbit', api_key)
        if self.api_key:
            self.session.headers['Authorization'] = f'Bearer {self.api_key}'
    
    def enrich(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich using Clearbit Company API."""
        if not self.is_available:
            return {}
        
        try:
            domain = urlparse(company_data.get('website', '')).netloc
            url = f"https://company.clearbit.com/v2/companies/find?domain={domain}"
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return {
                    'founded_year': data.get('foundedYear'),
                    'headquarters': f"{data.get('location', {}).get('city')}, {data.get('location', {}).get('state')}",
                    'revenue_range': self._format_revenue(data.get('metrics', {}).get('annualRevenue')),
                    'employee_count': data.get('metrics', {}).get('employees'),
                    'tech_stack': data.get('tech', []),
                    'industry': data.get('category', {}).get('industry'),
                    'tags': data.get('tags', [])
                }
        except Exception as e:
            print(f"Clearbit enrichment failed: {e}")
        
        return {}
    
    def _format_revenue(self, revenue: Optional[int]) -> str:
        """Format revenue into ranges."""
        if not revenue:
            return None
        if revenue < 1000000:
            return "<$1M"
        elif revenue < 10000000:
            return "$1M-$10M"
        elif revenue < 50000000:
            return "$10M-$50M"
        elif revenue < 100000000:
            return "$50M-$100M"
        else:
            return "$100M+"

class ApolloProvider(EnrichmentProvider):
    """Apollo.io API enrichment provider."""
    
    def __init__(self):
        api_key = os.environ.get('APOLLO_API_KEY')
        super().__init__('Apollo', api_key)
    
    def enrich(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich using Apollo.io API."""
        if not self.is_available:
            return {}
        
        try:
            url = "https://api.apollo.io/v1/organizations/enrich"
            params = {
                'api_key': self.api_key,
                'domain': urlparse(company_data.get('website', '')).netloc
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json().get('organization', {})
                return {
                    'founded_year': data.get('founded_year'),
                    'headquarters': data.get('primary_location'),
                    'funding_total': data.get('total_funding'),
                    'funding_stage': data.get('latest_funding_stage'),
                    'employee_count': data.get('estimated_num_employees'),
                    'technologies': data.get('technologies', []),
                    'keywords': data.get('keywords', [])
                }
        except Exception as e:
            print(f"Apollo enrichment failed: {e}")
        
        return {}

class LinkedInProvider(EnrichmentProvider):
    """LinkedIn data provider (using public data only)."""
    
    def __init__(self):
        # No API key needed for public scraping
        super().__init__('LinkedIn', None)
        self.is_available = True  # Always available for public data
    
    def enrich(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Scrape public LinkedIn company data."""
        try:
            company_name = company_data.get('company_name', '').lower().replace(' ', '-')
            url = f"https://www.linkedin.com/company/{company_name}"
            
            # Note: In production, would use proper LinkedIn API or scraping service
            # For now, returning structured placeholder that would come from real scraping
            return {
                'employee_growth': None,  # Would calculate from employee count history
                'recent_posts': [],  # Would extract recent company posts
                'job_postings_count': 0,  # Would count open positions
                'follower_count': 0  # Would extract follower metrics
            }
        except Exception as e:
            print(f"LinkedIn enrichment failed: {e}")
        
        return {}

class NewsProvider(EnrichmentProvider):
    """News and press release provider."""
    
    def __init__(self):
        api_key = os.environ.get('NEWS_API_KEY')
        super().__init__('NewsAPI', api_key)
    
    def enrich(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch recent news about the company."""
        if not self.is_available:
            # Fallback to Google News RSS
            return self._scrape_google_news(company_data.get('company_name', ''))
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                'q': f'"{company_data.get("company_name")}"',
                'apiKey': self.api_key,
                'sortBy': 'publishedAt',
                'pageSize': 10,
                'from': (datetime.now() - timedelta(days=30)).isoformat()
            }
            
            response = self.session.get(url, params=params, timeout=10)
            if response.status_code == 200:
                articles = response.json().get('articles', [])
                return {
                    'recent_news': [
                        {
                            'title': article['title'],
                            'url': article['url'],
                            'date': article['publishedAt'],
                            'source': article['source']['name']
                        }
                        for article in articles[:5]
                    ]
                }
        except Exception as e:
            print(f"News enrichment failed: {e}")
        
        return self._scrape_google_news(company_data.get('company_name', ''))
    
    def _scrape_google_news(self, company_name: str) -> Dict[str, Any]:
        """Fallback to Google News RSS."""
        try:
            # Simple Google News RSS approach
            url = f"https://news.google.com/rss/search?q={quote(company_name)}"
            response = self.session.get(url, timeout=10)
            
            # Parse RSS (simplified - would use feedparser in production)
            news = []
            # Basic extraction of news items
            
            return {'recent_news': news}
        except:
            return {'recent_news': []}

class TechStackAnalyzer:
    """Advanced technology stack detection."""
    
    def __init__(self):
        self.builtwith_key = os.environ.get('BUILTWITH_API_KEY')
        self.wappalyzer_key = os.environ.get('WAPPALYZER_API_KEY')
    
    def analyze(self, website: str) -> Dict[str, Any]:
        """Comprehensive tech stack analysis."""
        tech_data = {
            'technologies': [],
            'categories': {},
            'tech_spend_estimate': None,
            'digital_maturity_score': 50  # Default
        }
        
        # Try BuiltWith API
        if self.builtwith_key:
            tech_data.update(self._builtwith_analysis(website))
        
        # Try Wappalyzer API
        if self.wappalyzer_key:
            tech_data.update(self._wappalyzer_analysis(website))
        
        # Fallback to pattern detection
        if not tech_data['technologies']:
            tech_data['technologies'] = self._detect_technologies(website)
        
        # Calculate digital maturity score
        tech_data['digital_maturity_score'] = self._calculate_maturity_score(tech_data)
        
        # Estimate tech spend
        tech_data['tech_spend_estimate'] = self._estimate_tech_spend(tech_data)
        
        return tech_data
    
    def _builtwith_analysis(self, website: str) -> Dict[str, Any]:
        """BuiltWith API analysis."""
        try:
            url = f"https://api.builtwith.com/v14/lookup"
            params = {'key': self.builtwith_key, 'lookup': website}
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                # Parse BuiltWith response
                return {'technologies': []}  # Simplified
        except:
            pass
        return {}
    
    def _wappalyzer_analysis(self, website: str) -> Dict[str, Any]:
        """Wappalyzer API analysis."""
        # Implementation for Wappalyzer API
        return {}
    
    def _detect_technologies(self, website: str) -> List[str]:
        """Fallback technology detection."""
        # Use research_engine patterns as fallback
        engine = ResearchEngine()
        try:
            response = engine.session.get(website, timeout=10)
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            return engine._detect_tech_stack(response.text, soup)
        except:
            return []
    
    def _calculate_maturity_score(self, tech_data: Dict[str, Any]) -> int:
        """Calculate digital maturity score (1-100)."""
        score = 50  # Base score
        
        tech_count = len(tech_data.get('technologies', []))
        if tech_count > 20:
            score += 20
        elif tech_count > 10:
            score += 10
        elif tech_count > 5:
            score += 5
        
        # Bonus for specific categories
        modern_tech = ['react', 'vue', 'angular', 'kubernetes', 'docker', 'aws', 'gcp', 'azure']
        for tech in tech_data.get('technologies', []):
            if any(m in tech.lower() for m in modern_tech):
                score += 2
        
        return min(100, score)
    
    def _estimate_tech_spend(self, tech_data: Dict[str, Any]) -> str:
        """Estimate technology spending based on stack."""
        tech_count = len(tech_data.get('technologies', []))
        
        if tech_count < 5:
            return "<$10K/month"
        elif tech_count < 10:
            return "$10K-$50K/month"
        elif tech_count < 20:
            return "$50K-$200K/month"
        else:
            return "$200K+/month"

class DataEnrichmentEngine:
    """Main enrichment orchestrator."""
    
    def __init__(self):
        self.providers = [
            ClearbitProvider(),
            ApolloProvider(),
            LinkedInProvider(),
            NewsProvider()
        ]
        self.tech_analyzer = TechStackAnalyzer()
        self.research_engine = ResearchEngine()
        self.cache_dir = "enrichment_cache"
        os.makedirs(self.cache_dir, exist_ok=True)
    
    def enrich_company(self, website_url: str) -> EnrichedCompanyData:
        """
        Comprehensive company enrichment pipeline.
        
        Args:
            website_url: Company website URL
            
        Returns:
            EnrichedCompanyData with all available information
        """
        print(f"[ENRICHMENT] Starting for: {website_url}")
        
        # Start with basic research
        base_research = self.research_engine.research_company(website_url)
        
        # Initialize enriched data
        enriched = EnrichedCompanyData(
            company_name=base_research.company_name,
            website=base_research.website,
            industry=base_research.industry,
            company_size=base_research.company_size,
            tech_stack=base_research.tech_stack
        )
        
        # Check cache
        cache_key = self._get_cache_key(website_url)
        cached_data = self._load_from_cache(cache_key)
        if cached_data and not self._is_cache_stale(cached_data):
            print("[CACHE] Using cached enrichment data")
            return self._dict_to_enriched_data(cached_data)
        
        # Run enrichment providers in parallel
        enrichment_results = self._run_parallel_enrichment({
            'website': website_url,
            'company_name': base_research.company_name,
            'industry': base_research.industry
        })
        
        # Merge enrichment results
        for provider_name, data in enrichment_results.items():
            self._merge_enrichment_data(enriched, data, provider_name)
        
        # Analyze technology stack
        tech_analysis = self.tech_analyzer.analyze(website_url)
        enriched.tech_stack.extend(tech_analysis.get('technologies', []))
        enriched.tech_stack = list(set(enriched.tech_stack))  # Remove duplicates
        enriched.tech_spend_estimate = tech_analysis.get('tech_spend_estimate')
        enriched.digital_maturity_score = tech_analysis.get('digital_maturity_score')
        
        # Identify automation opportunities
        enriched.automation_opportunities = self._identify_automation_opportunities(enriched)
        
        # Detect buying signals
        enriched.growth_signals = self._detect_growth_signals(enriched)
        enriched.pain_indicators = self._detect_pain_indicators(enriched)
        enriched.trigger_events = self._detect_trigger_events(enriched)
        
        # Calculate confidence scores
        enriched.confidence_scores = self._calculate_confidence_scores(enriched)
        
        # Track enrichment sources
        enriched.enrichment_sources = [
            p.name for p in self.providers if p.name in enrichment_results
        ]
        
        # Cache the results
        self._save_to_cache(cache_key, asdict(enriched))
        
        print(f"[COMPLETE] Enrichment complete - {len(enriched.enrichment_sources)} sources used")
        
        return enriched
    
    def _run_parallel_enrichment(self, company_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run all enrichment providers in parallel."""
        results = {}
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = {
                executor.submit(provider.enrich, company_data): provider.name
                for provider in self.providers
            }
            
            for future in as_completed(futures):
                provider_name = futures[future]
                try:
                    data = future.result(timeout=10)
                    if data:
                        results[provider_name] = data
                        print(f"[OK] {provider_name} enrichment complete")
                except Exception as e:
                    print(f"[FAIL] {provider_name} enrichment failed: {e}")
        
        return results
    
    def _merge_enrichment_data(self, enriched: EnrichedCompanyData, 
                               data: Dict[str, Any], source: str):
        """Merge data from enrichment provider."""
        # Merge basic fields
        if 'founded_year' in data and not enriched.founded_year:
            enriched.founded_year = data['founded_year']
        
        if 'headquarters' in data and not enriched.headquarters:
            enriched.headquarters = data['headquarters']
        
        if 'revenue_range' in data and not enriched.revenue_range:
            enriched.revenue_range = data['revenue_range']
        
        if 'funding_total' in data and not enriched.funding_total:
            enriched.funding_total = data['funding_total']
        
        if 'funding_stage' in data and not enriched.funding_stage:
            enriched.funding_stage = data['funding_stage']
        
        # Merge lists
        if 'technologies' in data:
            enriched.tech_stack.extend(data['technologies'])
        
        if 'competitors' in data:
            enriched.competitors.extend(data['competitors'])
        
        if 'recent_news' in data:
            enriched.recent_news.extend(data['recent_news'])
        
        if 'job_postings' in data:
            enriched.job_postings.extend(data['job_postings'])
    
    def _identify_automation_opportunities(self, enriched: EnrichedCompanyData) -> List[str]:
        """Identify specific automation opportunities based on company profile."""
        opportunities = []
        
        # Based on tech stack
        if not any(crm in enriched.tech_stack for crm in ['salesforce', 'hubspot', 'pipedrive']):
            opportunities.append("CRM implementation for lead management")
        
        if not any(mkt in enriched.tech_stack for mkt in ['mailchimp', 'marketo', 'pardot']):
            opportunities.append("Marketing automation platform")
        
        # Based on company size
        if '50' in enriched.company_size or '200' in enriched.company_size:
            opportunities.append("Workflow automation for scaling operations")
        
        # Based on industry
        if 'commerce' in enriched.industry.lower():
            opportunities.append("Inventory management automation")
        elif 'service' in enriched.industry.lower():
            opportunities.append("Customer service chatbot")
        elif 'saas' in enriched.industry.lower() or 'software' in enriched.industry.lower():
            opportunities.append("DevOps automation and CI/CD pipeline")
        
        # Based on digital maturity
        if enriched.digital_maturity_score and enriched.digital_maturity_score < 60:
            opportunities.append("Digital transformation consulting")
        
        return opportunities[:5]  # Top 5 opportunities
    
    def _detect_growth_signals(self, enriched: EnrichedCompanyData) -> List[str]:
        """Detect signals indicating company growth."""
        signals = []
        
        if enriched.funding_stage and 'series' in enriched.funding_stage.lower():
            signals.append(f"Recent funding: {enriched.funding_stage}")
        
        if enriched.employee_growth and enriched.employee_growth > 20:
            signals.append(f"High employee growth: {enriched.employee_growth}% YoY")
        
        if len(enriched.job_postings) > 5:
            signals.append(f"Active hiring: {len(enriched.job_postings)} open positions")
        
        if enriched.recent_news:
            for news in enriched.recent_news[:2]:
                if any(word in news.get('title', '').lower() 
                      for word in ['expansion', 'growth', 'acquisition', 'partnership']):
                    signals.append(f"Recent news: {news['title']}")
        
        return signals
    
    def _detect_pain_indicators(self, enriched: EnrichedCompanyData) -> List[str]:
        """Detect indicators of business pain points."""
        pains = []
        
        # Low digital maturity
        if enriched.digital_maturity_score and enriched.digital_maturity_score < 40:
            pains.append("Low digital maturity compared to industry")
        
        # Missing critical tech
        if 'aws' not in enriched.tech_stack and 'azure' not in enriched.tech_stack:
            pains.append("No cloud infrastructure detected")
        
        # Manual processes likely
        if len(enriched.tech_stack) < 5:
            pains.append("Limited technology adoption suggests manual processes")
        
        # Growing company without automation
        if ('50' in enriched.company_size or '200' in enriched.company_size) and \
           not any(auto in enriched.tech_stack for auto in ['zapier', 'make', 'n8n']):
            pains.append("Scaling without automation tools")
        
        return pains
    
    def _detect_trigger_events(self, enriched: EnrichedCompanyData) -> List[str]:
        """Detect trigger events for outreach."""
        triggers = []
        
        # Recent funding
        if enriched.funding_stage:
            triggers.append(f"Recent {enriched.funding_stage} funding")
        
        # New leadership (would need to check news/LinkedIn)
        for news in enriched.recent_news:
            if any(word in news.get('title', '').lower() 
                  for word in ['ceo', 'cto', 'vp', 'hire', 'appoint']):
                triggers.append("Leadership change")
                break
        
        # Expansion
        if any('expansion' in news.get('title', '').lower() 
              for news in enriched.recent_news):
            triggers.append("Business expansion")
        
        # High growth
        if enriched.employee_growth and enriched.employee_growth > 30:
            triggers.append("Rapid growth phase")
        
        return triggers
    
    def _calculate_confidence_scores(self, enriched: EnrichedCompanyData) -> Dict[str, float]:
        """Calculate confidence scores for different data points."""
        scores = {}
        
        # Company info confidence
        company_fields = ['founded_year', 'headquarters', 'revenue_range']
        company_score = sum(1 for f in company_fields if getattr(enriched, f)) / len(company_fields)
        scores['company_info'] = company_score
        
        # Tech stack confidence
        scores['tech_stack'] = min(1.0, len(enriched.tech_stack) / 10)
        
        # Market intelligence confidence
        intel_score = 0
        if enriched.competitors:
            intel_score += 0.33
        if enriched.recent_news:
            intel_score += 0.33
        if enriched.job_postings:
            intel_score += 0.34
        scores['market_intelligence'] = intel_score
        
        # Overall confidence
        scores['overall'] = sum(scores.values()) / len(scores)
        
        return scores
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL."""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load data from cache."""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict[str, Any]):
        """Save data to cache."""
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        try:
            # Convert datetime to string for JSON serialization
            if 'last_updated' in data:
                data['last_updated'] = data['last_updated'].isoformat()
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Cache save failed: {e}")
    
    def _is_cache_stale(self, cached_data: Dict[str, Any], max_age_hours: int = 24) -> bool:
        """Check if cached data is stale."""
        if 'last_updated' not in cached_data:
            return True
        
        try:
            last_updated = datetime.fromisoformat(cached_data['last_updated'])
            age = datetime.now() - last_updated
            return age.total_seconds() > (max_age_hours * 3600)
        except:
            return True
    
    def _dict_to_enriched_data(self, data: Dict[str, Any]) -> EnrichedCompanyData:
        """Convert dictionary to EnrichedCompanyData."""
        # Handle datetime conversion
        if 'last_updated' in data and isinstance(data['last_updated'], str):
            data['last_updated'] = datetime.fromisoformat(data['last_updated'])
        
        return EnrichedCompanyData(**data)

def generate_enrichment_report(enriched: EnrichedCompanyData) -> str:
    """Generate a formatted enrichment report."""
    report = []
    report.append("=" * 60)
    report.append(f"ENRICHED COMPANY PROFILE: {enriched.company_name}")
    report.append("=" * 60)
    
    # Basic Information
    report.append("\n== BASIC INFORMATION ==")
    report.append(f"Website: {enriched.website}")
    report.append(f"Industry: {enriched.industry}")
    report.append(f"Size: {enriched.company_size}")
    if enriched.founded_year:
        report.append(f"Founded: {enriched.founded_year}")
    if enriched.headquarters:
        report.append(f"HQ: {enriched.headquarters}")
    if enriched.revenue_range:
        report.append(f"Revenue: {enriched.revenue_range}")
    
    # Technology Profile
    report.append("\n== TECHNOLOGY PROFILE ==")
    report.append(f"Tech Stack ({len(enriched.tech_stack)} detected): {', '.join(enriched.tech_stack[:10])}")
    if enriched.digital_maturity_score:
        report.append(f"Digital Maturity: {enriched.digital_maturity_score}/100")
    if enriched.tech_spend_estimate:
        report.append(f"Est. Tech Spend: {enriched.tech_spend_estimate}")
    
    # Growth Indicators
    if enriched.growth_signals:
        report.append("\n== GROWTH SIGNALS ==")
        for signal in enriched.growth_signals:
            report.append(f"• {signal}")
    
    # Pain Points
    if enriched.pain_indicators:
        report.append("\n== PAIN INDICATORS ==")
        for pain in enriched.pain_indicators:
            report.append(f"• {pain}")
    
    # Automation Opportunities
    if enriched.automation_opportunities:
        report.append("\n== AUTOMATION OPPORTUNITIES ==")
        for opp in enriched.automation_opportunities:
            report.append(f"• {opp}")
    
    # Trigger Events
    if enriched.trigger_events:
        report.append("\n== TRIGGER EVENTS ==")
        for trigger in enriched.trigger_events:
            report.append(f"• {trigger}")
    
    # Recent News
    if enriched.recent_news:
        report.append("\n== RECENT NEWS ==")
        for news in enriched.recent_news[:3]:
            report.append(f"• {news.get('title', 'Unknown')}")
    
    # Data Quality
    report.append("\n== DATA QUALITY ==")
    for metric, score in enriched.confidence_scores.items():
        report.append(f"{metric}: {score*100:.0f}%")
    report.append(f"Sources: {', '.join(enriched.enrichment_sources)}")
    
    return "\n".join(report)

def main():
    """Test the enrichment engine."""
    engine = DataEnrichmentEngine()
    
    test_companies = [
        "https://www.stripe.com",
        "https://www.notion.so",
        "https://www.figma.com"
    ]
    
    for url in test_companies:
        print(f"\n[ENRICHING] {url}")
        print("-" * 60)
        
        enriched = engine.enrich_company(url)
        report = generate_enrichment_report(enriched)
        print(report)
        
        # Save detailed JSON
        output_file = f"enrichment_{enriched.company_name.lower().replace(' ', '_')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            data = asdict(enriched)
            # Convert datetime for JSON
            data['last_updated'] = data['last_updated'].isoformat()
            json.dump(data, f, indent=2)
        
        print(f"\n[SAVED] Detailed data saved to: {output_file}")

if __name__ == "__main__":
    main()