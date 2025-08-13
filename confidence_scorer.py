"""
confidence_scorer.py - VideoReach AI Confidence Scoring System
Phase 4: VRA-022 - Data quality and confidence tracking

This module provides comprehensive confidence scoring for all data points
and recommendations in the automation assessment pipeline.

Requirements:
- pip install numpy scipy
"""

import os
import sys
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import statistics
from enum import Enum

# Fix Windows Unicode issues
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

class DataSource(Enum):
    """Data source types with reliability weights."""
    DIRECT_SCRAPING = 0.95      # Direct website scraping
    API_VERIFIED = 0.90          # Verified API data (Clearbit, Apollo)
    PUBLIC_RECORDS = 0.85        # Public records and filings
    SOCIAL_MEDIA = 0.70          # Social media profiles
    NEWS_ARTICLES = 0.65         # News and press releases
    INFERENCE = 0.50             # Inferred from patterns
    ESTIMATION = 0.30            # Rough estimates
    UNKNOWN = 0.10               # Unknown source

class DataFreshness(Enum):
    """Data freshness levels with confidence multipliers."""
    REAL_TIME = 1.0             # < 1 hour old
    VERY_FRESH = 0.95           # < 24 hours old
    FRESH = 0.85                # < 7 days old
    RECENT = 0.70               # < 30 days old
    DATED = 0.50                # < 90 days old
    STALE = 0.30                # < 1 year old
    VERY_STALE = 0.10           # > 1 year old

@dataclass
class DataPoint:
    """Individual data point with confidence metadata."""
    field_name: str
    value: Any
    source: DataSource
    source_url: Optional[str] = None
    collected_at: datetime = field(default_factory=datetime.now)
    confidence: float = 0.0
    notes: Optional[str] = None
    
    def calculate_confidence(self) -> float:
        """Calculate confidence based on source and freshness."""
        # Base confidence from source
        source_confidence = self.source.value
        
        # Adjust for freshness
        age = datetime.now() - self.collected_at
        if age < timedelta(hours=1):
            freshness = DataFreshness.REAL_TIME
        elif age < timedelta(days=1):
            freshness = DataFreshness.VERY_FRESH
        elif age < timedelta(days=7):
            freshness = DataFreshness.FRESH
        elif age < timedelta(days=30):
            freshness = DataFreshness.RECENT
        elif age < timedelta(days=90):
            freshness = DataFreshness.DATED
        elif age < timedelta(days=365):
            freshness = DataFreshness.STALE
        else:
            freshness = DataFreshness.VERY_STALE
        
        freshness_multiplier = freshness.value
        
        # Calculate final confidence
        self.confidence = source_confidence * freshness_multiplier
        return self.confidence

@dataclass
class ConfidenceReport:
    """Complete confidence assessment for a company analysis."""
    overall_confidence: float = 0.0
    data_completeness: float = 0.0
    source_diversity: float = 0.0
    data_freshness: float = 0.0
    
    # Category-specific confidence scores
    company_info_confidence: float = 0.0
    technology_confidence: float = 0.0
    financial_confidence: float = 0.0
    market_confidence: float = 0.0
    automation_confidence: float = 0.0
    
    # Detailed breakdowns
    field_confidences: Dict[str, float] = field(default_factory=dict)
    missing_critical_data: List[str] = field(default_factory=list)
    low_confidence_fields: List[str] = field(default_factory=list)
    high_confidence_fields: List[str] = field(default_factory=list)
    
    # Recommendations
    confidence_warnings: List[str] = field(default_factory=list)
    data_improvement_suggestions: List[str] = field(default_factory=list)
    
    def get_confidence_level(self) -> str:
        """Get human-readable confidence level."""
        if self.overall_confidence >= 0.85:
            return "Very High"
        elif self.overall_confidence >= 0.70:
            return "High"
        elif self.overall_confidence >= 0.50:
            return "Moderate"
        elif self.overall_confidence >= 0.30:
            return "Low"
        else:
            return "Very Low"
    
    def is_reliable(self) -> bool:
        """Check if data is reliable enough for decision-making."""
        return self.overall_confidence >= 0.60

