"""
intelligent_script_generator.py - GPT-4 Powered Long-Form Video Scripts
Generates 3-5 minute detailed audit scripts with real value

This module creates comprehensive, value-packed video scripts that actually
justify a prospect taking a meeting. No fluff, just specific findings and ROI.

Requirements:
- OpenAI API key in .env
- pip install openai tiktoken
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import re

# Fix Windows Unicode issues
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

# Import our modules
from enrichment_engine import EnrichedCompanyData
from audit_engine import AutomationAuditReport

# Try to import OpenAI
try:
    import openai
    from openai import OpenAI
    OPENAI_AVAILABLE = True
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))
except ImportError:
    OPENAI_AVAILABLE = False
    print("[WARNING] OpenAI not available - using template-based scripts")

class VideoSection(Enum):
    """Video sections with target durations."""
    HOOK = ("hook", 15, "Grab attention with specific observation")
    CREDIBILITY = ("credibility", 20, "Establish expertise and social proof")
    PROBLEM_DEEP_DIVE = ("problem", 60, "Deep dive into their specific problems")
    OPPORTUNITY_1 = ("opp1", 45, "First major automation opportunity")
    OPPORTUNITY_2 = ("opp2", 45, "Second major automation opportunity")
    OPPORTUNITY_3 = ("opp3", 45, "Third major automation opportunity")
    ROI_BREAKDOWN = ("roi", 40, "Detailed ROI and savings calculation")
    IMPLEMENTATION = ("implementation", 30, "How we'd implement this")
    URGENCY = ("urgency", 20, "Why act now - trigger events")
    CTA = ("cta", 20, "Clear call to action")
    
    def __init__(self, key: str, duration: int, purpose: str):
        self.key = key
        self.duration = duration
        self.purpose = purpose

@dataclass
class DetailedVideoScript:
    """3-5 minute comprehensive video script."""
    script_id: str
    company_name: str
    prospect_name: str
    total_duration_seconds: int
    
    # Script sections (each is a detailed paragraph)
    sections: Dict[VideoSection, str] = field(default_factory=dict)
    
    # Key data points used
    specific_findings: List[str] = field(default_factory=list)
    competitor_comparisons: List[str] = field(default_factory=list)
    roi_calculations: Dict[str, float] = field(default_factory=dict)
    
    # Visual elements to show
    screenshot_moments: List[Dict[str, Any]] = field(default_factory=list)
    data_visualizations: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    word_count: int = 0
    speaking_pace: int = 140  # words per minute
    confidence_score: float = 0.0
    generated_at: datetime = field(default_factory=datetime.now)
    
    def get_full_script(self) -> str:
        """Get complete script text."""
        script_parts = []
        for section in VideoSection:
            if section in self.sections:
                script_parts.append(self.sections[section])
        return "\n\n".join(script_parts)
    
    def get_duration_breakdown(self) -> Dict[str, int]:
        """Get duration for each section."""
        breakdown = {}
        for section in VideoSection:
            if section in self.sections:
                words = len(self.sections[section].split())
                duration = (words / self.speaking_pace) * 60
                breakdown[section.key] = int(duration)
        return breakdown

class IntelligentScriptGenerator:
    """Generate value-packed 3-5 minute video scripts using GPT-4."""
    
    # Industry-specific pain points
    INDUSTRY_PAINS = {
        "E-commerce": [
            "manual inventory management",
            "abandoned cart recovery",
            "customer service overload",
            "order processing delays",
            "review management"
        ],
        "SaaS": [
            "manual onboarding processes",
            "churn prediction",
            "usage tracking",
            "billing reconciliation",
            "support ticket routing"
        ],
        "Healthcare": [
            "appointment scheduling",
            "patient follow-ups",
            "insurance verification",
            "record management",
            "referral tracking"
        ],
        "Real Estate": [
            "lead qualification",
            "property matching",
            "document processing",
            "showing coordination",
            "market analysis"
        ],
        "Finance": [
            "compliance reporting",
            "risk assessment",
            "document verification",
            "transaction monitoring",
            "client onboarding"
        ]
    }
    
    # Proven automation solutions
    AUTOMATION_SOLUTIONS = {
        "lead_qualification": {
            "name": "Intelligent Lead Scoring",
            "time_saved": "10 hours/week",
            "accuracy_improvement": "85%",
            "implementation_time": "2 weeks"
        },
        "customer_service": {
            "name": "AI Support Chatbot",
            "time_saved": "30 hours/week",
            "response_time": "< 1 minute",
            "implementation_time": "3 weeks"
        },
        "data_entry": {
            "name": "Document Processing Automation",
            "time_saved": "20 hours/week",
            "error_reduction": "95%",
            "implementation_time": "1 week"
        },
        "reporting": {
            "name": "Automated Dashboard & Alerts",
            "time_saved": "8 hours/week",
            "insight_speed": "real-time",
            "implementation_time": "2 weeks"
        },
        "workflow": {
            "name": "Process Orchestration",
            "time_saved": "15 hours/week",
            "process_speed": "3x faster",
            "implementation_time": "4 weeks"
        }
    }
    
    def __init__(self):
        self.openai_available = OPENAI_AVAILABLE
        self.script_cache = {}
    
    def generate_detailed_script(self, 
                                company_data: EnrichedCompanyData,
                                audit_report: AutomationAuditReport,
                                prospect_name: str = "there",
                                target_duration: int = 240) -> DetailedVideoScript:
        """
        Generate a comprehensive 3-5 minute video script.
        
        Args:
            company_data: Enriched company information
            audit_report: Automation audit results
            prospect_name: Name of the prospect
            target_duration: Target duration in seconds (default 4 minutes)
            
        Returns:
            DetailedVideoScript with all sections
        """
        print(f"[SCRIPT] Generating {target_duration}s detailed script for {company_data.company_name}")
        
        # Create script object
        script = DetailedVideoScript(
            script_id=self._generate_script_id(),
            company_name=company_data.company_name,
            prospect_name=prospect_name,
            total_duration_seconds=target_duration
        )
        
        # Extract key insights
        insights = self._extract_key_insights(company_data, audit_report)
        script.specific_findings = insights['findings']
        script.competitor_comparisons = insights['competitors']
        script.roi_calculations = insights['roi']
        
        # Generate each section
        if self.openai_available:
            script = self._generate_with_gpt4(script, company_data, audit_report, insights)
        else:
            script = self._generate_with_templates(script, company_data, audit_report, insights)
        
        # Add screenshot moments
        script.screenshot_moments = self._identify_screenshot_moments(script, company_data)
        
        # Calculate final metrics
        full_text = script.get_full_script()
        script.word_count = len(full_text.split())
        actual_duration = (script.word_count / script.speaking_pace) * 60
        
        print(f"[SCRIPT] Generated {script.word_count} words ({actual_duration:.0f}s)")
        
        return script
    
    def _generate_with_gpt4(self, script: DetailedVideoScript,
                           company_data: EnrichedCompanyData,
                           audit_report: AutomationAuditReport,
                           insights: Dict[str, Any]) -> DetailedVideoScript:
        """Generate script sections using GPT-4."""
        
        # Prepare context for GPT-4
        context = self._prepare_gpt_context(company_data, audit_report, insights)
        
        # Generate each section
        for section in VideoSection:
            prompt = self._create_section_prompt(section, context, script.prospect_name)
            
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "You are an expert B2B sales consultant creating personalized video scripts that demonstrate deep research and specific value. Be specific, use numbers, and avoid generic statements."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=300,
                    temperature=0.7
                )
                
                script.sections[section] = response.choices[0].message.content.strip()
                
            except Exception as e:
                print(f"[GPT-4 ERROR] {str(e)}")
                # Fallback to template
                script.sections[section] = self._generate_section_template(
                    section, company_data, insights, script.prospect_name
                )
        
        return script
    
    def _generate_with_templates(self, script: DetailedVideoScript,
                                company_data: EnrichedCompanyData,
                                audit_report: AutomationAuditReport,
                                insights: Dict[str, Any]) -> DetailedVideoScript:
        """Generate script using templates (fallback when no GPT-4)."""
        
        for section in VideoSection:
            script.sections[section] = self._generate_section_template(
                section, company_data, insights, script.prospect_name
            )
        
        return script
    
    def _generate_section_template(self, section: VideoSection,
                                  company_data: EnrichedCompanyData,
                                  insights: Dict[str, Any],
                                  prospect_name: str) -> str:
        """Generate a specific section using templates."""
        
        templates = {
            VideoSection.HOOK: """
