"""
test_full_pipeline.py - Test what actually works with current API keys
Let's see what we can actually generate!
"""

import os
import sys
from dotenv import load_dotenv

# Fix Windows Unicode issues
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

load_dotenv()

def test_research():
    """Test website research - should work!"""
    print("\n[TEST 1] Website Research")
    print("-" * 40)
    
    try:
        from research_engine import research_prospect
        data = research_prospect("https://www.shopify.com")
        print(f"✅ Research works! Found: {data.get('company_name')}")
        print(f"   Tech stack: {', '.join(data.get('tech_stack', [])[:5])}")
        return True
    except Exception as e:
        print(f"❌ Research failed: {e}")
        return False

def test_enrichment():
    """Test enrichment - should work with public data!"""
    print("\n[TEST 2] Company Enrichment")
    print("-" * 40)
    
    try:
        from enrichment_engine import DataEnrichmentEngine
        engine = DataEnrichmentEngine()
        enriched = engine.enrich_company("https://www.shopify.com")
        print(f"✅ Enrichment works! Industry: {enriched.industry}")
        print(f"   Opportunities: {len(enriched.automation_opportunities)}")
        return True
    except Exception as e:
        print(f"❌ Enrichment failed: {e}")
        return False

def test_audit():
    """Test audit generation - should work!"""
    print("\n[TEST 3] Automation Audit")
    print("-" * 40)
    
    try:
        from audit_engine import AutomationAuditEngine
        engine = AutomationAuditEngine()
        audit = engine.generate_audit("https://www.shopify.com")
        print(f"✅ Audit works! Found {len(audit.opportunities)} opportunities")
        if audit.opportunities:
            print(f"   Top opportunity: {audit.opportunities[0].name}")
        return True
    except Exception as e:
        print(f"❌ Audit failed: {e}")
        return False

def test_script_generation():
    """Test script generation - template version should work!"""
    print("\n[TEST 4] Script Generation")
    print("-" * 40)
    
    try:
        from intelligent_script_generator import IntelligentScriptGenerator
        from enrichment_engine import DataEnrichmentEngine
        from audit_engine import AutomationAuditEngine
        
        # Get data
        enrichment = DataEnrichmentEngine()
        company_data = enrichment.enrich_company("https://www.shopify.com")
        
        audit = AutomationAuditEngine()
        audit_report = audit.generate_audit("https://www.shopify.com")
        
        # Generate script
        generator = IntelligentScriptGenerator()
        script = generator.generate_detailed_script(
            company_data,
            audit_report,
            prospect_name="Sarah",
            target_duration=240
        )
        
        print(f"✅ Script generation works! {script.word_count} words")
        print(f"   Duration: {script.total_duration_seconds}s")
        
        # Show first 100 chars of script
        full_script = script.get_full_script()
        print(f"   Preview: {full_script[:100]}...")
        
        return True
    except Exception as e:
        print(f"❌ Script generation failed: {e}")
        return False

def test_video_generation():
    """Test video generation with D-ID - might fail if no credits"""
    print("\n[TEST 5] Video Generation (D-ID)")
    print("-" * 40)
    
    try:
        from core_test import generate_video_did
        
        # Short test script
        test_script = "Hi Sarah, I analyzed Shopify and found three ways to save 100k per year."
        
        result = generate_video_did(test_script)
        
        if result and result.get('success'):
            print(f"✅ Video generation works! URL: {result.get('video_url')}")
            return True
        else:
            print(f"❌ Video generation failed - likely no credits")
            return False
            
    except Exception as e:
        print(f"❌ Video generation error: {e}")
        return False

def test_heygen():
    """Test HeyGen as backup"""
    print("\n[TEST 6] Video Generation (HeyGen)")
    print("-" * 40)
    
    try:
        import requests
        import time
        
        api_key = os.environ.get('HEYGEN_API_KEY')
        if not api_key:
            print("❌ No HeyGen API key")
            return False
        
        # Test with HeyGen
        url = "https://api.heygen.com/v2/video/generate"
        
        headers = {
            "X-Api-Key": api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "video_inputs": [{
                "character": {
                    "type": "avatar",
                    "avatar_id": os.environ.get('HEYGEN_AVATAR_ID'),
                    "avatar_style": "normal"
                },
                "voice": {
                    "type": "text",
                    "input_text": "Testing HeyGen API",
                    "voice_id": "en-US-1"
                }
            }],
            "dimension": {"width": 1280, "height": 720}
        }
        
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code in [200, 201]:
            print(f"✅ HeyGen API responded! Checking status...")
            data = response.json()
            
            # Check video status
            video_id = data.get('data', {}).get('video_id')
            if video_id:
                # Poll for status
                status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
                time.sleep(5)
                
                status_response = requests.get(status_url, headers={"X-Api-Key": api_key})
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"   Status: {status_data.get('data', {}).get('status', 'unknown')}")
                    return True
        else:
            print(f"❌ HeyGen failed: {response.status_code}")
            print(f"   Error: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ HeyGen error: {e}")
        return False

def main():
    print("=" * 60)
    print("VIDEOREACH AI - FULL PIPELINE TEST")
    print("=" * 60)
    print("Testing what actually works with current API keys...")
    
    results = {
        "research": test_research(),
        "enrichment": test_enrichment(),
        "audit": test_audit(),
        "script": test_script_generation(),
        "video_did": test_video_generation(),
        "video_heygen": test_heygen()
    }
    
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    
    working = []
    broken = []
    
    for component, status in results.items():
        if status:
            working.append(component)
            print(f"✅ {component}: WORKING")
        else:
            broken.append(component)
            print(f"❌ {component}: NOT WORKING")
    
    print(f"\nWorking: {len(working)}/{len(results)}")
    
    if len(working) >= 4:
        print("\n🎉 Core pipeline is functional!")
        print("You can generate scripts from real website data.")
        print("Just need video API credits to complete the pipeline.")
    else:
        print("\n⚠️ Pipeline needs fixes")

if __name__ == "__main__":
    main()