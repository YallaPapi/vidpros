"""
Fixed Faceless Video Generator with Proper Async Handling
"""

import os
import json
import time
import asyncio
import tempfile
import subprocess
from typing import Dict, List, Optional, Tuple
from pathlib import Path

# Fix matplotlib backend for threading issues
import matplotlib
matplotlib.use('Agg')

import requests
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImprovedVoiceGenerator:
    """Fixed voice generator with proper async handling"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('ELEVENLABS_API_KEY')
    
    async def generate_voiceover(self, text: str) -> str:
        """Generate voiceover with fallback options"""
        
        # Try ElevenLabs first
        if self.api_key:
            try:
                return await self._elevenlabs_tts(text)
            except Exception as e:
                logger.error(f"ElevenLabs failed: {e}")
        
        # Fallback to edge-tts
        try:
            return await self._edge_tts(text)
        except Exception as e:
            logger.error(f"Edge-TTS failed: {e}")
        
        # Last resort - pyttsx3
        return self._pyttsx3_tts(text)
    
    async def _elevenlabs_tts(self, text: str) -> str:
        """Use ElevenLabs API"""
        import aiohttp
        
        url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        data = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    output_path = tempfile.mktemp(suffix='.mp3')
                    audio_content = await response.read()
                    with open(output_path, 'wb') as f:
                        f.write(audio_content)
                    logger.info(f"ElevenLabs voiceover generated: {output_path}")
                    return output_path
                else:
                    raise Exception(f"ElevenLabs API error: {response.status}")
    
    async def _edge_tts(self, text: str) -> str:
        """Use edge-tts for natural voice"""
        import edge_tts
        
        output_path = tempfile.mktemp(suffix='.mp3')
        voice = "en-US-AriaNeural"
        
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
        
        logger.info(f"Edge-TTS voiceover generated: {output_path}")
        return output_path
    
    def _pyttsx3_tts(self, text: str) -> str:
        """Fallback to pyttsx3"""
        import pyttsx3
        
        engine = pyttsx3.init()
        output_path = tempfile.mktemp(suffix='.mp3')
        engine.save_to_file(text, output_path)
        engine.runAndWait()
        
        logger.info(f"Pyttsx3 voiceover generated: {output_path}")
        return output_path


class ImprovedScriptGenerator:
    """Generate compelling scripts with real data"""
    
    def generate_script(self, company_data: Dict) -> str:
        """Create personalized, compelling script"""
        
        company = company_data.get('company', 'your company')
        industry = company_data.get('industry', 'business')
        pain_points = company_data.get('pain_points', ['manual processes'])
        monthly_loss = company_data.get('monthly_loss', 10000)
        
        # Industry-specific metrics
        industry_metrics = {
            "HVAC": {
                "avg_ticket": 385,
                "missed_calls_per_day": 12,
                "conversion_rate": 0.35
            },
            "Plumbing": {
                "avg_ticket": 425,
                "missed_calls_per_day": 15,
                "conversion_rate": 0.40
            }
        }
        
        metrics = industry_metrics.get(industry, industry_metrics["HVAC"])
        
        # Calculate real impact
        annual_loss = monthly_loss * 12
        missed_revenue = metrics['missed_calls_per_day'] * metrics['avg_ticket'] * 22
        
        # Build compelling script
        script = f"""
        I was just on {company}'s website and noticed you're probably losing about 
        ${monthly_loss:,.0f} every month. 
        
        Look, you're {pain_points[0] if pain_points else 'missing opportunities'}. 
        That's {metrics['missed_calls_per_day']} potential customers every day who 
        can't book with you after hours.
        
        I helped another {industry} company automate this last month. 
        They went from missing half their calls to capturing every single lead, 
        even at 2AM on Sunday.
        
        For {company}, we could have online booking live in 48 hours. 
        No complex setup, just a simple system that captures those 
        ${missed_revenue:,.0f} in monthly revenue you're currently missing.
        
        I've got 15 minutes tomorrow to show you exactly how this works. 
        No pitch, just a quick demo. Click below if you want to stop 
        leaving money on the table.
        """
        
        # Clean up whitespace
        script = ' '.join(script.split())
        
        return script


class SimpleVideoAssembler:
    """Assemble video from images and audio"""
    
    @staticmethod
    def create_video(images: List[str], audio_path: str, output_path: str) -> bool:
        """Create video using FFmpeg"""
        
        try:
            # Create concat file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for i, image_path in enumerate(images):
                    duration = 5.0  # 5 seconds per image
                    f.write(f"file '{os.path.abspath(image_path)}'\n")
                    f.write(f"duration {duration}\n")
                # Add last image
                if images:
                    f.write(f"file '{os.path.abspath(images[-1])}'\n")
                concat_file = f.name
            
            # FFmpeg command
            cmd = [
                'ffmpeg',
                '-f', 'concat',
                '-safe', '0',
                '-i', concat_file,
                '-i', audio_path,
                '-c:v', 'libx264',
                '-c:a', 'aac',
                '-pix_fmt', 'yuv420p',
                '-shortest',
                '-y',
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            os.unlink(concat_file)
            
            if result.returncode == 0:
                logger.info(f"Video created: {output_path}")
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Video assembly error: {e}")
            return False


class SimpleFacelessVideoGenerator:
    """Main generator with fixed async handling"""
    
    def __init__(self):
        self.voice_gen = ImprovedVoiceGenerator()
        self.script_gen = ImprovedScriptGenerator()
        self.video_assembler = SimpleVideoAssembler()
    
    async def generate_video(self, company_data: Dict) -> str:
        """Generate complete faceless video"""
        
        logger.info(f"Generating video for {company_data.get('company')}")
        
        # 1. Generate script
        script = self.script_gen.generate_script(company_data)
        logger.info(f"Script generated: {len(script)} characters")
        
        # 2. Generate voiceover
        audio_path = await self.voice_gen.generate_voiceover(script)
        logger.info(f"Voiceover generated: {audio_path}")
        
        # 3. Create simple visuals
        images = self._create_simple_visuals(company_data)
        logger.info(f"Created {len(images)} visual frames")
        
        # 4. Assemble video
        output_path = f"video_{company_data.get('company', 'output').replace(' ', '_')}_{int(time.time())}.mp4"
        success = self.video_assembler.create_video(images, audio_path, output_path)
        
        if success:
            logger.info(f"Video completed: {output_path}")
            return output_path
        else:
            logger.error("Video assembly failed")
            return None
    
    def _create_simple_visuals(self, company_data: Dict) -> List[str]:
        """Create simple visual frames"""
        
        images = []
        
        # Frame 1: Problem statement
        img1 = self._create_text_frame(
            f"{company_data.get('company', 'Your Company')}",
            f"Losing ${company_data.get('monthly_loss', 10000):,.0f}/month",
            "red"
        )
        images.append(img1)
        
        # Frame 2: Solution
        img2 = self._create_text_frame(
            "Simple Solution",
            "Online booking in 48 hours",
            "green"
        )
        images.append(img2)
        
        # Frame 3: CTA
        img3 = self._create_text_frame(
            "Book a Demo",
            "15 minutes to see it working",
            "blue"
        )
        images.append(img3)
        
        return images
    
    def _create_text_frame(self, title: str, subtitle: str, color: str) -> str:
        """Create a simple text frame"""
        
        img = Image.new('RGB', (1920, 1080), color='white')
        draw = ImageDraw.Draw(img)
        
        # Try to use a better font
        try:
            title_font = ImageFont.truetype("arial.ttf", 80)
            subtitle_font = ImageFont.truetype("arial.ttf", 60)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
        
        # Draw text
        draw.text((960, 400), title, fill=color, font=title_font, anchor="mm")
        draw.text((960, 600), subtitle, fill="black", font=subtitle_font, anchor="mm")
        
        # Save
        output_path = tempfile.mktemp(suffix='.png')
        img.save(output_path)
        
        return output_path


# Test function
async def test_fixed_generator():
    """Test the fixed generator"""
    
    company_data = {
        "company": "Bob's HVAC Services",
        "website": "https://example.com",
        "industry": "HVAC",
        "pain_points": ["no online booking", "manual scheduling"],
        "monthly_loss": 15000
    }
    
    generator = SimpleFacelessVideoGenerator()
    video_path = await generator.generate_video(company_data)
    
    if video_path:
        print(f"SUCCESS: Video generated at {video_path}")
        file_size = os.path.getsize(video_path) / 1024 / 1024
        print(f"File size: {file_size:.2f} MB")
    else:
        print("FAILED: Could not generate video")


if __name__ == "__main__":
    asyncio.run(test_fixed_generator())