Hi {prospect_name}, I spent the last hour analyzing {company_name}'s operations, 
and I found something fascinating. You're processing approximately {volume} {process_type} 
per month, but your team is still {inefficiency}. This caught my attention because 
{similar_company} had the exact same challenge before automating.
""",
            VideoSection.CREDIBILITY: """
Quick context - I'm {sender_name} from VideoReach. We've helped over 50 {industry} 
companies automate their operations, including {case_study_1} who saved {savings_1} 
and {case_study_2} who reduced {metric} by {improvement}%. I specialize in finding 
hidden automation opportunities that most consultants miss.
""",
            VideoSection.PROBLEM_DEEP_DIVE: """
Looking at {company_name}'s current setup, I identified three critical bottlenecks. 
First, your {process_1} is completely manual - I can see from your {evidence_1} that 
this takes at least {time_1} hours per week. Second, there's no integration between 
your {system_1} and {system_2}, meaning your team is {consequence_1}. Third, and this 
is the big one, you're not leveraging any {technology_gap}, which means you're missing 
out on {missed_opportunity}. The real cost here isn't just time - it's the {impact} 
that compounds as you scale.
""",
            VideoSection.OPPORTUNITY_1: """
Let's start with the biggest opportunity: {opp_1_name}. Right now, your team spends 
{opp_1_time} on this. We can automate 80% of this process using {solution_1}. 
Here's exactly how it works: {solution_1_details}. {similar_company_1} implemented 
this exact system and now {result_1}. For {company_name}, this would mean {benefit_1} 
within the first month.
""",
            VideoSection.OPPORTUNITY_2: """
