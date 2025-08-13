"""
Faceless Video Generator
Creates data-driven videos using screenshots, statistics, and AI voiceover
No avatar needed - focuses on showing actual problems and data
"""

import os
import json
import time
import asyncio
import tempfile
import subprocess
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path

# Fix matplotlib backend for threading issues
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend

import requests
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class FacelessVideoConfig:
    """Configuration for faceless video generation"""
    voice_id: str = "EXAVITQu4vr4xnSDxMaL"  # Professional male voice
    voice_model: str = "eleven_monolingual_v1"
    voice_stability: float = 0.5
    voice_similarity: float = 0.75
    voice_speed: float = 1.1  # Slightly faster for engagement
    
    video_width: int = 1920
    video_height: int = 1080
    video_fps: int = 30
    
    # Timing for each scene (in seconds)
    scene_timings: Dict[str, float] = None
    
    def __post_init__(self):
        if self.scene_timings is None:
            self.scene_timings = {
                "problem_highlight": 5,
                "competitor_solution": 10,
                "data_visualization": 10,
                "roi_calculator": 10,
                "solution_mockup": 10,
                "call_to_action": 5
            }


class ScreenshotAnnotator:
    """Adds annotations and highlights to screenshots"""
    
    @staticmethod
    def add_problem_highlight(image_path: str, problems: List[Dict]) -> str:
        """Add red boxes and arrows highlighting problems"""
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # Try to load a font, fallback to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", 36)
            small_font = ImageFont.truetype("arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        for problem in problems:
            x, y, w, h = problem.get('bbox', [100, 100, 400, 100])
            
            # Draw red box around problem area
            draw.rectangle([x, y, x+w, y+h], outline="red", width=4)
            
            # Add annotation text
            text = problem.get('text', '❌ Missing Feature')
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            
            # Position text box
            text_x = x + w + 20
            text_y = y
            
            # Draw text background
            padding = 10
            draw.rectangle([
                text_x - padding, 
                text_y - padding,
                text_x + text_width + padding,
                text_y + text_height + padding
            ], fill="red")
            
            # Draw text
            draw.text((text_x, text_y), text, fill="white", font=font)
            
            # Draw arrow from box to problem
            arrow_start = (text_x - 20, text_y + text_height // 2)
            arrow_end = (x + w, y + h // 2)
            draw.line([arrow_start, arrow_end], fill="red", width=3)
        
        output_path = image_path.replace('.png', '_annotated.png')
        img.save(output_path)
        return output_path
    
    @staticmethod
    def add_competitor_success(image_path: str, features: List[Dict]) -> str:
        """Add green checkmarks and highlights for competitor features"""
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        for feature in features:
            x, y, w, h = feature.get('bbox', [100, 100, 400, 100])
            
            # Draw green box around feature
            draw.rectangle([x, y, x+w, y+h], outline="green", width=4)
            
            # Add checkmark and text
            text = "✓ " + feature.get('text', 'Has this feature')
            draw.text((x + w + 20, y), text, fill="green", font=font)
        
        output_path = image_path.replace('.png', '_success.png')
        img.save(output_path)
        return output_path


class DataVisualizationGenerator:
    """Creates data visualizations and charts"""
    
    @staticmethod
    def create_lost_revenue_chart(monthly_loss: float, company_name: str) -> str:
        """Create a bar chart showing lost revenue"""
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        fig, ax = plt.subplots(figsize=(16, 9))
        
        # Data
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        losses = [monthly_loss * 0.8, monthly_loss * 0.9, monthly_loss, 
                 monthly_loss * 1.1, monthly_loss * 1.2, monthly_loss * 1.3]
        cumulative = np.cumsum(losses)
        
        # Create bar chart
        bars = ax.bar(months, losses, color='red', alpha=0.7, label='Monthly Loss')
        ax.plot(months, cumulative, color='darkred', marker='o', linewidth=3, 
                markersize=10, label='Cumulative Loss')
        
        # Styling
        ax.set_title(f"{company_name} - Revenue Lost to Missing Automation", 
                    fontsize=28, fontweight='bold', pad=20)
        ax.set_ylabel('Lost Revenue ($)', fontsize=20)
        ax.set_xlabel('Month', fontsize=20)
        
        # Add value labels on bars
        for bar, loss in zip(bars, losses):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'${loss:,.0f}', ha='center', va='bottom', fontsize=16)
        
        # Add cumulative total
        total_loss = cumulative[-1]
        ax.text(0.7, 0.9, f'6-Month Loss: ${total_loss:,.0f}', 
               transform=ax.transAxes, fontsize=24, fontweight='bold',
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
        
        ax.legend(fontsize=16)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, max(cumulative) * 1.2)
        
        # Format y-axis as currency
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        plt.tight_layout()
        
        output_path = tempfile.mktemp(suffix='_revenue_loss.png')
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    @staticmethod
    def create_roi_calculator(investment: float, return_monthly: float, company_name: str) -> str:
        """Create ROI visualization"""
        import matplotlib.pyplot as plt
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 9))
        
        # ROI Metrics (left)
        roi_percentage = ((return_monthly - investment) / investment) * 100
        payback_months = investment / return_monthly if return_monthly > 0 else float('inf')
        
        # Pie chart showing investment vs return
        sizes = [investment, return_monthly - investment] if return_monthly > investment else [investment, 0]
        colors = ['red', 'green']
        labels = ['Investment', 'Profit']
        
        ax1.pie(sizes, labels=labels, colors=colors, autopct='%1.0f%%',
               startangle=90, textprops={'fontsize': 18})
        ax1.set_title(f'Monthly ROI: {roi_percentage:.0f}%', fontsize=24, fontweight='bold')
        
        # Timeline chart (right)
        months = list(range(1, 13))
        cumulative_return = [return_monthly * m for m in months]
        cumulative_investment = [investment] * 12  # One-time investment
        cumulative_profit = [r - investment for r in cumulative_return]
        
        ax2.plot(months, cumulative_profit, 'g-', linewidth=3, label='Cumulative Profit')
        ax2.axhline(y=0, color='black', linestyle='-', alpha=0.3)
        ax2.fill_between(months, 0, cumulative_profit, where=[p > 0 for p in cumulative_profit],
                        color='green', alpha=0.3, label='Profit Zone')
        ax2.fill_between(months, 0, cumulative_profit, where=[p <= 0 for p in cumulative_profit],
                        color='red', alpha=0.3, label='Investment Recovery')
        
        # Mark break-even point
        if payback_months < 12:
            ax2.plot(payback_months, 0, 'ro', markersize=15)
            ax2.annotate(f'Break-even: Month {payback_months:.1f}',
                        xy=(payback_months, 0), xytext=(payback_months, -investment/2),
                        arrowprops=dict(arrowstyle='->', color='red', lw=2),
                        fontsize=16, ha='center')
        
        ax2.set_title('12-Month Projection', fontsize=24, fontweight='bold')
        ax2.set_xlabel('Month', fontsize=18)
        ax2.set_ylabel('Cumulative Profit ($)', fontsize=18)
        ax2.legend(fontsize=14)
        ax2.grid(True, alpha=0.3)
        
        # Format y-axis as currency
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:,.0f}'))
        
        # Add summary box
        fig.text(0.5, 0.02, 
                f'{company_name} | Investment: ${investment:,.0f}/mo | Return: ${return_monthly:,.0f}/mo | ROI: {roi_percentage:.0f}%',
                ha='center', fontsize=20, bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        output_path = tempfile.mktemp(suffix='_roi_calculator.png')
        plt.savefig(output_path, dpi=100, bbox_inches='tight')
        plt.close()
        
        return output_path


class ElevenLabsVoiceGenerator:
    """Generate voiceover using ElevenLabs API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        
    def generate_voiceover(self, text: str, config: FacelessVideoConfig) -> str:
        """Generate voiceover audio from text"""
        url = f"{self.base_url}/text-to-speech/{config.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.api_key
        }
        
        data = {
            "text": text,
            "model_id": config.voice_model,
            "voice_settings": {
                "stability": config.voice_stability,
                "similarity_boost": config.voice_similarity,
                "speed": config.voice_speed
            }
        }
        
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            output_path = tempfile.mktemp(suffix='.mp3')
            with open(output_path, 'wb') as f:
                f.write(response.content)
            logger.info(f"Voiceover generated: {output_path}")
            return output_path
        else:
            logger.error(f"Failed to generate voiceover: {response.status_code} - {response.text}")
            # Fallback to system TTS
            return self._fallback_tts(text)
    
    def _fallback_tts(self, text: str) -> str:
        """Fallback to better TTS if ElevenLabs fails"""
        output_path = tempfile.mktemp(suffix='.mp3')
        
        # Try edge-tts first (much better quality)
        try:
            import edge_tts
            import asyncio
            
            async def generate_edge_tts():
                voice = "en-US-AriaNeural"  # Natural female voice
                communicate = edge_tts.Communicate(text, voice)
                await communicate.save(output_path)
            
            # Check if we're already in an event loop
            try:
                loop = asyncio.get_running_loop()
                # If we're in a loop, create new thread for sync operation
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(asyncio.run, generate_edge_tts())
                    future.result()
            except RuntimeError:
                # No loop running, we can use asyncio.run
                asyncio.run(generate_edge_tts())
            
            logger.info(f"Natural voice generated with edge-tts: {output_path}")
            return output_path
            
        except ImportError:
            # Fall back to pyttsx3 if edge-tts not available
            import pyttsx3
            
            engine = pyttsx3.init()
            engine.save_to_file(text, output_path)
            engine.runAndWait()
            
            logger.info(f"Fallback TTS generated: {output_path}")
            return output_path


class FFmpegVideoAssembler:
    """Assemble final video using FFmpeg"""
    
    @staticmethod
    def create_video(images: List[Tuple[str, float]], audio_path: str, output_path: str) -> bool:
        """
        Create video from images and audio
        images: List of (image_path, duration_seconds) tuples
        """
        try:
            # Create a temporary file listing all inputs
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                for image_path, duration in images:
                    f.write(f"file '{os.path.abspath(image_path)}'\n")
                    f.write(f"duration {duration}\n")
                # Add last image again for proper ending
                if images:
                    f.write(f"file '{os.path.abspath(images[-1][0])}'\n")
                concat_file = f.name
            
            # Build FFmpeg command
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
            
            # Execute FFmpeg
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            # Clean up temp file
            os.unlink(concat_file)
            
            if result.returncode == 0:
                logger.info(f"Video created successfully: {output_path}")
                return True
            else:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error creating video: {e}")
            return False


class FacelessVideoGenerator:
    """Main class for generating faceless videos"""
    
    def __init__(self, elevenlabs_api_key: str = None):
        self.config = FacelessVideoConfig()
        self.screenshot_annotator = ScreenshotAnnotator()
        self.data_viz = DataVisualizationGenerator()
        self.voice_generator = ElevenLabsVoiceGenerator(
            elevenlabs_api_key or os.getenv('ELEVENLABS_API_KEY')
        )
        self.video_assembler = FFmpegVideoAssembler()
        
    async def capture_website_screenshots(self, url: str) -> Dict[str, str]:
        """Capture screenshots of website with different states"""
        screenshots = {}
        
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page(viewport={'width': 1920, 'height': 1080})
            
            # Capture homepage
            await page.goto(url, wait_until='networkidle')
            homepage_path = tempfile.mktemp(suffix='_homepage.png')
            await page.screenshot(path=homepage_path, full_page=False)
            screenshots['homepage'] = homepage_path
            
            # Try to find and capture contact/booking page
            try:
                # Look for common booking/contact links
                for selector in ['a:has-text("Book")', 'a:has-text("Contact")', 
                               'a:has-text("Schedule")', 'a:has-text("Get Started")']:
                    try:
                        await page.click(selector, timeout=2000)
                        await page.wait_for_load_state('networkidle')
                        contact_path = tempfile.mktemp(suffix='_contact.png')
                        await page.screenshot(path=contact_path, full_page=False)
                        screenshots['contact'] = contact_path
                        break
                    except:
                        continue
            except:
                logger.info("Could not find contact/booking page")
            
            await browser.close()
        
        return screenshots
    
    def generate_script_sections(self, company_data: Dict) -> Dict[str, str]:
        """Generate script sections for each scene"""
        company = company_data.get('company', 'your company')
        industry = company_data.get('industry', 'business')
        pain_points = company_data.get('pain_points', ['manual processes'])
        monthly_loss = company_data.get('monthly_loss', 10000)
        solution_cost = company_data.get('solution_cost', 500)
        competitor = company_data.get('competitor', 'your competitors')
        
        scripts = {
            "problem_highlight": f"I noticed {company} is still handling {pain_points[0]} manually. "
                               f"This is costing you valuable time and money every single day.",
            
            "competitor_solution": f"Meanwhile, {competitor} is already using automation to handle this. "
                                 f"They're booking more {industry} jobs and spending less time on admin work.",
            
            "data_visualization": f"Let me show you the numbers. Based on industry data, "
                                f"you're losing approximately {monthly_loss} dollars every month "
                                f"from these inefficiencies.",
            
            "roi_calculator": f"Here's the ROI breakdown. For just {solution_cost} dollars per month, "
                            f"you could be capturing that lost revenue. "
                            f"That's a return of {int((monthly_loss/solution_cost)*100)} percent.",
            
            "solution_mockup": f"Your website could have online booking, automated scheduling, "
                             f"and customer self-service within 48 hours. "
                             f"No complex integration, just simple tools that work.",
            
            "call_to_action": f"Let's discuss your specific situation. "
                            f"Book a 15-minute call at the link below, "
                            f"and I'll show you exactly how this works for {industry} companies."
        }
        
        return scripts
    
    async def generate_faceless_video(
        self, 
        company_data: Dict,
        output_path: str = None
    ) -> str:
        """Generate complete faceless video"""
        
        logger.info(f"Generating faceless video for {company_data.get('company')}")
        
        # 1. Capture website screenshots
        url = company_data.get('website', 'https://example.com')
        screenshots = await self.capture_website_screenshots(url)
        
        # 2. Generate script sections
        scripts = self.generate_script_sections(company_data)
        
        # 3. Combine all script sections
        full_script = " ".join(scripts.values())
        
        # 4. Generate voiceover
        audio_path = self.voice_generator.generate_voiceover(full_script, self.config)
        
        # 5. Annotate screenshots and create visualizations
        scene_images = []
        
        # Scene 1: Problem highlight
        if 'homepage' in screenshots:
            annotated = self.screenshot_annotator.add_problem_highlight(
                screenshots['homepage'],
                [{'text': '❌ No Online Booking', 'bbox': [1500, 100, 300, 80]}]
            )
            scene_images.append((annotated, self.config.scene_timings['problem_highlight']))
        
        # Scene 2: Competitor solution (use same homepage with success markers)
        if 'homepage' in screenshots:
            success = self.screenshot_annotator.add_competitor_success(
                screenshots['homepage'],
                [{'text': 'Online Booking', 'bbox': [1500, 100, 300, 80]}]
            )
            scene_images.append((success, self.config.scene_timings['competitor_solution']))
        
        # Scene 3: Data visualization
        revenue_chart = self.data_viz.create_lost_revenue_chart(
            company_data.get('monthly_loss', 10000),
            company_data.get('company', 'Company')
        )
        scene_images.append((revenue_chart, self.config.scene_timings['data_visualization']))
        
        # Scene 4: ROI calculator
        roi_chart = self.data_viz.create_roi_calculator(
            company_data.get('solution_cost', 500),
            company_data.get('monthly_loss', 10000),
            company_data.get('company', 'Company')
        )
        scene_images.append((roi_chart, self.config.scene_timings['roi_calculator']))
        
        # Scene 5: Solution mockup (homepage again)
        if 'homepage' in screenshots:
            scene_images.append((screenshots['homepage'], self.config.scene_timings['solution_mockup']))
        
        # Scene 6: Call to action (create simple CTA image)
        cta_image = self._create_cta_image(company_data.get('calendar_link', 'calendly.com/demo'))
        scene_images.append((cta_image, self.config.scene_timings['call_to_action']))
        
        # 6. Assemble video
        if not output_path:
            output_path = f"faceless_video_{company_data.get('company', 'output')}_{int(time.time())}.mp4"
        
        success = self.video_assembler.create_video(scene_images, audio_path, output_path)
        
        if success:
            logger.info(f"Faceless video generated successfully: {output_path}")
            return output_path
        else:
            logger.error("Failed to generate video")
            return None
    
    def _create_cta_image(self, calendar_link: str) -> str:
        """Create a simple CTA image"""
        img = Image.new('RGB', (1920, 1080), color='white')
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("arial.ttf", 72)
            small_font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        # Main CTA text
        text = "Ready to Automate?"
        draw.text((960, 400), text, fill="black", font=font, anchor="mm")
        
        # Calendar link
        draw.text((960, 540), "Book Your Free Strategy Call", fill="blue", font=small_font, anchor="mm")
        draw.text((960, 620), calendar_link, fill="blue", font=small_font, anchor="mm")
        
        # Add urgency
        draw.text((960, 760), "⏰ Limited Slots Available This Week", fill="red", font=small_font, anchor="mm")
        
        output_path = tempfile.mktemp(suffix='_cta.png')
        img.save(output_path)
        return output_path


# Example usage
async def main():
    """Test the faceless video generator"""
    
    # Sample company data
    company_data = {
        'company': "Bob's HVAC",
        'website': 'https://example-hvac.com',
        'industry': 'HVAC',
        'pain_points': ['phone-only scheduling', 'no online booking', 'manual dispatching'],
        'monthly_loss': 12000,
        'solution_cost': 497,
        'competitor': 'TechHVAC Solutions',
        'calendar_link': 'calendly.com/automation-demo'
    }
    
    generator = FacelessVideoGenerator()
    video_path = await generator.generate_faceless_video(company_data)
    
    print(f"Video generated: {video_path}")


if __name__ == "__main__":
    asyncio.run(main())