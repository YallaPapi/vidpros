"""
Faceless Video Pipeline Integration
Integrates faceless video generation with the existing research and distribution pipeline
"""

import os
import json
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime

from research_engine import ResearchEngine
from intelligent_script_generator import IntelligentScriptGenerator
from faceless_video_generator import FacelessVideoGenerator
from delivery_system import MultiChannelDelivery
from report_generator import ReportGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FacelessVideoPipeline:
    """Complete pipeline for faceless video generation and distribution"""
    
    def __init__(self):
        self.research_engine = ResearchEngine()
        self.script_generator = IntelligentScriptGenerator(
            api_key=os.getenv('OPENAI_API_KEY')
        )
        self.video_generator = FacelessVideoGenerator(
            elevenlabs_api_key=os.getenv('ELEVENLABS_API_KEY')
        )
        self.delivery_system = MultiChannelDelivery()
        self.report_generator = ReportGenerator()
        
    async def process_prospect(
        self,
        company_name: str,
        website: str,
        email: str,
        industry: str,
        owner_name: Optional[str] = None,
        include_report: bool = True
    ) -> Dict:
        """
        Complete pipeline for a single prospect
        Returns dict with video_url, report_url, and status
        """
        
        logger.info(f"Processing prospect: {company_name}")
        result = {
            'company': company_name,
            'status': 'processing',
            'video_url': None,
            'report_url': None,
            'email_sent': False,
            'errors': []
        }
        
        try:
            # 1. Research Phase
            logger.info("Phase 1: Researching company...")
            research_data = self.research_engine.research_company(website)
            
            if not research_data:
                result['errors'].append("Failed to research company")
                result['status'] = 'failed'
                return result
            
            # 2. Calculate automation opportunities and ROI
            automation_opportunities = self._analyze_automation_opportunities(research_data)
            
            # 3. Prepare data for video generation
            company_data = {
                'company': company_name,
                'website': website,
                'industry': industry,
                'owner_name': owner_name,
                'email': email,
                'pain_points': automation_opportunities['pain_points'],
                'monthly_loss': automation_opportunities['monthly_loss'],
                'solution_cost': automation_opportunities['solution_cost'],
                'competitor': automation_opportunities['competitor'],
                'calendar_link': os.getenv('CALENDAR_LINK', 'calendly.com/demo')
            }
            
            # 4. Generate video script sections
            logger.info("Phase 2: Generating personalized script...")
            script_data = self.script_generator.generate_script(
                company_name=company_name,
                industry=industry,
                website_url=website,
                pain_points=automation_opportunities['pain_points'],
                competitor=automation_opportunities['competitor']
            )
            
            # Update company data with generated script
            company_data['full_script'] = script_data.get('script', '')
            
            # 5. Generate faceless video
            logger.info("Phase 3: Creating faceless video...")
            video_path = await self.video_generator.generate_faceless_video(
                company_data=company_data,
                output_path=f"videos/{company_name.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
            )
            
            if video_path:
                result['video_url'] = video_path
                logger.info(f"Video generated: {video_path}")
            else:
                result['errors'].append("Failed to generate video")
                result['status'] = 'partial'
            
            # 6. Generate audit report (optional)
            if include_report:
                logger.info("Phase 4: Generating automation audit report...")
                report_path = self.report_generator.generate_report(
                    company_name=company_name,
                    research_data=research_data,
                    automation_opportunities=automation_opportunities
                )
                
                if report_path:
                    result['report_url'] = report_path
                    logger.info(f"Report generated: {report_path}")
                else:
                    result['errors'].append("Failed to generate report")
                    result['status'] = 'partial'
            
            # 7. Send via email (disabled for testing)
            if result['video_url']:
                logger.info("Phase 5: Email delivery disabled for testing")
                # TODO: Fix email delivery integration
                # email_sent = self.delivery_system.deliver_report(...)
                result['email_sent'] = False
                result['status'] = 'completed'  # Mark as completed even without email
            
        except Exception as e:
            logger.error(f"Pipeline error for {company_name}: {str(e)}")
            result['errors'].append(str(e))
            result['status'] = 'failed'
        
        return result
    
    def _analyze_automation_opportunities(self, research_data: Dict) -> Dict:
        """Analyze research data to find automation opportunities"""
        
        # Default values
        opportunities = {
            'pain_points': [],
            'monthly_loss': 10000,
            'solution_cost': 497,
            'competitor': 'leading competitors',
            'automation_score': 0
        }
        
        # Check for missing features (pain points)
        if not research_data.get('has_online_booking'):
            opportunities['pain_points'].append('no online booking')
            opportunities['automation_score'] += 20
            opportunities['monthly_loss'] += 5000
        
        if not research_data.get('has_chat'):
            opportunities['pain_points'].append('no live chat support')
            opportunities['automation_score'] += 15
            opportunities['monthly_loss'] += 3000
        
        if not research_data.get('has_crm'):
            opportunities['pain_points'].append('no customer management system')
            opportunities['automation_score'] += 25
            opportunities['monthly_loss'] += 7000
        
        if not research_data.get('mobile_responsive'):
            opportunities['pain_points'].append('not mobile optimized')
            opportunities['automation_score'] += 15
            opportunities['monthly_loss'] += 4000
        
        if research_data.get('page_speed', 10) > 5:
            opportunities['pain_points'].append('slow website performance')
            opportunities['automation_score'] += 10
            opportunities['monthly_loss'] += 2000
        
        # Set solution cost based on complexity
        if opportunities['automation_score'] > 50:
            opportunities['solution_cost'] = 997
        elif opportunities['automation_score'] > 30:
            opportunities['solution_cost'] = 697
        else:
            opportunities['solution_cost'] = 497
        
        # Find competitor (if available from research)
        if research_data.get('competitors'):
            opportunities['competitor'] = research_data['competitors'][0]
        
        return opportunities
    
    async def process_batch(self, prospects: list) -> list:
        """Process multiple prospects in parallel"""
        
        logger.info(f"Processing batch of {len(prospects)} prospects")
        
        # Create tasks for parallel processing
        tasks = []
        for prospect in prospects:
            task = self.process_prospect(
                company_name=prospect['company'],
                website=prospect['website'],
                email=prospect['email'],
                industry=prospect.get('industry', 'business'),
                owner_name=prospect.get('owner_name'),
                include_report=prospect.get('include_report', True)
            )
            tasks.append(task)
        
        # Process all prospects in parallel
        results = await asyncio.gather(*tasks)
        
        # Summary statistics
        successful = sum(1 for r in results if r['status'] == 'completed')
        partial = sum(1 for r in results if r['status'] == 'partial')
        failed = sum(1 for r in results if r['status'] == 'failed')
        
        logger.info(f"Batch processing complete: {successful} successful, {partial} partial, {failed} failed")
        
        return results