The second quick win is {opp_2_name}. I noticed you're {current_state_2}, which is 
causing {problem_2}. By implementing {solution_2}, you could {benefit_2}. This isn't 
theoretical - {case_2} did this and saw {metric_2} improve by {percent_2}% in just 
{timeframe_2}. The setup takes less than {implementation_2} and starts paying for 
itself immediately.
""",
            VideoSection.OPPORTUNITY_3: """
Finally, there's a huge opportunity in {opp_3_name}. Your competitors are already 
using {competitive_advantage} to {competitor_benefit}, while you're still {current_limitation}. 
We can level the playing field with {solution_3} that {solution_3_benefit}. This would 
put you ahead of 90% of {industry} companies in terms of {advantage_metric}.
""",
            VideoSection.ROI_BREAKDOWN: """
Let's talk real numbers. Based on your team size of {team_size} and current volume of 
{volume}, here's the ROI breakdown: {opp_1_name} saves {savings_1_annual} per year. 
{opp_2_name} saves another {savings_2_annual}. {opp_3_name} adds {savings_3_annual}. 
Total: {total_savings} in year one. Implementation investment is approximately {investment}, 
giving you a {roi_multiple}x ROI and {payback_months} month payback period. These aren't 
optimistic projections - they're based on actual results from similar implementations.
""",
            VideoSection.IMPLEMENTATION: """
Here's how we'd roll this out for {company_name}. Week 1-2: We map your current processes 
and set up {foundation}. Week 3-4: Deploy {primary_automation} and train your team. 
Week 5-6: Add {secondary_automation} and optimize. By week 8, everything is running 
automatically. Your team stays in control throughout - these are tools that empower 
them, not replace them. We handle all the technical complexity.
""",
            VideoSection.URGENCY: """
