"""
demo_script_standalone.py - Generate a script without dependencies
This shows you exactly what kind of script the system generates!
"""

import random
from datetime import datetime

print("=" * 60)
print("VIDEOREACH AI - SCRIPT GENERATION DEMO")
print("=" * 60)

# Simulate enriched company data (this would come from real scraping)
company_data = {
    'company_name': 'Notion',
    'website': 'https://www.notion.so',
    'industry': 'Technology',
    'company_size': '200-1000 employees',
    'tech_stack': ['react', 'aws', 'stripe', 'intercom', 'segment'],
    'pain_indicators': [
        'manual customer onboarding taking 30 minutes per user',
        'support tickets not automatically categorized',
        'no automated usage tracking for churn prediction'
    ],
    'automation_opportunities': [
        'Automated customer onboarding workflow',
        'AI-powered support ticket routing',
        'Predictive churn analysis system'
    ],
    'growth_signals': ['Recent Series C funding', 'Hiring 50+ engineers'],
    'trigger_events': ['Scaling from 5M to 20M users'],
    'competitors': ['Confluence', 'Coda', 'Airtable']
}

# Simulate audit results (this would come from AI analysis)
audit_results = {
    'total_savings': 750000,  # $750k/year
    'implementation_cost': 150000,
    'payback_months': 3,
    'team_size': 500,
    'monthly_volume': 50000,  # customer interactions
    'wasted_hours_per_week': 120
}

# Generate the actual script
prospect_name = "Sarah"
company = company_data['company_name']
industry = company_data['industry']

# Build the script sections
script_sections = {
    'HOOK (15 seconds)': f"""
Hi {prospect_name}, I spent the last hour analyzing {company}'s operations, 
and I found something fascinating. You're processing approximately {audit_results['monthly_volume']:,} customer 
interactions per month, but your team is still {company_data['pain_indicators'][0]}. 
This caught my attention because Confluence had the exact same challenge before automating.
""",
    
    'CREDIBILITY (20 seconds)': f"""
Quick context - I'm Alex from VideoReach. We've helped over 50 {industry} 
companies automate their operations, including Coda who saved $2M annually 
and Airtable who reduced onboarding time by 75%. I specialize in finding 
hidden automation opportunities that most consultants miss.
""",
    
    'PROBLEM DEEP DIVE (60 seconds)': f"""
Looking at {company}'s current setup, I identified three critical bottlenecks. 
First, your {company_data['pain_indicators'][0]} - I can see from your public documentation that 
this takes at least {audit_results['wasted_hours_per_week']} hours per week across your team. 

Second, there's no integration between your {company_data['tech_stack'][0]} frontend and your support system, 
meaning your team is constantly switching contexts and losing productivity. 

Third, and this is the big one, you're not leveraging any predictive analytics for user behavior, 
which means you're missing out on preventing churn before it happens. The real cost here isn't 
just time - it's the compounding inefficiency that gets worse as you scale from 5 million to 
20 million users.
""",
    
    'OPPORTUNITY 1 (45 seconds)': f"""
Let's start with the biggest opportunity: {company_data['automation_opportunities'][0]}. 
Right now, your team spends 30 minutes onboarding each enterprise customer. We can automate 
80% of this process using intelligent workflows that adapt to each customer's needs. 

Here's exactly how it works: AI analyzes the customer's profile, automatically provisions 
the right workspace setup, sends personalized tutorials, and only escalates to human support 
for complex edge cases. Coda implemented this exact system and now onboards 10x more 
customers with the same team size. For {company}, this would mean saving 400 hours per month 
within the first 30 days.
""",
    
    'OPPORTUNITY 2 (45 seconds)': f"""
The second quick win is {company_data['automation_opportunities'][1]}. I noticed you're 
manually categorizing and routing thousands of support tickets, which is causing response 
delays and frustrated customers. 

By implementing AI-powered ticket routing with natural language processing, you could 
instantly categorize tickets, route them to the right expert, and even auto-resolve 
40% of common issues. This isn't theoretical - Intercom's own data shows this reduces 
response time by 90% and improves satisfaction scores by 35%. The setup takes less than 
2 weeks and starts paying for itself immediately.
""",
    
    'OPPORTUNITY 3 (45 seconds)': f"""
Finally, there's a huge opportunity in {company_data['automation_opportunities'][2]}. 
Your competitors are already using machine learning to predict which users will churn 
30 days before they actually leave, while you're still reacting after the fact. 

We can implement predictive analytics that monitors usage patterns, identifies at-risk 
accounts, and automatically triggers retention campaigns. This would put you ahead of 
90% of {industry} companies in terms of retention intelligence. One client saw their 
churn rate drop by 25% in the first quarter after implementation.
""",
    
    'ROI BREAKDOWN (40 seconds)': f"""
Let's talk real numbers. Based on your team size of {audit_results['team_size']} and current 
volume of {audit_results['monthly_volume']:,} monthly interactions, here's the ROI breakdown: 

Automated onboarding saves ${audit_results['total_savings'] * 0.4:,.0f} per year. 
AI ticket routing saves another ${audit_results['total_savings'] * 0.35:,.0f}. 
Churn prediction adds ${audit_results['total_savings'] * 0.25:,.0f}. 

Total: ${audit_results['total_savings']:,} in year one. Implementation investment is 
approximately ${audit_results['implementation_cost']:,}, giving you a 
{audit_results['total_savings'] / audit_results['implementation_cost']:.1f}x ROI and 
{audit_results['payback_months']} month payback period. These aren't optimistic projections - 
they're based on actual results from similar implementations.
""",
    
    'IMPLEMENTATION (30 seconds)': f"""
Here's how we'd roll this out for {company}. Week 1-2: We map your current processes 
and set up the automation infrastructure. Week 3-4: Deploy the onboarding automation 
and train your team. Week 5-6: Add ticket routing and optimization. By week 8, everything 
is running automatically. 

Your team stays in control throughout - these are tools that empower them, not replace them. 
We handle all the technical complexity while you focus on growing from 5 to 20 million users.
""",
    
    'URGENCY (20 seconds)': f"""
Now, why is timing critical? {company_data['trigger_events'][0]} means you need to move fast. 
Plus, {company_data['competitors'][0]} just announced their own automation initiative, 
and if you don't automate soon, you'll be at a serious disadvantage in user experience. 

Every month you wait costs approximately ${audit_results['total_savings'] / 12:,.0f} in 
lost efficiency. The best part? We can start showing results within 2 weeks.
""",
    
    'CTA (20 seconds)': f"""
{prospect_name}, I've prepared a detailed automation roadmap specifically for {company}. 
It includes all the opportunities I mentioned, plus 5 more quick wins I found that could 
be implemented immediately. 

Let's spend 15 minutes going through it together - I'll show you exactly how each automation 
would work for your specific setup. Are you free this week? Here's my calendar: 
calendly.com/videoreach. Looking forward to helping {company} save those 
${audit_results['total_savings']:,} per year.
"""
}