class ConfidenceScorer:
    """Main confidence scoring engine."""
    
    # Critical fields that must have high confidence
    CRITICAL_FIELDS = [
        'company_name', 'website', 'industry', 'company_size',
        'tech_stack', 'automation_opportunities'
    ]
    
    # Field importance weights
    FIELD_WEIGHTS = {
        'company_name': 1.0,
        'website': 1.0,
        'industry': 0.9,
        'company_size': 0.8,
        'tech_stack': 0.9,
        'revenue_range': 0.7,
        'founded_year': 0.5,
        'headquarters': 0.4,
        'automation_opportunities': 0.95,
        'digital_maturity_score': 0.85,
        'growth_signals': 0.7,
        'pain_indicators': 0.8,
        'trigger_events': 0.6,
        'competitors': 0.5,
        'recent_news': 0.4,
        'social_metrics': 0.3
    }
    
    def __init__(self):
        self.data_points: List[DataPoint] = []
        self.confidence_cache = {}
    
    def add_data_point(self, field_name: str, value: Any, source: DataSource,
                       source_url: Optional[str] = None, notes: Optional[str] = None) -> DataPoint:
        """Add a data point and calculate its confidence."""
        dp = DataPoint(
            field_name=field_name,
            value=value,
            source=source,
            source_url=source_url,
            notes=notes
        )
        dp.calculate_confidence()
        self.data_points.append(dp)
        return dp
    
    def score_enriched_data(self, enriched_data: Dict[str, Any]) -> ConfidenceReport:
        """Score confidence for enriched company data."""
        report = ConfidenceReport()
        
        # Analyze each field
        self._analyze_fields(enriched_data, report)
        
        # Calculate category confidences
        self._calculate_category_confidences(enriched_data, report)
        
        # Assess data quality metrics
        self._assess_data_quality(enriched_data, report)
        
        # Generate warnings and suggestions
        self._generate_recommendations(report)
        
        # Calculate overall confidence
        report.overall_confidence = self._calculate_overall_confidence(report)
        
        return report
    
    def score_automation_recommendation(self, recommendation: Dict[str, Any],
                                       supporting_data: List[DataPoint]) -> float:
        """Score confidence for a specific automation recommendation."""
        if not supporting_data:
            return 0.1
        
        # Calculate average confidence of supporting data
        confidences = [dp.confidence for dp in supporting_data]
        avg_confidence = statistics.mean(confidences) if confidences else 0.0
        
        # Adjust based on number of supporting points
        support_multiplier = min(1.0, len(supporting_data) / 3)  # Max at 3+ points
        
        # Adjust based on data source diversity
        unique_sources = len(set(dp.source for dp in supporting_data))
        diversity_multiplier = min(1.0, unique_sources / 2)  # Max at 2+ sources
        
        # Calculate final score
        confidence = avg_confidence * support_multiplier * diversity_multiplier
        
        return min(1.0, confidence)
    
    def _analyze_fields(self, data: Dict[str, Any], report: ConfidenceReport):
        """Analyze confidence for each field."""
        for field_name, value in data.items():
            if value is None or (isinstance(value, (list, dict)) and not value):
                # Missing or empty data
                confidence = 0.0
                if field_name in self.CRITICAL_FIELDS:
                    report.missing_critical_data.append(field_name)
            else:
                # Estimate confidence based on field type and content
                confidence = self._estimate_field_confidence(field_name, value)
            
            report.field_confidences[field_name] = confidence
            
            # Categorize by confidence level
            if confidence < 0.3:
                report.low_confidence_fields.append(field_name)
            elif confidence > 0.7:
                report.high_confidence_fields.append(field_name)
    
    def _estimate_field_confidence(self, field_name: str, value: Any) -> float:
        """Estimate confidence for a field based on its value."""
        base_confidence = 0.5  # Default moderate confidence
        
        # Adjust based on field type
        if field_name == 'company_name' and value:
            base_confidence = 0.95  # Company names from websites are reliable
        elif field_name == 'website' and value:
            base_confidence = 1.0  # Website URL is certain
        elif field_name == 'tech_stack' and isinstance(value, list):
            # Confidence based on number of technologies detected
            if len(value) > 10:
                base_confidence = 0.85
            elif len(value) > 5:
                base_confidence = 0.70
            else:
                base_confidence = 0.50
        elif field_name == 'industry' and value != 'Unknown':
            base_confidence = 0.75
        elif field_name == 'company_size' and value != 'Unknown':
            if any(num in str(value) for num in ['1', '5', '10', '50', '200', '1000']):
                base_confidence = 0.70  # Specific ranges are more confident
            else:
                base_confidence = 0.40
        elif field_name == 'digital_maturity_score' and isinstance(value, (int, float)):
            base_confidence = 0.65  # Calculated scores have moderate confidence
        elif field_name == 'automation_opportunities' and isinstance(value, list):
            if len(value) > 0:
                base_confidence = 0.70
        elif 'confidence' in field_name.lower():
            # If it's already a confidence score, use it directly
            return float(value) if isinstance(value, (int, float)) else 0.5
        
        # Apply field weight if available
        if field_name in self.FIELD_WEIGHTS:
            base_confidence *= self.FIELD_WEIGHTS[field_name]
        
        return min(1.0, base_confidence)
    
    def _calculate_category_confidences(self, data: Dict[str, Any], report: ConfidenceReport):
        """Calculate confidence scores for different categories."""
        # Company info confidence
        company_fields = ['company_name', 'website', 'industry', 'company_size',
                         'founded_year', 'headquarters', 'revenue_range']
        report.company_info_confidence = self._average_field_confidence(
            company_fields, report.field_confidences
        )
        
        # Technology confidence
        tech_fields = ['tech_stack', 'digital_maturity_score', 'tech_spend_estimate']
        report.technology_confidence = self._average_field_confidence(
            tech_fields, report.field_confidences
        )
        
        # Financial confidence
        financial_fields = ['revenue_range', 'funding_total', 'funding_stage', 'tech_spend_estimate']
        report.financial_confidence = self._average_field_confidence(
            financial_fields, report.field_confidences
        )
        
        # Market confidence
        market_fields = ['competitors', 'recent_news', 'job_postings', 'social_metrics']
        report.market_confidence = self._average_field_confidence(
            market_fields, report.field_confidences
        )
        
        # Automation confidence
        automation_fields = ['automation_opportunities', 'pain_indicators', 'growth_signals']
        report.automation_confidence = self._average_field_confidence(
            automation_fields, report.field_confidences
        )
    
    def _average_field_confidence(self, fields: List[str], 
                                  field_confidences: Dict[str, float]) -> float:
        """Calculate weighted average confidence for a set of fields."""
        total_weight = 0
        weighted_sum = 0
        
        for field in fields:
            if field in field_confidences:
                weight = self.FIELD_WEIGHTS.get(field, 0.5)
                confidence = field_confidences[field]
                weighted_sum += confidence * weight
                total_weight += weight
        
        if total_weight > 0:
            return weighted_sum / total_weight
        return 0.0
    
    def _assess_data_quality(self, data: Dict[str, Any], report: ConfidenceReport):
        """Assess overall data quality metrics."""
        # Data completeness
        total_fields = len(self.FIELD_WEIGHTS)
        filled_fields = sum(1 for field in self.FIELD_WEIGHTS if field in data and data.get(field))
        report.data_completeness = filled_fields / total_fields if total_fields > 0 else 0
        
        # Source diversity (simplified - would check actual sources in production)
        if 'enrichment_sources' in data:
            sources = data.get('enrichment_sources', [])
            report.source_diversity = min(1.0, len(sources) / 3)  # Max at 3+ sources
        else:
            report.source_diversity = 0.3  # Low diversity if no enrichment
        
        # Data freshness (simplified - would check timestamps in production)
        if 'last_updated' in data:
            last_updated = data.get('last_updated')
            if isinstance(last_updated, str):
                # Parse ISO format
                from datetime import datetime
                try:
                    last_updated = datetime.fromisoformat(last_updated)
                    age = datetime.now() - last_updated
                    if age < timedelta(days=1):
                        report.data_freshness = 1.0
                    elif age < timedelta(days=7):
                        report.data_freshness = 0.85
                    elif age < timedelta(days=30):
                        report.data_freshness = 0.70
                    else:
                        report.data_freshness = 0.50
                except:
                    report.data_freshness = 0.5
            else:
                report.data_freshness = 0.5
        else:
            report.data_freshness = 0.5
    
    def _generate_recommendations(self, report: ConfidenceReport):
        """Generate warnings and improvement suggestions."""
        # Warnings
        if report.overall_confidence < 0.5:
            report.confidence_warnings.append(
                "Overall confidence is low - recommendations should be validated with additional research"
            )
        
        if report.missing_critical_data:
            report.confidence_warnings.append(
                f"Missing critical data: {', '.join(report.missing_critical_data)}"
            )
        
        if report.data_completeness < 0.5:
            report.confidence_warnings.append(
                "Less than 50% of data fields are populated"
            )
        
        if report.source_diversity < 0.5:
            report.confidence_warnings.append(
                "Limited data source diversity - consider additional enrichment"
            )
        
        # Improvement suggestions
        if report.company_info_confidence < 0.7:
            report.data_improvement_suggestions.append(
                "Enrich company information using verified business databases"
            )
        
        if report.technology_confidence < 0.7:
            report.data_improvement_suggestions.append(
                "Perform deeper technology stack analysis with specialized tools"
            )
        
        if report.financial_confidence < 0.5:
            report.data_improvement_suggestions.append(
                "Add financial data from public filings or business intelligence sources"
            )
        
        if report.automation_confidence < 0.7:
            report.data_improvement_suggestions.append(
                "Conduct stakeholder interviews to validate automation opportunities"
            )
    
    def _calculate_overall_confidence(self, report: ConfidenceReport) -> float:
        """Calculate overall confidence score."""
        # Weighted average of different components
        components = [
            (report.company_info_confidence, 0.20),
            (report.technology_confidence, 0.25),
            (report.automation_confidence, 0.30),
            (report.data_completeness, 0.10),
            (report.source_diversity, 0.10),
            (report.data_freshness, 0.05)
        ]
        
        weighted_sum = sum(score * weight for score, weight in components)
        
        # Apply penalties for critical issues
        if report.missing_critical_data:
            weighted_sum *= 0.8  # 20% penalty for missing critical data
        
        if report.data_completeness < 0.3:
            weighted_sum *= 0.7  # 30% penalty for very incomplete data
        
        return min(1.0, max(0.0, weighted_sum))

