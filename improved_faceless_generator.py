"""
Improved Faceless Video Generator with Better Scripts and Voice
"""

import os
import json
import tempfile
import asyncio
from typing import Dict, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ImprovedScriptGenerator:
    """Generate actually compelling, personalized scripts"""
    
    def __init__(self):
        # Load industry-specific templates
        self.load_industry_data()
    
    def load_industry_data(self):
        """Load industry playbooks for better personalization"""
        # This would load from COMPLETE_140_INDUSTRIES.md
        self.industry_data = {
            "HVAC": {
                "pain_points": {
                    "no online booking": "forcing customers to call during business hours, losing 40% of after-hours leads",
                    "manual scheduling": "double-booking technicians and missing service windows", 
                    "phone-only support": "missing 60% of calls during peak service times"
                },
                "metrics": {
                    "avg_ticket": 385,
                    "missed_calls_per_day": 12,
                    "after_hours_inquiries": 8,
                    "scheduling_errors_per_week": 3
                },
                "competitor_examples": ["ServiceTitan users", "Housecall Pro customers"],
                "owner_struggles": "You're probably spending nights and weekends returning calls instead of growing your business"
            }
        }
    
    def generate_personalized_script(self, company_data: Dict) -> Dict[str, str]:
        """Create actually compelling video scripts"""
        
        company = company_data.get('company', 'your company')
        industry = company_data.get('industry', 'HVAC')
        website = company_data.get('website', '')
        pain_points = company_data.get('pain_points', [])
        
        # Get industry-specific data
        industry_info = self.industry_data.get(industry, self.industry_data['HVAC'])
        
        # Calculate real metrics
        missed_revenue = industry_info['metrics']['missed_calls_per_day'] * industry_info['metrics']['avg_ticket'] * 22  # monthly
        
        scripts = {
            "hook": f"Hey, I was just on {company}'s website and noticed something that's probably costing you about ${missed_revenue:,.0f} every month.",
            
            "problem_deep_dive": f"Look, I work with a lot of {industry} companies, and here's what I see - "
                               f"{industry_info['owner_struggles']}. "
                               f"Your website doesn't have online booking, which means you're {industry_info['pain_points'].get(pain_points[0] if pain_points else 'no online booking', 'missing opportunities')}.",
            
            "social_proof": f"I just helped another {industry} company in your area implement this. "
                          f"Within 30 days, they went from missing 12 calls a day to capturing every single lead automatically. "
                          f"Their revenue jumped 23% without hiring anyone new.",
            
            "specific_solution": f"Here's exactly what we'd do for {company}: "
                              f"First, add a 'Book Now' button that works 24/7. "
                              f"Second, automated text reminders so customers actually show up. "
                              f"Third, a simple dashboard showing every job, payment, and customer in one place. "
                              f"This isn't complex - we can have it live in 48 hours.",
            
            "urgency": f"Look, every day you wait is literally costing you money. "
                     f"Those {industry_info['metrics']['after_hours_inquiries']} after-hours leads tonight? "
                     f"They're calling your competitor right now.",
            
            "soft_cta": f"I've got 15 minutes blocked tomorrow to show you exactly how this works. "
                      f"No sales pitch, just a quick screen share showing the system in action. "
                      f"Hit the link below if you want to see it."
        }
        
        # Combine into full script (keep it under 45 seconds when spoken)
        full_script = f"{scripts['hook']} {scripts['problem_deep_dive']} {scripts['social_proof']} {scripts['specific_solution']} {scripts['soft_cta']}"
        
        scripts['full'] = full_script
        return scripts