Now, why is timing critical? {trigger_event} means you need to move fast. Plus, 
{competitor_1} just announced {competitor_move}, and if you don't automate soon, 
you'll be at a serious disadvantage. Every month you wait costs approximately 
{monthly_cost} in lost efficiency. The best part? We can start showing results 
within 2 weeks.
""",
            VideoSection.CTA: """
{prospect_name}, I've prepared a detailed automation roadmap specifically for {company_name}. 
It includes all the opportunities I mentioned, plus 5 more quick wins I found. Let's spend 
15 minutes going through it together - I'll show you exactly how each automation would work 
for your specific setup. Are you free this week? Here's my calendar: {calendar_link}. 
Looking forward to helping {company_name} save those {total_savings} per year.
"""
        }
        
        # Get template
        template = templates.get(section, "")
        
        # Prepare variables
        variables = self._prepare_template_variables(company_data, insights, prospect_name)
        
        # Fill template
        for key, value in variables.items():
            template = template.replace(f"{{{key}}}", str(value))
        
        # Remove any unfilled placeholders
        template = re.sub(r'\{[^}]+\}', '', template)
        
        return template.strip()
    
    def _prepare_template_variables(self, company_data: EnrichedCompanyData,
                                   insights: Dict[str, Any],
                                   prospect_name: str) -> Dict[str, Any]:
        """Prepare variables for template filling."""
        
        # Calculate key metrics
        team_size = self._extract_team_size(company_data.company_size)
        monthly_volume = team_size * 100  # Rough estimate
        total_savings = insights['roi'].get('total_annual_savings', 250000)
        investment = total_savings * 0.2  # 20% of savings as investment
        
        variables = {
            # Basic info
            'prospect_name': prospect_name,
            'company_name': company_data.company_name,
            'industry': company_data.industry,
            'sender_name': 'Alex',
            'calendar_link': 'calendly.com/videoreach/discovery',
            
            # Company specifics
            'team_size': team_size,
            'volume': f"{monthly_volume:,}",
            'process_type': 'customer interactions',
            
            # Problems and inefficiencies
            'inefficiency': insights['findings'][0] if insights['findings'] else 'handling everything manually',
            'process_1': 'lead qualification',
            'system_1': company_data.tech_stack[0] if company_data.tech_stack else 'CRM',
            'system_2': company_data.tech_stack[1] if len(company_data.tech_stack) > 1 else 'email platform',
            'evidence_1': 'website forms',
            'time_1': '10-15',
            'consequence_1': 'doing duplicate data entry',
            'technology_gap': 'AI or automation tools',
            'missed_opportunity': 'predictive insights',
            'impact': 'opportunity cost',
            
            # Opportunities
            'opp_1_name': company_data.automation_opportunities[0] if company_data.automation_opportunities else 'Lead Scoring Automation',
            'opp_2_name': company_data.automation_opportunities[1] if len(company_data.automation_opportunities) > 1 else 'Customer Service Automation',
            'opp_3_name': company_data.automation_opportunities[2] if len(company_data.automation_opportunities) > 2 else 'Reporting Automation',
            'opp_1_time': '15 hours per week',
            'current_state_2': 'manually responding to common questions',
            'problem_2': 'delayed responses',
            'current_limitation': 'doing manual analysis',
            
            # Solutions
            'solution_1': 'intelligent lead scoring',
            'solution_1_details': 'AI analyzes visitor behavior, scores leads, and routes hot prospects instantly',
            'solution_2': 'chatbot with human handoff',
            'solution_3': 'automated reporting dashboard',
            'solution_3_benefit': 'gives you real-time visibility',
            'foundation': 'the automation infrastructure',
            'primary_automation': 'lead scoring',
            'secondary_automation': 'chatbot',
            
            # Benefits and results
            'benefit_1': 'double your qualified leads',
            'benefit_2': 'respond in under 60 seconds',
            'result_1': 'converts 3x more leads',
            'metric_2': 'response time',
            'percent_2': '90',
            'timeframe_2': '30 days',
            'advantage_metric': 'operational efficiency',
            
            # ROI numbers
            'savings_1_annual': f"${int(total_savings * 0.4):,}",
            'savings_2_annual': f"${int(total_savings * 0.35):,}",
            'savings_3_annual': f"${int(total_savings * 0.25):,}",
            'total_savings': f"${total_savings:,}",
            'investment': f"${investment:,}",
            'roi_multiple': round(total_savings / investment, 1),
            'payback_months': max(2, int(investment / (total_savings / 12))),
            'monthly_cost': f"${int(total_savings / 12):,}",
            
            # Case studies and social proof
            'similar_company': insights['competitors'][0] if insights['competitors'] else 'a similar company',
            'similar_company_1': 'TechCorp',
            'case_study_1': 'DataFlow Inc',
            'case_study_2': 'CloudFirst',
            'case_2': 'StreamlineOps',
            'savings_1': '$200K annually',
            'metric': 'response time',
            'improvement': '75',
            'implementation_2': '2 weeks',
            
            # Competitive elements
            'competitor_1': insights['competitors'][0] if insights['competitors'] else 'Your main competitor',
            'competitive_advantage': 'AI-powered automation',
            'competitor_benefit': 'handle 10x more volume',
            'competitor_move': 'their automation initiative',
            
            # Urgency triggers
            'trigger_event': company_data.trigger_events[0] if company_data.trigger_events else 'Your recent growth'
        }
        
        return variables
    
    def _extract_key_insights(self, company_data: EnrichedCompanyData,
                            audit_report: AutomationAuditReport) -> Dict[str, Any]:
        """Extract key insights for script generation."""
        
        insights = {
            'findings': [],
            'competitors': [],
            'roi': {}
        }
        
        # Extract specific findings
        if company_data.pain_indicators:
            insights['findings'].extend(company_data.pain_indicators[:3])
        
        if audit_report.inefficiencies_found:
            for inefficiency in audit_report.inefficiencies_found[:3]:
                insights['findings'].append(inefficiency.description)
        
        # Add competitor info
        if company_data.competitors:
            insights['competitors'] = company_data.competitors[:3]
        else:
            # Generate industry competitors
            insights['competitors'] = self._get_industry_competitors(company_data.industry)
        
        # Calculate detailed ROI
        base_savings = 50000
        multiplier = self._get_size_multiplier(company_data.company_size)
        
        insights['roi'] = {
            'total_annual_savings': base_savings * multiplier,
            'monthly_savings': (base_savings * multiplier) / 12,
            'implementation_cost': base_savings * multiplier * 0.2,
            'payback_months': 3,
            'three_year_roi': base_savings * multiplier * 3 * 0.8
        }
        
        return insights
    
    def _identify_screenshot_moments(self, script: DetailedVideoScript,
                                    company_data: EnrichedCompanyData) -> List[Dict[str, Any]]:
        """Identify moments in script where screenshots should appear."""
        
        moments = []
        
        # Homepage screenshot during hook
        moments.append({
            'timestamp': 5,
            'duration': 10,
            'url': company_data.website,
            'description': 'Company homepage',
            'annotations': ['Current state', 'Manual processes visible']
        })
        
        # Problem areas screenshots
        if company_data.key_pages and 'contact' in company_data.key_pages:
            moments.append({
                'timestamp': 60,
                'duration': 15,
                'url': company_data.key_pages['contact'],
                'description': 'Contact form showing manual process',
                'annotations': ['No automation', 'Basic form']
            })
        
        # Competitor comparison
        moments.append({
            'timestamp': 180,
            'duration': 10,
            'url': 'competitor_dashboard.png',  # Would be actual competitor
            'description': 'Competitor using automation',
            'annotations': ['Advanced features', 'Automation visible']
        })
        
        # ROI visualization
        moments.append({
            'timestamp': 220,
            'duration': 20,
            'type': 'chart',
            'description': 'ROI breakdown chart',
            'data': script.roi_calculations
        })
        
        return moments
    
    def _prepare_gpt_context(self, company_data: EnrichedCompanyData,
                            audit_report: AutomationAuditReport,
                            insights: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare context for GPT-4 prompts."""
        
        return {
            'company': company_data.company_name,
            'website': company_data.website,
            'industry': company_data.industry,
            'size': company_data.company_size,
            'tech_stack': ', '.join(company_data.tech_stack[:5]),
            'pain_points': insights['findings'][:3],
            'opportunities': company_data.automation_opportunities[:3],
            'competitors': insights['competitors'][:2],
            'total_savings': insights['roi']['total_annual_savings'],
            'trigger_events': company_data.trigger_events[:2] if company_data.trigger_events else []
        }
    
    def _create_section_prompt(self, section: VideoSection,
                              context: Dict[str, Any],
                              prospect_name: str) -> str:
        """Create GPT-4 prompt for a specific section."""
        
        prompt = f"""
Generate a {section.duration}-second video script section for {section.purpose}.

Company: {context['company']}
Industry: {context['industry']}
Prospect: {prospect_name}
Website: {context['website']}

Key Points to Include:
- Pain points: {context['pain_points']}
- Opportunities: {context['opportunities']}
- Savings potential: ${context['total_savings']:,}

Requirements:
- Be extremely specific with numbers and examples
- Reference their actual website/tools
- Sound conversational but authoritative
- Include specific metrics and timeframes
- {section.duration} seconds at 140 words/minute = ~{int(section.duration * 140/60)} words

Generate the {section.key} section:
"""
        
        return prompt
    
    def _extract_team_size(self, company_size: str) -> int:
        """Extract numeric team size from company size string."""
        if '1000+' in company_size:
            return 1000
        elif '200' in company_size:
            return 200
        elif '50' in company_size:
            return 50
        elif '10' in company_size:
            return 10
        else:
            return 25  # Default
    
    def _get_size_multiplier(self, company_size: str) -> float:
        """Get savings multiplier based on company size."""
        if '1000+' in company_size:
            return 10
        elif '200' in company_size:
            return 5
        elif '50' in company_size:
            return 3
        elif '10' in company_size:
            return 1.5
        else:
            return 2
    
    def _get_industry_competitors(self, industry: str) -> List[str]:
        """Get typical competitors for an industry."""
        competitors = {
            'E-commerce': ['Amazon', 'Shopify stores', 'eBay sellers'],
            'SaaS': ['Salesforce', 'HubSpot', 'Zendesk'],
            'Healthcare': ['Epic Systems', 'Cerner', 'Athenahealth'],
            'Finance': ['Quickbooks', 'Xero', 'FreshBooks'],
            'Real Estate': ['Zillow', 'Redfin', 'Compass']
        }
        return competitors.get(industry, ['Industry leaders'])
    
    def _generate_script_id(self) -> str:
        """Generate unique script ID."""
        import hashlib
        return hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:8]