class ConfidenceValidator:
    """Validate and adjust recommendations based on confidence."""
    
    @staticmethod
    def filter_recommendations(recommendations: List[Dict[str, Any]], 
                              min_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """Filter recommendations by minimum confidence threshold."""
        return [r for r in recommendations if r.get('confidence', 0) >= min_confidence]
    
    @staticmethod
    def adjust_roi_projections(roi: float, confidence: float) -> Tuple[float, float, float]:
        """Adjust ROI projections based on confidence level."""
        # Calculate conservative, likely, and optimistic scenarios
        conservative = roi * (confidence * 0.7)  # More conservative
        likely = roi * confidence  # Scaled by confidence
        optimistic = roi * min(1.0, confidence * 1.3)  # Less aggressive optimism
        
        return conservative, likely, optimistic
    
    @staticmethod
    def generate_confidence_disclaimer(confidence_level: str) -> str:
        """Generate appropriate disclaimer based on confidence level."""
        disclaimers = {
            "Very High": "Analysis based on comprehensive, verified data from multiple sources.",
            "High": "Analysis based on reliable data with good coverage across key metrics.",
            "Moderate": "Analysis based on available data; some assumptions made where data was limited.",
            "Low": "Analysis based on limited data; findings should be validated with additional research.",
            "Very Low": "Preliminary analysis only; significant data gaps require further investigation before decision-making."
        }
        return disclaimers.get(confidence_level, "Data confidence level unclear.")

def test_confidence_scoring():
    """Test the confidence scoring system."""
    scorer = ConfidenceScorer()
    
    # Add sample data points
    scorer.add_data_point(
        "company_name", "TechCorp",
        DataSource.DIRECT_SCRAPING,
        "https://techcorp.com"
    )
    
    scorer.add_data_point(
        "employee_count", 150,
        DataSource.INFERENCE,
        notes="Estimated from LinkedIn data"
    )
    
    scorer.add_data_point(
        "revenue_range", "$10M-$50M",
        DataSource.ESTIMATION,
        notes="Based on company size and industry"
    )
    
    # Test with sample enriched data
    sample_data = {
        "company_name": "TechCorp",
        "website": "https://techcorp.com",
        "industry": "Technology",
        "company_size": "51-200 employees",
        "tech_stack": ["react", "aws", "python", "postgresql"],
        "digital_maturity_score": 65,
        "automation_opportunities": [
            "CRM implementation",
            "Marketing automation",
            "DevOps pipeline"
        ],
        "revenue_range": "$10M-$50M",
        "founded_year": None,  # Missing data
        "headquarters": None,  # Missing data
        "last_updated": datetime.now().isoformat(),
        "enrichment_sources": ["LinkedIn", "Website", "NewsAPI"]
    }
    
    # Score the data
    report = scorer.score_enriched_data(sample_data)
    
    # Print report
    print("=" * 60)
    print("CONFIDENCE SCORING REPORT")
    print("=" * 60)
    
    print(f"\nOverall Confidence: {report.overall_confidence:.2%} ({report.get_confidence_level()})")
    print(f"Data Reliable for Decisions: {'Yes' if report.is_reliable() else 'No'}")
    
    print("\n== Category Confidence Scores ==")
    print(f"Company Info: {report.company_info_confidence:.2%}")
    print(f"Technology: {report.technology_confidence:.2%}")
    print(f"Financial: {report.financial_confidence:.2%}")
    print(f"Market: {report.market_confidence:.2%}")
    print(f"Automation: {report.automation_confidence:.2%}")
    
    print("\n== Data Quality Metrics ==")
    print(f"Completeness: {report.data_completeness:.2%}")
    print(f"Source Diversity: {report.source_diversity:.2%}")
    print(f"Data Freshness: {report.data_freshness:.2%}")
    
    if report.high_confidence_fields:
        print(f"\n== High Confidence Fields ==")
        for field in report.high_confidence_fields[:5]:
            print(f"  - {field}: {report.field_confidences[field]:.2%}")
    
    if report.low_confidence_fields:
        print(f"\n== Low Confidence Fields ==")
        for field in report.low_confidence_fields[:5]:
            print(f"  - {field}: {report.field_confidences[field]:.2%}")
    
    if report.missing_critical_data:
        print(f"\n== Missing Critical Data ==")
        for field in report.missing_critical_data:
            print(f"  - {field}")
    
    if report.confidence_warnings:
        print(f"\n== Warnings ==")
        for warning in report.confidence_warnings:
            print(f"  ⚠ {warning}")
    
    if report.data_improvement_suggestions:
        print(f"\n== Improvement Suggestions ==")
        for suggestion in report.data_improvement_suggestions:
            print(f"  → {suggestion}")
    
    # Test ROI adjustment
    print("\n== ROI Confidence Adjustment ==")
    base_roi = 250000
    conservative, likely, optimistic = ConfidenceValidator.adjust_roi_projections(
        base_roi, report.overall_confidence
    )
    print(f"Base ROI: ${base_roi:,.0f}")
    print(f"Conservative: ${conservative:,.0f}")
    print(f"Likely: ${likely:,.0f}")
    print(f"Optimistic: ${optimistic:,.0f}")
    
    # Test disclaimer
    print(f"\n== Confidence Disclaimer ==")
    disclaimer = ConfidenceValidator.generate_confidence_disclaimer(report.get_confidence_level())
    print(disclaimer)

if __name__ == "__main__":
    test_confidence_scoring()