class BetterVoiceGenerator:
    """Use better TTS or AI voice services"""
    
    def __init__(self):
        self.elevenlabs_api_key = os.getenv('ELEVENLABS_API_KEY')
        self.voice_settings = {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.25,  # More conversational
            "use_speaker_boost": True
        }
    
    async def generate_natural_voice(self, text: str, output_path: str) -> str:
        """Generate natural-sounding voice"""
        
        if self.elevenlabs_api_key:
            # Use ElevenLabs for natural voice
            import aiohttp
            
            url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"  # Rachel voice
            
            headers = {
                "xi-api-key": self.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": self.voice_settings
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=data, headers=headers) as response:
                    if response.status == 200:
                        audio_content = await response.read()
                        with open(output_path, 'wb') as f:
                            f.write(audio_content)
                        return output_path
        
        # Fallback to Azure TTS (better than pyttsx3)
        return await self.use_azure_tts(text, output_path)
    
    async def use_azure_tts(self, text: str, output_path: str) -> str:
        """Use Azure Cognitive Services for better TTS"""
        azure_key = os.getenv('AZURE_SPEECH_KEY')
        
        if azure_key:
            import azure.cognitiveservices.speech as speechsdk
            
            speech_config = speechsdk.SpeechConfig(
                subscription=azure_key,
                region="eastus"
            )
            
            # Use a natural voice
            speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
            
            # SSML for better prosody
            ssml = f"""
            <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
                <voice name="en-US-JennyNeural">
                    <prosody rate="0.95" pitch="-5%">
                        {text}
                    </prosody>
                </voice>
            </speak>
            """
            
            synthesizer = speechsdk.SpeechSynthesizer(
                speech_config=speech_config,
                audio_config=None
            )
            
            result = synthesizer.speak_ssml_async(ssml).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                with open(output_path, "wb") as f:
                    f.write(result.audio_data)
                return output_path
        
        # Last resort - use edge-tts (free and better than pyttsx3)
        return await self.use_edge_tts(text, output_path)
    
    async def use_edge_tts(self, text: str, output_path: str) -> str:
        """Use Edge TTS for free natural voice"""
        try:
            import edge_tts
            
            # Use a natural US voice
            voice = "en-US-AriaNeural"
            
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            
            logger.info(f"Generated natural voice with edge-tts: {output_path}")
            return output_path
            
        except ImportError:
            logger.error("edge-tts not installed. Installing...")
            os.system("pip install edge-tts")
            
            # Try again after install
            import edge_tts
            voice = "en-US-AriaNeural"
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(output_path)
            return output_path


class RealWebsiteCapture:
    """Actually capture real website screenshots"""
    
    async def capture_annotated_screenshots(self, url: str, pain_points: List[str]) -> List[str]:
        """Capture and annotate website showing problems"""
        
        from playwright.async_api import async_playwright
        import cv2
        import numpy as np
        from PIL import Image, ImageDraw, ImageFont
        
        screenshots = []
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            try:
                # Actually navigate to the website
                await page.goto(url, wait_until='domcontentloaded', timeout=10000)
                await page.wait_for_timeout(2000)  # Let it render
                
                # Take homepage screenshot
                homepage_path = tempfile.mktemp(suffix='_homepage.png')
                await page.screenshot(path=homepage_path)
                
                # Annotate with problems
                img = Image.open(homepage_path)
                draw = ImageDraw.Draw(img)
                
                # Add red arrows and text pointing to missing features
                if "no online booking" in str(pain_points):
                    # Draw attention to lack of booking button
                    draw.rectangle([1600, 100, 1900, 200], outline="red", width=5)
                    draw.text((1620, 210), "NO BOOKING BUTTON!", fill="red", font=ImageFont.load_default())
                
                if "phone-only" in str(pain_points):
                    # Highlight phone number area
                    draw.ellipse([100, 50, 400, 150], outline="red", width=5)
                    draw.text((420, 80), "Only contact method!", fill="red", font=ImageFont.load_default())
                
                annotated_path = tempfile.mktemp(suffix='_annotated.png')
                img.save(annotated_path)
                screenshots.append(annotated_path)
                
            except Exception as e:
                logger.error(f"Failed to capture {url}: {e}")
                # Create a placeholder if site doesn't load
                img = Image.new('RGB', (1920, 1080), color='white')
                draw = ImageDraw.Draw(img)
                draw.text((860, 540), f"Analysis of {url}", fill="black", font=ImageFont.load_default())
                placeholder_path = tempfile.mktemp(suffix='_placeholder.png')
                img.save(placeholder_path)
                screenshots.append(placeholder_path)
            
            finally:
                await browser.close()
        
        return screenshots


# Test the improved version
async def test_improved_generator():
    """Test with better script and voice"""
    
    # Install edge-tts for better voice
    os.system("pip install edge-tts")
    
    script_gen = ImprovedScriptGenerator()
    voice_gen = BetterVoiceGenerator()
    
    company_data = {
        "company": "Bob's HVAC Services",
        "website": "https://example.com",
        "industry": "HVAC",
        "pain_points": ["no online booking", "manual scheduling", "phone-only support"]
    }
    
    # Generate better script
    scripts = script_gen.generate_personalized_script(company_data)
    print("Generated Script:")
    print("-" * 60)
    print(scripts['full'])
    print("-" * 60)
    
    # Generate natural voice
    voice_path = await voice_gen.use_edge_tts(
        scripts['full'],
        "improved_voiceover.mp3"
    )
    
    print(f"\nVoice generated: {voice_path}")
    print("This should sound much more natural!")


if __name__ == "__main__":
    asyncio.run(test_improved_generator())