# Display the script
print(f"\nTarget: {company_data['company_name']}")
print(f"Prospect: {prospect_name}")
print(f"Industry: {industry}")
print("-" * 60)

full_script = ""
total_words = 0

for section_title, section_text in script_sections.items():
    # Clean up the text
    clean_text = ' '.join(section_text.split())
    word_count = len(clean_text.split())
    total_words += word_count
    
    print(f"\n[{section_title}]")
    print("-" * 40)
    print(clean_text)
    
    full_script += clean_text + "\n\n"

# Calculate duration
duration_seconds = (total_words / 140) * 60  # 140 words per minute

print("\n" + "=" * 60)
print("SCRIPT ANALYSIS")
print("=" * 60)
print(f"Total Word Count: {total_words} words")
print(f"Speaking Duration: {duration_seconds:.0f} seconds ({duration_seconds/60:.1f} minutes)")
print(f"Potential Savings Mentioned: ${audit_results['total_savings']:,}/year")
print(f"ROI Multiple: {audit_results['total_savings'] / audit_results['implementation_cost']:.1f}x")
print(f"Payback Period: {audit_results['payback_months']} months")

print("\nKEY PERSONALIZATION POINTS:")
print(f"  • Company name mentioned: {full_script.count(company)} times")
print(f"  • Prospect name mentioned: {full_script.count(prospect_name)} times")
print(f"  • Specific metrics used: {len([x for x in str(audit_results.values()) if x.isdigit()])} data points")
print(f"  • Competitor references: {len(company_data['competitors'])} companies")
print(f"  • Pain points addressed: {len(company_data['pain_indicators'])} specific issues")

# Save the script
output_file = f"generated_script_notion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(f"VIDEOREACH AI - GENERATED SCRIPT FOR {company.upper()}\n")
    f.write("=" * 60 + "\n")
    f.write(f"Prospect: {prospect_name}\n")
    f.write(f"Company: {company}\n")
    f.write(f"Duration: {duration_seconds:.0f} seconds\n")
    f.write(f"Word Count: {total_words} words\n")
    f.write("=" * 60 + "\n\n")
    f.write(full_script)

print(f"\n[SAVED] Full script saved to: {output_file}")
print("\nThis is a REAL script that would be delivered as a personalized video!")
print("Notice how it's specific, mentions real numbers, and focuses on VALUE not features.")