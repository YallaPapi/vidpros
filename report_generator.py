"""
report_generator.py - VideoReach AI Report Generation Engine
Phase 4: VRA-021 - Professional report generation with visualizations

This module generates comprehensive automation assessment reports in multiple formats.
Combines data from research, enrichment, and audit engines into actionable reports.

Requirements:
- pip install jinja2 weasyprint plotly pandas
- For PDF: WeasyPrint requires GTK (see https://weasyprint.readthedocs.io/en/stable/install.html)
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import base64
from io import BytesIO

# Import our engines
from research_engine import ResearchEngine
from enrichment_engine import DataEnrichmentEngine, EnrichedCompanyData
from audit_engine import AutomationAuditEngine, AutomationAuditReport

# Fix Windows Unicode issues
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# HTML templating
from jinja2 import Template, Environment, FileSystemLoader

# Try to import PDF generation (optional)
try:
    from weasyprint import HTML as WeasyHTML
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("[WARNING] WeasyPrint not available - PDF generation disabled")

# Try to import visualization library (optional)
try:
    import plotly.graph_objects as go
    import plotly.io as pio
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    print("[WARNING] Plotly not available - visualizations disabled")

@dataclass
class ComprehensiveReport:
    """Complete automation assessment report structure."""
    # Meta information
    report_id: str
    generated_at: datetime
    company_name: str
    website: str
    
    # Core data from engines
    enriched_data: EnrichedCompanyData
    audit_report: AutomationAuditReport
    
    # Visualizations
    charts: Dict[str, str] = None  # Base64 encoded chart images
    
    # Executive summary
    executive_summary: str = ""
    key_findings: List[str] = None
    critical_recommendations: List[str] = None
    
    # ROI projections
    total_savings_potential: float = 0
    implementation_cost: float = 0
    payback_period_months: int = 0
    
    # Risk assessment
    implementation_risks: List[str] = None
    success_factors: List[str] = None
    
    # Next steps
    immediate_actions: List[str] = None
    thirty_day_plan: List[str] = None
    ninety_day_plan: List[str] = None
    
    def __post_init__(self):
        if self.key_findings is None:
            self.key_findings = []
        if self.critical_recommendations is None:
            self.critical_recommendations = []
        if self.implementation_risks is None:
            self.implementation_risks = []
        if self.success_factors is None:
            self.success_factors = []
        if self.immediate_actions is None:
            self.immediate_actions = []
        if self.thirty_day_plan is None:
            self.thirty_day_plan = []
        if self.ninety_day_plan is None:
            self.ninety_day_plan = []
        if self.charts is None:
            self.charts = {}

class VisualizationGenerator:
    """Generate charts and visualizations for reports."""
    
    def __init__(self):
        self.enabled = PLOTLY_AVAILABLE
    
    def generate_all_charts(self, report: ComprehensiveReport) -> Dict[str, str]:
        """Generate all charts for the report."""
        if not self.enabled:
            return {}
        
        charts = {}
        
        # 1. Digital Maturity Radar Chart
        charts['maturity_radar'] = self._create_maturity_radar(report)
        
        # 2. ROI Timeline Chart
        charts['roi_timeline'] = self._create_roi_timeline(report)
        
        # 3. Tech Stack Comparison
        charts['tech_stack'] = self._create_tech_stack_chart(report)
        
        # 4. Automation Opportunities Impact Matrix
        charts['impact_matrix'] = self._create_impact_matrix(report)
        
        # 5. Cost Savings Breakdown
        charts['savings_breakdown'] = self._create_savings_breakdown(report)
        
        return charts
    
    def _create_maturity_radar(self, report: ComprehensiveReport) -> str:
        """Create digital maturity radar chart."""
        categories = ['Technology', 'Processes', 'Data', 'People', 'Strategy']
        
        # Calculate scores based on report data
        current_scores = [
            report.enriched_data.digital_maturity_score or 50,
            self._calculate_process_maturity(report),
            self._calculate_data_maturity(report),
            self._calculate_people_maturity(report),
            self._calculate_strategy_maturity(report)
        ]
        
        # Industry benchmark (hypothetical)
        benchmark_scores = [75, 70, 65, 60, 70]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=current_scores,
            theta=categories,
            fill='toself',
            name='Current State',
            line_color='blue'
        ))
        
        fig.add_trace(go.Scatterpolar(
            r=benchmark_scores,
            theta=categories,
            fill='toself',
            name='Industry Benchmark',
            line_color='green',
            opacity=0.5
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )),
            showlegend=True,
            title="Digital Maturity Assessment"
        )
        
        return self._fig_to_base64(fig)
    
    def _create_roi_timeline(self, report: ComprehensiveReport) -> str:
        """Create ROI timeline chart."""
        months = list(range(1, 25))  # 24 months
        
        # Calculate cumulative costs and savings
        implementation_cost = report.implementation_cost or 50000
        monthly_savings = (report.total_savings_potential or 100000) / 12
        
        cumulative_cost = [implementation_cost] * len(months)
        cumulative_savings = [monthly_savings * m for m in months]
        net_benefit = [s - implementation_cost for s in cumulative_savings]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=months,
            y=cumulative_cost,
            mode='lines',
            name='Implementation Cost',
            line=dict(color='red', dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=months,
            y=cumulative_savings,
            mode='lines',
            name='Cumulative Savings',
            line=dict(color='green')
        ))
        
        fig.add_trace(go.Scatter(
            x=months,
            y=net_benefit,
            mode='lines',
            name='Net Benefit',
            line=dict(color='blue', width=3)
        ))
        
        # Add break-even point
        break_even_month = next((i for i, v in enumerate(net_benefit) if v > 0), None)
        if break_even_month:
            fig.add_vline(x=break_even_month + 1, line_dash="dot", 
                         annotation_text=f"Break-even: Month {break_even_month + 1}")
        
        fig.update_layout(
            title="ROI Timeline (24 Months)",
            xaxis_title="Months",
            yaxis_title="Amount ($)",
            hovermode='x unified'
        )
        
        return self._fig_to_base64(fig)
    
    def _create_tech_stack_chart(self, report: ComprehensiveReport) -> str:
        """Create technology stack comparison chart."""
        current_tech = report.enriched_data.tech_stack[:10]  # Top 10
        recommended_tech = ['Zapier', 'HubSpot', 'Slack', 'Tableau', 'AWS']  # Example
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Current Stack',
            x=current_tech,
            y=[1] * len(current_tech),
            marker_color='lightblue'
        ))
        
        fig.add_trace(go.Bar(
            name='Recommended Additions',
            x=recommended_tech,
            y=[1] * len(recommended_tech),
            marker_color='lightgreen'
        ))
        
        fig.update_layout(
            title="Technology Stack Analysis",
            xaxis_title="Technologies",
            yaxis_title="",
            yaxis=dict(showticklabels=False),
            barmode='group'
        )
        
        return self._fig_to_base64(fig)
    
    def _create_impact_matrix(self, report: ComprehensiveReport) -> str:
        """Create automation opportunities impact matrix."""
        opportunities = report.enriched_data.automation_opportunities[:5]
        
        # Assign impact and effort scores (would be calculated in real implementation)
        impact_scores = [85, 70, 60, 75, 65]
        effort_scores = [30, 50, 70, 40, 60]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=effort_scores,
            y=impact_scores,
            mode='markers+text',
            text=opportunities,
            textposition="top center",
            marker=dict(
                size=20,
                color=impact_scores,
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title="Impact")
            )
        ))
        
        # Add quadrant lines
        fig.add_hline(y=50, line_dash="dot", opacity=0.3)
        fig.add_vline(x=50, line_dash="dot", opacity=0.3)
        
        # Add quadrant labels
        fig.add_annotation(x=25, y=75, text="Quick Wins", showarrow=False, font=dict(size=12, color="green"))
        fig.add_annotation(x=75, y=75, text="Major Projects", showarrow=False, font=dict(size=12, color="orange"))
        fig.add_annotation(x=25, y=25, text="Fill-ins", showarrow=False, font=dict(size=12, color="gray"))
        fig.add_annotation(x=75, y=25, text="Low Priority", showarrow=False, font=dict(size=12, color="red"))
        
        fig.update_layout(
            title="Automation Opportunities: Impact vs Effort",
            xaxis_title="Implementation Effort →",
            yaxis_title="Business Impact →",
            xaxis=dict(range=[0, 100]),
            yaxis=dict(range=[0, 100])
        )
        
        return self._fig_to_base64(fig)
    
    def _create_savings_breakdown(self, report: ComprehensiveReport) -> str:
        """Create savings breakdown pie chart."""
        categories = ['Labor Cost Reduction', 'Error Reduction', 'Speed Improvement', 
                     'Scalability Gains', 'Customer Satisfaction']
        values = [40, 20, 15, 15, 10]  # Percentage breakdown
        
        fig = go.Figure(data=[go.Pie(
            labels=categories,
            values=values,
            hole=.3
        )])
        
        fig.update_layout(
            title="Projected Savings Breakdown",
            annotations=[dict(text='Savings', x=0.5, y=0.5, font_size=20, showarrow=False)]
        )
        
        return self._fig_to_base64(fig)
    
    def _fig_to_base64(self, fig) -> str:
        """Convert Plotly figure to base64 string."""
        img_bytes = pio.to_image(fig, format='png', width=800, height=500)
        img_base64 = base64.b64encode(img_bytes).decode('utf-8')
        return f"data:image/png;base64,{img_base64}"
    
    def _calculate_process_maturity(self, report: ComprehensiveReport) -> int:
        """Calculate process maturity score."""
        score = 40  # Base score
        
        # Adjust based on automation opportunities
        if len(report.enriched_data.automation_opportunities) > 3:
            score -= 10  # Many opportunities means low current maturity
        
        # Adjust based on tech stack
        if 'zapier' in [t.lower() for t in report.enriched_data.tech_stack]:
            score += 15
        
        return min(100, max(0, score))
    
    def _calculate_data_maturity(self, report: ComprehensiveReport) -> int:
        """Calculate data maturity score."""
        score = 35  # Base score
        
        # Check for analytics tools
        analytics_tools = ['google_analytics', 'tableau', 'powerbi', 'looker']
        for tool in analytics_tools:
            if tool in [t.lower() for t in report.enriched_data.tech_stack]:
                score += 10
        
        return min(100, max(0, score))
    
    def _calculate_people_maturity(self, report: ComprehensiveReport) -> int:
        """Calculate people/culture maturity score."""
        # Based on company size and growth
        score = 45  # Base score
        
        if report.enriched_data.employee_growth and report.enriched_data.employee_growth > 20:
            score += 10  # Growing companies often have adaptive cultures
        
        return min(100, max(0, score))
    
    def _calculate_strategy_maturity(self, report: ComprehensiveReport) -> int:
        """Calculate strategy maturity score."""
        score = 50  # Base score
        
        # Adjust based on digital presence
        if report.enriched_data.digital_maturity_score:
            score = (score + report.enriched_data.digital_maturity_score) // 2
        
        return min(100, max(0, score))

class ReportGenerator:
    """Main report generation engine."""
    
    def __init__(self):
        self.research_engine = ResearchEngine()
        self.enrichment_engine = DataEnrichmentEngine()
        self.audit_engine = AutomationAuditEngine()
        self.viz_generator = VisualizationGenerator()
        
        # Setup Jinja2 templates
        self.template_dir = "report_templates"
        os.makedirs(self.template_dir, exist_ok=True)
        self._create_default_templates()
        
        self.env = Environment(loader=FileSystemLoader(self.template_dir))
    
    def generate_comprehensive_report(self, website_url: str) -> ComprehensiveReport:
        """
        Generate a comprehensive automation assessment report.
        
        Args:
            website_url: Target company website
            
        Returns:
            ComprehensiveReport object with all data and visualizations
        """
        print(f"[REPORT] Generating comprehensive report for: {website_url}")
        start_time = time.time()
        
        # 1. Gather enriched data
        print("[STEP 1/4] Enriching company data...")
        enriched_data = self.enrichment_engine.enrich_company(website_url)
        
        # 2. Generate audit report
        print("[STEP 2/4] Running automation audit...")
        audit_report = self.audit_engine.generate_audit(website_url)
        
        # 3. Create report structure
        report = ComprehensiveReport(
            report_id=self._generate_report_id(),
            generated_at=datetime.now(),
            company_name=enriched_data.company_name,
            website=website_url,
            enriched_data=enriched_data,
            audit_report=audit_report
        )
        
        # 4. Generate executive summary and recommendations
        print("[STEP 3/4] Generating insights and recommendations...")
        self._generate_executive_summary(report)
        self._generate_key_findings(report)
        self._generate_recommendations(report)
        self._calculate_roi_metrics(report)
        self._assess_risks_and_success_factors(report)
        self._create_action_plans(report)
        
        # 5. Generate visualizations
        print("[STEP 4/4] Creating visualizations...")
        report.charts = self.viz_generator.generate_all_charts(report)
        
        elapsed = time.time() - start_time
        print(f"[COMPLETE] Report generated in {elapsed:.1f} seconds")
        
        return report
    
    def export_html(self, report: ComprehensiveReport, output_file: str = None) -> str:
        """Export report as HTML."""
        if not output_file:
            output_file = f"report_{report.company_name.lower().replace(' ', '_')}_{report.report_id}.html"
        
        template = self.env.get_template('report_template.html')
        html_content = template.render(report=report)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"[EXPORT] HTML report saved to: {output_file}")
        return output_file
    
    def export_pdf(self, report: ComprehensiveReport, output_file: str = None) -> Optional[str]:
        """Export report as PDF (requires WeasyPrint)."""
        if not WEASYPRINT_AVAILABLE:
            print("[ERROR] PDF export not available - WeasyPrint not installed")
            return None
        
        if not output_file:
            output_file = f"report_{report.company_name.lower().replace(' ', '_')}_{report.report_id}.pdf"
        
        # First generate HTML
        html_file = self.export_html(report, output_file.replace('.pdf', '.html'))
        
        # Convert to PDF
        try:
            WeasyHTML(filename=html_file).write_pdf(output_file)
            print(f"[EXPORT] PDF report saved to: {output_file}")
            return output_file
        except Exception as e:
            print(f"[ERROR] PDF generation failed: {e}")
            return None
    
    def export_json(self, report: ComprehensiveReport, output_file: str = None) -> str:
        """Export report as JSON."""
        if not output_file:
            output_file = f"report_{report.company_name.lower().replace(' ', '_')}_{report.report_id}.json"
        
        # Convert to dict and handle datetime
        report_dict = asdict(report)
        report_dict['generated_at'] = report_dict['generated_at'].isoformat()
        report_dict['enriched_data']['last_updated'] = report_dict['enriched_data']['last_updated'].isoformat()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2)
        
        print(f"[EXPORT] JSON report saved to: {output_file}")
        return output_file
    
    def _generate_report_id(self) -> str:
        """Generate unique report ID."""
        import uuid
        return str(uuid.uuid4())[:8]
    
    def _generate_executive_summary(self, report: ComprehensiveReport):
        """Generate executive summary."""
        summary_parts = []
        
        # Company overview
        summary_parts.append(
            f"{report.company_name} is a {report.enriched_data.industry} company "
            f"with {report.enriched_data.company_size}."
        )
        
        # Digital maturity
        if report.enriched_data.digital_maturity_score:
            maturity_level = "high" if report.enriched_data.digital_maturity_score > 70 else \
                            "moderate" if report.enriched_data.digital_maturity_score > 40 else "low"
            summary_parts.append(
                f"The company demonstrates {maturity_level} digital maturity "
                f"({report.enriched_data.digital_maturity_score}/100)."
            )
        
        # Automation potential
        opp_count = len(report.enriched_data.automation_opportunities)
        if opp_count > 0:
            summary_parts.append(
                f"We identified {opp_count} key automation opportunities that could "
                f"deliver significant operational improvements."
            )
        
        # ROI potential
        if report.total_savings_potential:
            summary_parts.append(
                f"Implementing recommended automations could generate "
                f"${report.total_savings_potential:,.0f} in annual savings."
            )
        
        report.executive_summary = " ".join(summary_parts)
    
    def _generate_key_findings(self, report: ComprehensiveReport):
        """Generate key findings."""
        findings = []
        
        # Technology gaps
        if len(report.enriched_data.tech_stack) < 10:
            findings.append("Limited technology adoption indicates significant automation potential")
        
        # Growth indicators
        if report.enriched_data.growth_signals:
            findings.append(f"Company shows strong growth signals: {', '.join(report.enriched_data.growth_signals[:2])}")
        
        # Pain points
        if report.enriched_data.pain_indicators:
            findings.append(f"Key operational challenges identified: {report.enriched_data.pain_indicators[0]}")
        
        # Industry comparison
        findings.append(f"Digital maturity below industry average presents competitive risk")
        
        # Trigger events
        if report.enriched_data.trigger_events:
            findings.append(f"Recent trigger event creates automation urgency: {report.enriched_data.trigger_events[0]}")
        
        report.key_findings = findings[:5]
    
    def _generate_recommendations(self, report: ComprehensiveReport):
        """Generate critical recommendations."""
        recommendations = []
        
        # Based on automation opportunities
        for opp in report.enriched_data.automation_opportunities[:3]:
            recommendations.append(f"Implement {opp}")
        
        # Based on tech gaps
        if 'crm' not in ' '.join(report.enriched_data.tech_stack).lower():
            recommendations.append("Deploy CRM system for customer relationship management")
        
        # Based on maturity score
        if report.enriched_data.digital_maturity_score and report.enriched_data.digital_maturity_score < 50:
            recommendations.append("Establish digital transformation roadmap and governance")
        
        report.critical_recommendations = recommendations[:5]
    
    def _calculate_roi_metrics(self, report: ComprehensiveReport):
        """Calculate ROI metrics."""
        # Estimate based on company size and opportunities
        base_savings = 50000  # Base annual savings
        
        # Adjust for company size
        if "1000+" in report.enriched_data.company_size:
            multiplier = 5
        elif "200" in report.enriched_data.company_size:
            multiplier = 3
        elif "50" in report.enriched_data.company_size:
            multiplier = 2
        else:
            multiplier = 1
        
        # Adjust for number of opportunities
        opp_multiplier = min(3, len(report.enriched_data.automation_opportunities) * 0.5)
        
        report.total_savings_potential = base_savings * multiplier * opp_multiplier
        report.implementation_cost = report.total_savings_potential * 0.3  # 30% of savings
        report.payback_period_months = int((report.implementation_cost / report.total_savings_potential) * 12)
    
    def _assess_risks_and_success_factors(self, report: ComprehensiveReport):
        """Assess implementation risks and success factors."""
        # Risks
        risks = []
        if report.enriched_data.digital_maturity_score and report.enriched_data.digital_maturity_score < 40:
            risks.append("Low digital maturity may require additional change management")
        risks.append("Integration complexity with existing systems")
        risks.append("User adoption and training requirements")
        
        # Success factors
        success = []
        if report.enriched_data.growth_signals:
            success.append("Strong growth momentum supports transformation investment")
        success.append("Executive sponsorship and clear governance")
        success.append("Phased implementation approach with quick wins")
        
        report.implementation_risks = risks
        report.success_factors = success
    
    def _create_action_plans(self, report: ComprehensiveReport):
        """Create phased action plans."""
        # Immediate actions (0-7 days)
        report.immediate_actions = [
            "Schedule stakeholder alignment meeting",
            "Audit current technology stack and integrations",
            "Identify automation champions within organization"
        ]
        
        # 30-day plan
        report.thirty_day_plan = [
            "Complete detailed process mapping for top 3 automation opportunities",
            "Vendor evaluation and proof-of-concept planning",
            "Develop business case with detailed ROI projections"
        ]
        
        # 90-day plan
        report.ninety_day_plan = [
            "Launch pilot automation project",
            "Establish automation center of excellence",
            "Implement measurement framework and KPIs"
        ]
    
    def _create_default_templates(self):
        """Create default HTML template."""
        template_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Automation Assessment Report - {{ report.company_name }}</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; max-width: 1200px; margin: 0 auto; padding: 20px; }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 10px; margin-bottom: 30px; }
        .summary-box { background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #3498db; }
        .metric { display: inline-block; margin: 10px 20px; padding: 15px; background: white; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-value { font-size: 24px; font-weight: bold; color: #2c3e50; }
        .metric-label { font-size: 12px; color: #7f8c8d; text-transform: uppercase; }
        .chart-container { margin: 30px 0; text-align: center; }
        .recommendations { background: #e8f5e9; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .recommendation-item { margin: 10px 0; padding-left: 20px; position: relative; }
        .recommendation-item:before { content: "✓"; position: absolute; left: 0; color: #27ae60; font-weight: bold; }
        .risk-item { color: #e74c3c; }
        .success-item { color: #27ae60; }
        .footer { margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; text-align: center; color: #7f8c8d; }
        @media print { body { max-width: 100%; } .header { background: #667eea; } }
    </style>
</head>
<body>
    <div class="header">
        <h1>Automation Assessment Report</h1>
        <h2 style="color: white; border: none;">{{ report.company_name }}</h2>
        <p>Report ID: {{ report.report_id }} | Generated: {{ report.generated_at.strftime('%B %d, %Y') }}</p>
    </div>

    <div class="summary-box">
        <h2>Executive Summary</h2>
        <p>{{ report.executive_summary }}</p>
    </div>

    <div class="metrics">
        <div class="metric">
            <div class="metric-value">${{ "{:,.0f}".format(report.total_savings_potential) }}</div>
            <div class="metric-label">Annual Savings Potential</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ report.payback_period_months }} months</div>
            <div class="metric-label">Payback Period</div>
        </div>
        <div class="metric">
            <div class="metric-value">{{ report.enriched_data.digital_maturity_score }}/100</div>
            <div class="metric-label">Digital Maturity</div>
        </div>
    </div>

    <h2>Key Findings</h2>
    <ul>
        {% for finding in report.key_findings %}
        <li>{{ finding }}</li>
        {% endfor %}
    </ul>

    {% if report.charts.get('maturity_radar') %}
    <div class="chart-container">
        <h2>Digital Maturity Assessment</h2>
        <img src="{{ report.charts['maturity_radar'] }}" alt="Digital Maturity Radar Chart" style="max-width: 100%;">
    </div>
    {% endif %}

    <div class="recommendations">
        <h2>Critical Recommendations</h2>
        {% for rec in report.critical_recommendations %}
        <div class="recommendation-item">{{ rec }}</div>
        {% endfor %}
    </div>

    {% if report.charts.get('roi_timeline') %}
    <div class="chart-container">
        <h2>ROI Timeline</h2>
        <img src="{{ report.charts['roi_timeline'] }}" alt="ROI Timeline" style="max-width: 100%;">
    </div>
    {% endif %}

    <h2>Automation Opportunities</h2>
    <ul>
        {% for opp in report.enriched_data.automation_opportunities %}
        <li>{{ opp }}</li>
        {% endfor %}
    </ul>

    {% if report.charts.get('impact_matrix') %}
    <div class="chart-container">
        <h2>Impact vs Effort Analysis</h2>
        <img src="{{ report.charts['impact_matrix'] }}" alt="Impact Matrix" style="max-width: 100%;">
    </div>
    {% endif %}

    <h2>Implementation Roadmap</h2>
    
    <h3>Immediate Actions (0-7 days)</h3>
    <ul>
        {% for action in report.immediate_actions %}
        <li>{{ action }}</li>
        {% endfor %}
    </ul>

    <h3>30-Day Plan</h3>
    <ul>
        {% for action in report.thirty_day_plan %}
        <li>{{ action }}</li>
        {% endfor %}
    </ul>

    <h3>90-Day Plan</h3>
    <ul>
        {% for action in report.ninety_day_plan %}
        <li>{{ action }}</li>
        {% endfor %}
    </ul>

    <h2>Risk Assessment</h2>
    <div style="display: flex; gap: 40px;">
        <div style="flex: 1;">
            <h3>Implementation Risks</h3>
            <ul>
                {% for risk in report.implementation_risks %}
                <li class="risk-item">{{ risk }}</li>
                {% endfor %}
            </ul>
        </div>
        <div style="flex: 1;">
            <h3>Success Factors</h3>
            <ul>
                {% for factor in report.success_factors %}
                <li class="success-item">{{ factor }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>

    <div class="footer">
        <p>© 2024 VideoReach AI - Confidential Automation Assessment</p>
        <p>This report contains proprietary analysis and recommendations.</p>
    </div>
</body>
</html>'''
        
        template_path = os.path.join(self.template_dir, 'report_template.html')
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)

def main():
    """Test the report generator."""
    generator = ReportGenerator()
    
    test_companies = [
        "https://www.shopify.com",
        "https://www.airbnb.com"
    ]
    
    for url in test_companies[:1]:  # Test with one company
        print("\n" + "=" * 60)
        print(f"[TEST] Generating report for: {url}")
        print("=" * 60)
        
        # Generate comprehensive report
        report = generator.generate_comprehensive_report(url)
        
        # Export in multiple formats
        html_file = generator.export_html(report)
        json_file = generator.export_json(report)
        pdf_file = generator.export_pdf(report)  # May fail if WeasyPrint not installed
        
        # Print summary
        print("\n[SUMMARY]")
        print(f"Company: {report.company_name}")
        print(f"Savings Potential: ${report.total_savings_potential:,.0f}")
        print(f"Payback Period: {report.payback_period_months} months")
        print(f"Automation Opportunities: {len(report.enriched_data.automation_opportunities)}")
        print(f"Digital Maturity: {report.enriched_data.digital_maturity_score}/100")
        
        print("\n[EXPORTS]")
        print(f"HTML: {html_file}")
        print(f"JSON: {json_file}")
        if pdf_file:
            print(f"PDF: {pdf_file}")

if __name__ == "__main__":
    main()