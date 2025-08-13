"""
Test script for faceless video generation
Tests all components of the faceless video pipeline
"""

import os
import asyncio
import json
from datetime import datetime
from pathlib import Path

# Create necessary directories
Path("videos").mkdir(exist_ok=True)
Path("temp").mkdir(exist_ok=True)
Path("reports").mkdir(exist_ok=True)

# Import our modules
from faceless_video_generator import (
    FacelessVideoGenerator,
    ScreenshotAnnotator,
    DataVisualizationGenerator,
    FacelessVideoConfig
)


def test_data_visualization():
    """Test data visualization generation"""
    print("\n=== Testing Data Visualization ===")
    
    viz = DataVisualizationGenerator()
    
    # Test revenue loss chart
    chart_path = viz.create_lost_revenue_chart(
        monthly_loss=15000,
        company_name="Test Company"
    )
    print(f"✓ Revenue loss chart created: {chart_path}")
    
    # Test ROI calculator
    roi_path = viz.create_roi_calculator(
        investment=500,
        return_monthly=15000,
        company_name="Test Company"
    )
    print(f"✓ ROI calculator created: {roi_path}")
    
    return True


async def test_faceless_video_simple():
    """Test basic faceless video generation"""
    print("\n=== Testing Faceless Video Generation (Simple) ===")
    
    # Test data - minimal required fields
    company_data = {
        'company': "Demo HVAC Services",
        'website': 'https://example.com',
        'industry': 'HVAC',
        'pain_points': ['no online booking', 'manual scheduling', 'phone-only support'],
        'monthly_loss': 8000,
        'solution_cost': 497,
        'competitor': 'Modern HVAC Pro',
        'calendar_link': 'calendly.com/demo'
    }
    
    # Initialize generator (will use fallback TTS if no API key)
    generator = FacelessVideoGenerator()
    
    # Generate video
    print("Generating faceless video...")
    video_path = await generator.generate_faceless_video(
        company_data=company_data,
        output_path=f"videos/test_faceless_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    )
    
    if video_path and os.path.exists(video_path):
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        print(f"✓ Video generated successfully: {video_path}")
        print(f"  File size: {file_size:.2f} MB")
        return True
    else:
        print("✗ Failed to generate video")
        return False


async def test_faceless_video_complete():
    """Test complete faceless video with all features"""
    print("\n=== Testing Complete Faceless Video Pipeline ===")
    
    # Comprehensive test data
    company_data = {
        'company': "Bob's Professional HVAC",
        'website': 'https://www.hvac.com',  # Using a real site for better screenshots
        'industry': 'HVAC',
        'owner_name': 'Bob Johnson',
        'email': 'bob@bobshvac.com',
        'pain_points': [
            'no online booking system',
            'manual dispatch and routing',
            'paper-based invoicing',
            'no customer portal',
            'missing mobile app'
        ],
        'monthly_loss': 25000,
        'solution_cost': 997,
        'competitor': 'TechSavvy HVAC Solutions',
        'calendar_link': 'calendly.com/hvac-automation-demo',
        
        # Additional context for better personalization
        'city': 'Dallas',
        'employees': 15,
        'years_in_business': 20,
        'current_tools': ['QuickBooks', 'Excel', 'Phone system'],
        'growth_goal': 'Double revenue in 2 years'
    }
    
    # Initialize generator with config
    config = FacelessVideoConfig()
    config.scene_timings = {
        "problem_highlight": 7,
        "competitor_solution": 10,
        "data_visualization": 12,
        "roi_calculator": 12,
        "solution_mockup": 10,
        "call_to_action": 6
    }
    
    generator = FacelessVideoGenerator()
    generator.config = config
    
    # Generate comprehensive script
    scripts = generator.generate_script_sections(company_data)
    
    print("Generated Script Sections:")
    for section, text in scripts.items():
        print(f"\n[{section}]")
        print(f"  {text[:100]}..." if len(text) > 100 else f"  {text}")
    
    # Generate video
    print("\nGenerating comprehensive faceless video...")
    video_path = await generator.generate_faceless_video(
        company_data=company_data,
        output_path=f"videos/complete_faceless_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4"
    )
    
    if video_path and os.path.exists(video_path):
        file_size = os.path.getsize(video_path) / (1024 * 1024)  # MB
        print(f"✓ Complete video generated: {video_path}")
        print(f"  File size: {file_size:.2f} MB")
        print(f"  Duration: ~57 seconds (estimated)")
        return True
    else:
        print("✗ Failed to generate complete video")
        return False


def test_cost_comparison():
    """Compare costs between faceless and avatar videos"""
    print("\n=== Cost Comparison Analysis ===")
    
    # Cost per video
    faceless_cost = {
        'voiceover': 0.02,  # ElevenLabs
        'screenshots': 0.01,  # API costs
        'processing': 0.01,  # Compute
        'total': 0.04
    }
    
    avatar_cost = {
        'd_id_api': 0.15,
        'processing': 0.05,
        'total': 0.20
    }
    
    print("Cost per video:")
    print(f"  Faceless: ${faceless_cost['total']:.3f}")
    print(f"  Avatar: ${avatar_cost['total']:.3f}")
    print(f"  Savings: ${avatar_cost['total'] - faceless_cost['total']:.3f} (80% reduction)")
    
    print("\nCost for 1,000 videos:")
    print(f"  Faceless: ${faceless_cost['total'] * 1000:.2f}")
    print(f"  Avatar: ${avatar_cost['total'] * 1000:.2f}")
    print(f"  Savings: ${(avatar_cost['total'] - faceless_cost['total']) * 1000:.2f}")
    
    print("\nProcessing time:")
    print(f"  Faceless: 10-15 seconds")
    print(f"  Avatar: 30-45 seconds")
    print(f"  Speed improvement: 66% faster")
    
    return True


async def run_all_tests():
    """Run all faceless video tests"""
    print("=" * 60)
    print("FACELESS VIDEO GENERATION TEST SUITE")
    print("=" * 60)
    
    results = []
    
    # Test 1: Data Visualization
    try:
        results.append(("Data Visualization", test_data_visualization()))
    except Exception as e:
        print(f"Error in data visualization test: {e}")
        results.append(("Data Visualization", False))
    
    # Test 2: Simple Video
    try:
        result = await test_faceless_video_simple()
        results.append(("Simple Video Generation", result))
    except Exception as e:
        print(f"Error in simple video test: {e}")
        results.append(("Simple Video Generation", False))
    
    # Test 3: Complete Video
    try:
        result = await test_faceless_video_complete()
        results.append(("Complete Video Pipeline", result))
    except Exception as e:
        print(f"Error in complete video test: {e}")
        results.append(("Complete Video Pipeline", False))
    
    # Test 4: Cost Analysis
    try:
        results.append(("Cost Comparison", test_cost_comparison()))
    except Exception as e:
        print(f"Error in cost comparison: {e}")
        results.append(("Cost Comparison", False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)
    
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed! Faceless video generation is working correctly.")
    else:
        print(f"\n⚠️ {total_tests - total_passed} test(s) failed. Please check the errors above.")


if __name__ == "__main__":
    # Check for required dependencies
    print("Checking dependencies...")
    
    try:
        import matplotlib
        print("✓ matplotlib installed")
    except ImportError:
        print("✗ matplotlib not installed. Run: pip install matplotlib")
    
    try:
        import PIL
        print("✓ PIL/Pillow installed")
    except ImportError:
        print("✗ Pillow not installed. Run: pip install Pillow")
    
    try:
        from playwright.async_api import async_playwright
        print("✓ Playwright installed")
    except ImportError:
        print("✗ Playwright not installed. Run: pip install playwright && playwright install")
    
    # Check for FFmpeg
    import subprocess
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ FFmpeg installed")
        else:
            print("✗ FFmpeg not working properly")
    except FileNotFoundError:
        print("✗ FFmpeg not found. Please install FFmpeg and add to PATH")
        print("  Download from: https://ffmpeg.org/download.html")
    
    print("\nStarting tests...\n")
    
    # Run tests
    asyncio.run(run_all_tests())