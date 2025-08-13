"""
video_pipeline_integration.py - VideoReach AI Report-to-Video Pipeline
Phase 4: VRA-023 - Integrate audit reports with video generation

This module creates personalized video scripts from automation audit reports
and manages the end-to-end video generation pipeline.

Requirements:
- All previous modules (research, enrichment, audit, report, confidence)
- D-ID API key configured in .env
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
import hashlib
from enum import Enum

# Import all our modules
from research_engine import ResearchEngine
from enrichment_engine import DataEnrichmentEngine
from audit_engine import AutomationAuditEngine
from report_generator import ReportGenerator, ComprehensiveReport
from confidence_scorer import ConfidenceScorer, ConfidenceValidator
from core_test import generate_video_did

# Fix Windows Unicode issues
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class VideoType(Enum):
    """Types of videos to generate."""
    AUDIT_SUMMARY = "audit_summary"          # High-level audit findings
    ROI_FOCUSED = "roi_focused"              # Focus on financial benefits
    PAIN_SOLUTION = "pain_solution"          # Problem-solution narrative
    QUICK_WIN = "quick_win"                  # Focus on easy wins
    TRANSFORMATION = "transformation"        # Digital transformation story
    COMPARISON = "comparison"                # Industry comparison

@dataclass
class VideoScript:
    """Structured video script with metadata."""
    script_id: str
    prospect_name: str
    company_name: str
    video_type: VideoType
    duration_seconds: int
    
    # Script sections
    hook: str                    # 0-5 seconds
    problem_statement: str       # 5-15 seconds
    solution_overview: str       # 15-35 seconds
    call_to_action: str         # 35-45 seconds
    
    # Full script
    full_script: str
    word_count: int
    
    # Personalization elements
    personalization_points: List[str] = field(default_factory=list)
    data_points_used: List[str] = field(default_factory=list)
    confidence_score: float = 0.0
    
    # Generation metadata
    generated_at: datetime = field(default_factory=datetime.now)
    report_id: Optional[str] = None

@dataclass
class VideoCampaign:
    """Video campaign for multiple prospects."""
    campaign_id: str
    campaign_name: str
    created_at: datetime
    
    # Prospects and videos
    prospects: List[Dict[str, Any]] = field(default_factory=list)
    scripts: List[VideoScript] = field(default_factory=list)
    videos: List[Dict[str, Any]] = field(default_factory=list)
    
    # Status tracking
    total_prospects: int = 0
    scripts_generated: int = 0
    videos_generated: int = 0
    videos_sent: int = 0
    
    # Performance metrics
    total_cost: float = 0.0
    average_generation_time: float = 0.0
    success_rate: float = 0.0

class ScriptGenerator:
    """Generate personalized video scripts from audit reports."""
    
    # Target words per minute for natural speech
    WORDS_PER_MINUTE = 140
    
    # Script templates by type
    TEMPLATES = {
        VideoType.AUDIT_SUMMARY: {
            'hook': "Hi {prospect_name}, I just completed an automation audit of {company_name} and found something interesting.",
            'problem': "Your team is currently {pain_point_1}, which based on our analysis, is costing approximately {wasted_time} hours per week.",
            'solution': "We've identified {opportunity_count} automation opportunities that could {key_benefit}. For example, {specific_example}.",
            'cta': "I've prepared a detailed report with ROI projections. Worth a quick 15-minute call to review? {calendar_link}"
        },
        VideoType.ROI_FOCUSED: {
            'hook': "{prospect_name}, quick question - what would an extra {savings_amount} per year mean for {company_name}?",
            'problem': "Right now, your {problematic_process} is creating inefficiencies that compound as you scale.",
            'solution': "By automating {automation_area}, companies like yours typically see {roi_percentage}% ROI within {payback_period} months. Your specific opportunity could save {specific_savings}.",
            'cta': "Let's discuss how to capture this value quickly. Free consultation available this week: {calendar_link}"
        },
        VideoType.PAIN_SOLUTION: {
            'hook': "Hi {prospect_name}, I noticed {company_name} is {growth_signal} - congrats on the growth!",
            'problem': "But I imagine {pain_indicator} is becoming a real challenge as you scale.",
            'solution': "We helped {similar_company} solve this exact problem with {solution_type}, reducing {metric} by {improvement}%.",
            'cta': "Want to see how it would work for {company_name}? Let's chat: {calendar_link}"
        },
        VideoType.QUICK_WIN: {
            'hook': "{prospect_name}, found a quick automation win for {company_name} that takes less than a week to implement.",
            'problem': "Your team spends approximately {wasted_hours} hours on {manual_task} that could be automated today.",
            'solution': "With a simple {automation_tool} setup, this entire process runs automatically. We can have it live in {implementation_time} days.",
            'cta': "Want me to show you exactly how it works? Quick demo available: {calendar_link}"
        }
    }
    
    def __init__(self):
        self.confidence_scorer = ConfidenceScorer()
        self.validator = ConfidenceValidator()
    
    def generate_script(self, report: ComprehensiveReport, 
                       prospect_name: str = "there",
                       video_type: VideoType = VideoType.AUDIT_SUMMARY,
                       calendar_link: str = "calendly.com/videoreach") -> VideoScript:
        """
        Generate a personalized video script from an audit report.
        
        Args:
            report: Comprehensive audit report
            prospect_name: Name of the prospect
            video_type: Type of video script to generate
            calendar_link: Booking link for CTA
            
        Returns:
            VideoScript object with personalized content
        """
        print(f"[SCRIPT] Generating {video_type.value} script for {report.company_name}")
        
        # Extract key data points from report
        data_points = self._extract_data_points(report)
        data_points['prospect_name'] = prospect_name
        data_points['company_name'] = report.company_name
        data_points['calendar_link'] = calendar_link
        
        # Select template
        template = self.TEMPLATES.get(video_type, self.TEMPLATES[VideoType.AUDIT_SUMMARY])
        
        # Generate each section
        hook = self._personalize_text(template['hook'], data_points)
        problem = self._personalize_text(template['problem'], data_points)
        solution = self._personalize_text(template['solution'], data_points)
        cta = self._personalize_text(template['cta'], data_points)
        
        # Combine into full script
        full_script = f"{hook} {problem} {solution} {cta}"
        
        # Calculate metrics
        word_count = len(full_script.split())
        duration = int(word_count / self.WORDS_PER_MINUTE * 60)
        
        # Track personalization
        personalization_points = self._identify_personalization(full_script, data_points)
        
        # Calculate confidence
        confidence = self._calculate_script_confidence(report, personalization_points)
        
        # Create script object
        script = VideoScript(
            script_id=self._generate_script_id(),
            prospect_name=prospect_name,
            company_name=report.company_name,
            video_type=video_type,
            duration_seconds=duration,
            hook=hook,
            problem_statement=problem,
            solution_overview=solution,
            call_to_action=cta,
            full_script=full_script,
            word_count=word_count,
            personalization_points=personalization_points,
            data_points_used=list(data_points.keys()),
            confidence_score=confidence,
            report_id=report.report_id
        )
        
        print(f"[SCRIPT] Generated {word_count} word script ({duration}s)")
        
        return script
    
    def _extract_data_points(self, report: ComprehensiveReport) -> Dict[str, str]:
        """Extract key data points from report for script personalization."""
        data = {}
        
        # Company basics
        data['industry'] = report.enriched_data.industry
        data['company_size'] = report.enriched_data.company_size
        
        # Pain points and opportunities
        if report.enriched_data.pain_indicators:
            data['pain_point_1'] = report.enriched_data.pain_indicators[0]
            data['pain_indicator'] = report.enriched_data.pain_indicators[0]
        
        if report.enriched_data.automation_opportunities:
            data['opportunity_count'] = str(len(report.enriched_data.automation_opportunities))
            data['automation_area'] = report.enriched_data.automation_opportunities[0]
            data['specific_example'] = report.enriched_data.automation_opportunities[0]
        
        # Growth signals
        if report.enriched_data.growth_signals:
            data['growth_signal'] = report.enriched_data.growth_signals[0]
        
        # ROI metrics
        data['savings_amount'] = f"${report.total_savings_potential:,.0f}" if report.total_savings_potential else "$50,000"
        data['roi_percentage'] = "200"
        data['payback_period'] = str(report.payback_period_months) if report.payback_period_months else "6"
        data['specific_savings'] = f"${report.total_savings_potential/12:,.0f}/month" if report.total_savings_potential else "$4,000/month"
        
        # Inefficiency metrics (estimated)
        data['wasted_time'] = "15"
        data['wasted_hours'] = "20"
        data['manual_task'] = "data entry and reporting"
        data['problematic_process'] = "manual lead qualification"
        
        # Implementation details
        data['implementation_time'] = "5"
        data['automation_tool'] = "Zapier workflow"
        data['solution_type'] = "intelligent automation"
        
        # Improvement metrics
        data['metric'] = "processing time"
        data['improvement'] = "70"
        data['key_benefit'] = f"save {data['wasted_time']} hours per week"
        
        # Similar company example
        data['similar_company'] = self._get_similar_company(report.enriched_data.industry)
        
        return data
    
    def _personalize_text(self, template: str, data: Dict[str, str]) -> str:
        """Personalize template text with data points."""
        text = template
        for key, value in data.items():
            placeholder = f"{{{key}}}"
            if placeholder in text:
                text = text.replace(placeholder, str(value))
        
        # Remove any remaining placeholders
        import re
        text = re.sub(r'\{[^}]+\}', '', text)
        
        return text.strip()
    
    def _identify_personalization(self, script: str, data_points: Dict[str, str]) -> List[str]:
        """Identify personalization elements used in the script."""
        personalizations = []
        
        for key, value in data_points.items():
            if str(value) in script and value and str(value) != "Unknown":
                personalizations.append(f"{key}: {value}")
        
        return personalizations
    
    def _calculate_script_confidence(self, report: ComprehensiveReport, 
                                    personalizations: List[str]) -> float:
        """Calculate confidence score for the script."""
        base_confidence = 0.5
        
        # Boost for personalization
        personalization_boost = min(0.3, len(personalizations) * 0.05)
        
        # Include report confidence
        if hasattr(report, 'confidence_score'):
            report_confidence = report.confidence_score * 0.2
        else:
            report_confidence = 0.1
        
        return min(1.0, base_confidence + personalization_boost + report_confidence)
    
    def _get_similar_company(self, industry: str) -> str:
        """Get a similar company name for social proof."""
        similar_companies = {
            'Technology': 'TechScale Inc',
            'E-commerce': 'ShopFlow',
            'Healthcare': 'MedOps Group',
            'Finance': 'FinTech Solutions',
            'Education': 'EduTech Pro',
            'Marketing': 'MarketBoost',
            'Real Estate': 'PropTech Leaders',
            'SaaS': 'CloudScale'
        }
        return similar_companies.get(industry, 'a similar company')
    
    def _generate_script_id(self) -> str:
        """Generate unique script ID."""
        return hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:8]

class VideoPipelineIntegration:
    """Main pipeline integration orchestrator."""
    
    def __init__(self):
        self.report_generator = ReportGenerator()
        self.script_generator = ScriptGenerator()
        self.video_cache = {}
        self.output_dir = "generated_videos"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_video_from_url(self, website_url: str, 
                               prospect_name: str = "there",
                               video_type: VideoType = VideoType.AUDIT_SUMMARY) -> Dict[str, Any]:
        """
        Complete pipeline: URL → Research → Audit → Script → Video
        
        Args:
            website_url: Target company website
            prospect_name: Name of the prospect
            video_type: Type of video to generate
            
        Returns:
            Dict with video URL and metadata
        """
        print(f"\n[PIPELINE] Starting video generation for {website_url}")
        start_time = time.time()
        
        try:
            # Step 1: Generate comprehensive report
            print("[STEP 1/4] Generating audit report...")
            report = self.report_generator.generate_comprehensive_report(website_url)
            
            # Step 2: Generate personalized script
            print("[STEP 2/4] Creating personalized script...")
            script = self.script_generator.generate_script(
                report, prospect_name, video_type
            )
            
            # Step 3: Generate video
            print("[STEP 3/4] Generating AI avatar video...")
            video_result = self._generate_video(script)
            
            # Step 4: Package results
            print("[STEP 4/4] Packaging results...")
            result = self._package_results(report, script, video_result)
            
            elapsed = time.time() - start_time
            result['total_generation_time'] = elapsed
            
            print(f"[SUCCESS] Video generated in {elapsed:.1f} seconds")
            print(f"[URL] {result.get('video_url', 'No URL available')}")
            
            # Save to cache
            self.video_cache[script.script_id] = result
            
            # Save metadata
            self._save_metadata(result)
            
            return result
            
        except Exception as e:
            print(f"[ERROR] Pipeline failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'elapsed_time': time.time() - start_time
            }
    
    def generate_campaign_videos(self, prospects: List[Dict[str, str]], 
                                campaign_name: str = "Automation Audit Campaign") -> VideoCampaign:
        """
        Generate videos for multiple prospects.
        
        Args:
            prospects: List of dicts with 'url', 'name', 'email' keys
            campaign_name: Name of the campaign
            
        Returns:
            VideoCampaign object with all results
        """
        print(f"\n[CAMPAIGN] Starting campaign: {campaign_name}")
        print(f"[CAMPAIGN] Processing {len(prospects)} prospects")
        
        campaign = VideoCampaign(
            campaign_id=self._generate_campaign_id(),
            campaign_name=campaign_name,
            created_at=datetime.now(),
            prospects=prospects,
            total_prospects=len(prospects)
        )
        
        successful = 0
        failed = 0
        
        for i, prospect in enumerate(prospects):
            print(f"\n[PROSPECT {i+1}/{len(prospects)}] {prospect.get('name', 'Unknown')}")
            
            try:
                # Generate video
                result = self.generate_video_from_url(
                    prospect['url'],
                    prospect.get('name', 'there'),
                    VideoType.AUDIT_SUMMARY
                )
                
                if result.get('success', False):
                    campaign.videos.append(result)
                    campaign.scripts.append(result.get('script'))
                    campaign.videos_generated += 1
                    successful += 1
                else:
                    failed += 1
                    print(f"[FAILED] {prospect.get('name')}: {result.get('error')}")
                    
            except Exception as e:
                failed += 1
                print(f"[ERROR] Failed for {prospect.get('name')}: {str(e)}")
            
            # Rate limiting
            if i < len(prospects) - 1:
                time.sleep(2)  # Delay between videos
        
        # Calculate campaign metrics
        campaign.scripts_generated = successful
        campaign.success_rate = (successful / len(prospects)) * 100 if prospects else 0
        campaign.total_cost = successful * 0.10  # Estimated cost per video
        
        # Save campaign data
        self._save_campaign(campaign)
        
        print(f"\n[CAMPAIGN COMPLETE]")
        print(f"Success: {successful}/{len(prospects)} ({campaign.success_rate:.1f}%)")
        print(f"Total Cost: ${campaign.total_cost:.2f}")
        
        return campaign
    
    def _generate_video(self, script: VideoScript) -> Dict[str, Any]:
        """Generate video using D-ID API."""
        # Adjust script if too long
        if script.word_count > 250:
            print("[WARNING] Script too long, truncating to 250 words")
            words = script.full_script.split()[:250]
            script_text = ' '.join(words)
        else:
            script_text = script.full_script
        
        # Generate video
        result = generate_video_did(script_text)
        
        if result and result.get('success'):
            return {
                'success': True,
                'video_url': result['video_url'],
                'video_id': result.get('video_id'),
                'duration': result.get('duration'),
                'provider': 'D-ID'
            }
        else:
            return {
                'success': False,
                'error': 'Video generation failed'
            }
    
    def _package_results(self, report: ComprehensiveReport, 
                        script: VideoScript, 
                        video_result: Dict[str, Any]) -> Dict[str, Any]:
        """Package all results into a comprehensive response."""
        return {
            'success': video_result.get('success', False),
            'video_url': video_result.get('video_url'),
            'video_id': video_result.get('video_id'),
            'script_id': script.script_id,
            'report_id': report.report_id,
            'company_name': report.company_name,
            'prospect_name': script.prospect_name,
            'video_type': script.video_type.value,
            'duration_seconds': script.duration_seconds,
            'script': script.full_script,
            'personalization_count': len(script.personalization_points),
            'confidence_score': script.confidence_score,
            'automation_opportunities': len(report.enriched_data.automation_opportunities),
            'potential_savings': report.total_savings_potential,
            'payback_months': report.payback_period_months,
            'generated_at': datetime.now().isoformat()
        }
    
    def _save_metadata(self, result: Dict[str, Any]):
        """Save video metadata to file."""
        filename = f"{self.output_dir}/video_{result.get('script_id', 'unknown')}_metadata.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"[SAVED] Metadata: {filename}")
    
    def _save_campaign(self, campaign: VideoCampaign):
        """Save campaign data to file."""
        filename = f"{self.output_dir}/campaign_{campaign.campaign_id}.json"
        campaign_dict = asdict(campaign)
        # Convert datetime objects
        campaign_dict['created_at'] = campaign_dict['created_at'].isoformat()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(campaign_dict, f, indent=2)
        print(f"[SAVED] Campaign: {filename}")
    
    def _generate_campaign_id(self) -> str:
        """Generate unique campaign ID."""
        return hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:8]

def main():
    """Test the integrated pipeline."""
    pipeline = VideoPipelineIntegration()
    
    # Test single video generation
    print("=" * 60)
    print("TESTING SINGLE VIDEO GENERATION")
    print("=" * 60)
    
    test_url = "https://www.canva.com"
    result = pipeline.generate_video_from_url(
        test_url,
        prospect_name="Sarah",
        video_type=VideoType.ROI_FOCUSED
    )
    
    if result.get('success'):
        print("\n[RESULT SUMMARY]")
        print(f"Video URL: {result['video_url']}")
        print(f"Duration: {result['duration_seconds']}s")
        print(f"Personalization Points: {result['personalization_count']}")
        print(f"Confidence Score: {result['confidence_score']:.2%}")
        print(f"Potential Savings: ${result['potential_savings']:,.0f}")
        print(f"Total Time: {result['total_generation_time']:.1f}s")
    
    # Test campaign (batch) generation
    print("\n" + "=" * 60)
    print("TESTING CAMPAIGN VIDEO GENERATION")
    print("=" * 60)
    
    test_prospects = [
        {"url": "https://www.monday.com", "name": "David", "email": "david@monday.com"},
        {"url": "https://www.slack.com", "name": "Lisa", "email": "lisa@slack.com"}
    ]
    
    campaign = pipeline.generate_campaign_videos(
        test_prospects,
        campaign_name="Q4 Automation Audit Outreach"
    )
    
    print(f"\n[CAMPAIGN RESULTS]")
    print(f"Campaign ID: {campaign.campaign_id}")
    print(f"Videos Generated: {campaign.videos_generated}/{campaign.total_prospects}")
    print(f"Success Rate: {campaign.success_rate:.1f}%")
    print(f"Total Cost: ${campaign.total_cost:.2f}")

if __name__ == "__main__":
    # Check if D-ID API key is configured
    from dotenv import load_dotenv
    load_dotenv()
    
    if not os.environ.get('DID_API_KEY'):
        print("[ERROR] D-ID API key not configured in .env file")
        print("Please add: DID_API_KEY=your_api_key")
        exit(1)
    
    main()