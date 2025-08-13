"""
Simple test for faceless video generation - no unicode issues
"""

import os
import sys
import asyncio
from pathlib import Path

# Create necessary directories
Path("videos").mkdir(exist_ok=True)
Path("temp").mkdir(exist_ok=True)

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

from faceless_video_generator import FacelessVideoGenerator, DataVisualizationGenerator

def test_data_viz():
    """Test data visualization generation"""
    print("\n=== Testing Data Visualization ===")
    
    viz = DataVisualizationGenerator()
    
    # Test revenue loss chart
    try:
        chart_path = viz.create_lost_revenue_chart(
            monthly_loss=15000,
            company_name="Test Company"
        )
        print(f"SUCCESS: Revenue loss chart created: {chart_path}")
        if os.path.exists(chart_path):
            size = os.path.getsize(chart_path) / 1024
            print(f"  File size: {size:.2f} KB")
    except Exception as e:
        print(f"ERROR: Failed to create revenue chart: {e}")
        return False
    
    # Test ROI calculator
    try:
        roi_path = viz.create_roi_calculator(
            investment=500,
            return_monthly=15000,
            company_name="Test Company"
        )
        print(f"SUCCESS: ROI calculator created: {roi_path}")
        if os.path.exists(roi_path):
            size = os.path.getsize(roi_path) / 1024
            print(f"  File size: {size:.2f} KB")
    except Exception as e:
        print(f"ERROR: Failed to create ROI chart: {e}")
        return False
    
    return True

async def test_faceless_video():
    """Test faceless video generation without web scraping"""
    print("\n=== Testing Faceless Video Generation ===")
    
    # Test data
    company_data = {
        'company': "Test HVAC Company",
        'website': 'https://example.com',
        'industry': 'HVAC',
        'pain_points': ['no online booking', 'manual scheduling', 'phone-only support'],
        'monthly_loss': 12000,
        'solution_cost': 497,
        'competitor': 'Modern HVAC Solutions',
        'calendar_link': 'calendly.com/demo'
    }
    
    print(f"Company: {company_data['company']}")
    print(f"Industry: {company_data['industry']}")
    print(f"Pain points: {', '.join(company_data['pain_points'])}")
    
    # Initialize generator
    generator = FacelessVideoGenerator()
    
    # Generate script sections
    print("\nGenerating script sections...")
    scripts = generator.generate_script_sections(company_data)
    
    for section, text in scripts.items():
        print(f"\n[{section}]")
        print(f"  {text[:80]}..." if len(text) > 80 else f"  {text}")
    
    # Try to generate video (will use fallback TTS if no ElevenLabs key)
    print("\nAttempting to generate video...")
    try:
        video_path = await generator.generate_faceless_video(
            company_data=company_data,
            output_path=f"videos/test_faceless_simple.mp4"
        )
        
        if video_path and os.path.exists(video_path):
            file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
            print(f"SUCCESS: Video generated: {video_path}")
            print(f"  File size: {file_size:.2f} MB")
            return True
        else:
            print("ERROR: Video file not created")
            return False
            
    except Exception as e:
        print(f"ERROR: Failed to generate video: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests"""
    print("=" * 60)
    print("FACELESS VIDEO GENERATION - SIMPLE TEST")
    print("=" * 60)
    
    # Test 1: Data Visualization
    viz_result = test_data_viz()
    
    # Test 2: Video Generation
    video_result = await test_faceless_video()
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Data Visualization: {'PASSED' if viz_result else 'FAILED'}")
    print(f"Video Generation: {'PASSED' if video_result else 'FAILED'}")
    
    if viz_result and video_result:
        print("\nAll tests passed! Faceless video system is working.")
    else:
        print("\nSome tests failed. Check errors above.")

if __name__ == "__main__":
    # Check dependencies first
    print("Checking critical dependencies...\n")
    
    # Check Python packages
    required_packages = ['matplotlib', 'PIL', 'playwright', 'elevenlabs']
    for package in required_packages:
        try:
            __import__(package)
            print(f"[OK] {package} installed")
        except ImportError:
            print(f"[ERROR] {package} not installed")
    
    # Check FFmpeg
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("[OK] FFmpeg installed")
        else:
            print("[ERROR] FFmpeg not working")
    except FileNotFoundError:
        print("[ERROR] FFmpeg not found in PATH")
    
    print("\nStarting tests...\n")
    asyncio.run(main())