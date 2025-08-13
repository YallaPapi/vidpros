"""
generate_script_demo.py - Generate a real script from website analysis
This will show you what the system actually produces!
"""

import os
import sys
from datetime import datetime

# Fix Windows Unicode issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("VIDEOREACH AI - SCRIPT GENERATION DEMO")
print("=" * 60)

# Import our modules
from intelligent_script_generator import IntelligentScriptGenerator
from enrichment_engine import DataEnrichmentEngine
from audit_engine import AutomationAuditEngine

# Pick a real company to analyze
target_url = "https://www.notion.so"  # Popular SaaS company
prospect_name = "Sarah"
target_duration = 240  # 4 minutes

print(f"\nTarget Company: {target_url}")
print(f"Prospect Name: {prospect_name}")
print(f"Target Duration: {target_duration} seconds")
print("-" * 60)

# Step 1: Enrich company data
print("\n[STEP 1/3] Analyzing company website...")
enrichment_engine = DataEnrichmentEngine()
company_data = enrichment_engine.enrich_company(target_url)

print(f"Company: {company_data.company_name}")
print(f"Industry: {company_data.industry}")
print(f"Size: {company_data.company_size}")
print(f"Tech Stack: {', '.join(company_data.tech_stack[:5]) if company_data.tech_stack else 'None detected'}")

# Step 2: Generate automation audit
print("\n[STEP 2/3] Running automation audit...")
audit_engine = AutomationAuditEngine()
audit_report = audit_engine.generate_audit(target_url)

print(f"Opportunities Found: {len(audit_report.opportunities)}")
if audit_report.opportunities:
    for i, opp in enumerate(audit_report.opportunities[:3], 1):
        print(f"  {i}. {opp.name}")

# Step 3: Generate detailed script
print("\n[STEP 3/3] Generating personalized script...")
script_generator = IntelligentScriptGenerator()
script = script_generator.generate_detailed_script(
    company_data,
    audit_report,
    prospect_name=prospect_name,
    target_duration=target_duration
)

# Display the full script
print("\n" + "=" * 60)
print("GENERATED SCRIPT")
print("=" * 60)
print(f"Company: {script.company_name}")
print(f"Prospect: {script.prospect_name}")
print(f"Word Count: {script.word_count} words")
print(f"Speaking Duration: {script.total_duration_seconds} seconds")
print("-" * 60)

# Show each section
from intelligent_script_generator import VideoSection

for section in VideoSection:
    if section in script.sections:
        print(f"\n[{section.key.upper()}] ({section.duration}s - {section.purpose})")
        print("-" * 40)
        print(script.sections[section])

# Show key metrics
print("\n" + "=" * 60)
print("SCRIPT ANALYSIS")
print("=" * 60)

print("\nKEY FINDINGS USED:")
for finding in script.specific_findings[:5]:
    print(f"  • {finding}")

print("\nROI CALCULATIONS:")
for metric, value in script.roi_calculations.items():
    if isinstance(value, (int, float)):
        print(f"  • {metric}: ${value:,.0f}")

print("\nSCREENSHOT MOMENTS:")
for moment in script.screenshot_moments[:3]:
    print(f"  • {moment['timestamp']}s: {moment['description']}")

# Save the full script
output_file = f"generated_script_{script.script_id}.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"VIDEOREACH AI - GENERATED SCRIPT\n")
    f.write(f"Company: {script.company_name}\n")
    f.write(f"Prospect: {script.prospect_name}\n")
    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    f.write("=" * 60 + "\n\n")
    f.write(script.get_full_script())
    f.write(f"\n\n{'=' * 60}\n")
    f.write(f"Word Count: {script.word_count}\n")
    f.write(f"Duration: {script.total_duration_seconds} seconds\n")

print(f"\n[SAVED] Full script saved to: {output_file}")
print("\nThis is what would be turned into a video with avatar + screenshots!")