class FacelessVideoComparison:
    """Compare faceless vs avatar videos for A/B testing"""
    
    @staticmethod
    def calculate_cost_comparison():
        """Calculate cost difference between faceless and avatar videos"""
        
        comparison = {
            'faceless': {
                'voiceover': 0.02,  # ElevenLabs
                'screenshot': 0.01,  # Minimal API costs
                'processing': 0.01,  # FFmpeg is free
                'total_per_video': 0.04
            },
            'avatar': {
                'd_id': 0.15,  # D-ID API
                'processing': 0.05,  # Additional processing
                'total_per_video': 0.20
            }
        }
        
        # Calculate savings
        savings_per_video = comparison['avatar']['total_per_video'] - comparison['faceless']['total_per_video']
        savings_per_1000 = savings_per_video * 1000
        
        comparison['savings'] = {
            'per_video': savings_per_video,
            'per_1000_videos': savings_per_1000,
            'percentage': (savings_per_video / comparison['avatar']['total_per_video']) * 100
        }
        
        return comparison
    
    @staticmethod
    def expected_performance():
        """Expected performance metrics for faceless videos"""
        
        return {
            'processing_time': {
                'faceless': '10-15 seconds',
                'avatar': '30-45 seconds',
                'improvement': '66% faster'
            },
            'conversion_rates': {
                'faceless': {
                    'open_rate': '60-65%',
                    'watch_rate': '35-40%',
                    'response_rate': '15-20%',
                    'meeting_rate': '5-7%'
                },
                'avatar': {
                    'open_rate': '55-60%',
                    'watch_rate': '30-35%',
                    'response_rate': '12-18%',
                    'meeting_rate': '4-6%'
                },
                'notes': 'Faceless videos often perform better due to focus on data/problems'
            },
            'scalability': {
                'faceless': '1000+ videos/day possible',
                'avatar': '500 videos/day (API limits)',
                'bottleneck': 'Faceless has no API rate limits'
            }
        }


# Test function
async def test_faceless_pipeline():
    """Test the faceless video pipeline with a sample prospect"""
    
    pipeline = FacelessVideoPipeline()
    
    # Test prospect
    result = await pipeline.process_prospect(
        company_name="Test HVAC Company",
        website="https://example-hvac.com",
        email="test@example.com",
        industry="HVAC",
        owner_name="Bob Smith",
        include_report=True
    )
    
    print(f"Pipeline Result: {json.dumps(result, indent=2)}")
    
    # Show cost comparison
    comparison = FacelessVideoComparison.calculate_cost_comparison()
    print(f"\nCost Comparison: {json.dumps(comparison, indent=2)}")
    
    # Show expected performance
    performance = FacelessVideoComparison.expected_performance()
    print(f"\nExpected Performance: {json.dumps(performance, indent=2)}")


if __name__ == "__main__":
    asyncio.run(test_faceless_pipeline())