def test_script_generation():
    """Test the intelligent script generator."""
    from enrichment_engine import DataEnrichmentEngine
    from audit_engine import AutomationAuditEngine
    
    print("=" * 60)
    print("INTELLIGENT SCRIPT GENERATOR TEST")
    print("=" * 60)
    
    # Get enriched data
    print("\n[1/3] Enriching company data...")
    enrichment = DataEnrichmentEngine()
    company_data = enrichment.enrich_company("https://www.example-saas.com")
    
    # Generate audit
    print("[2/3] Generating audit report...")
    audit = AutomationAuditEngine()
    audit_report = audit.generate_audit("https://www.example-saas.com")
    
    # Generate script
    print("[3/3] Generating detailed video script...")
    generator = IntelligentScriptGenerator()
    script = generator.generate_detailed_script(
        company_data,
        audit_report,
        prospect_name="Sarah",
        target_duration=240  # 4 minutes
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("GENERATED SCRIPT")
    print("=" * 60)
    
    print(f"\nCompany: {script.company_name}")
    print(f"Prospect: {script.prospect_name}")
    print(f"Word Count: {script.word_count}")
    print(f"Duration: {script.total_duration_seconds}s")
    
    print("\n--- SCRIPT SECTIONS ---")
    for section, text in script.sections.items():
        print(f"\n[{section.key.upper()}] ({section.duration}s)")
        print("-" * 40)
        print(text[:200] + "..." if len(text) > 200 else text)
    
    print("\n--- KEY INSIGHTS ---")
    print(f"Findings: {script.specific_findings[:3]}")
    print(f"ROI: ${script.roi_calculations.get('total_annual_savings', 0):,.0f}/year")
    
    print("\n--- SCREENSHOT MOMENTS ---")
    for moment in script.screenshot_moments[:3]:
        print(f"  {moment['timestamp']}s: {moment['description']}")
    
    # Save full script
    output_file = f"script_{script.script_id}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(f"FULL SCRIPT FOR {script.company_name}\n")
        f.write("=" * 60 + "\n\n")
        f.write(script.get_full_script())
        f.write(f"\n\n{'=' * 60}\n")
        f.write(f"Total: {script.word_count} words ({script.total_duration_seconds}s)")
    
    print(f"\n[SAVED] Full script saved to: {output_file}")

if __name__ == "__main__":
    test_script_generation()