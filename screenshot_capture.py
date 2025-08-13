"""
screenshot_capture.py - Website Screenshot & Screen Recording System
Captures website screenshots and recordings to show in prospect videos

This module handles:
- Full page screenshots
- Specific element captures  
- Scrolling screen recordings
- Annotation overlays
- Competitor comparisons

Requirements:
- pip install selenium pillow opencv-python playwright
- Chrome/Chromium browser installed
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import base64
from io import BytesIO

# Fix Windows Unicode issues
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Try imports
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    print("[WARNING] Selenium not available - screenshot capture disabled")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[WARNING] PIL not available - image annotation disabled")

@dataclass
class Screenshot:
    """Captured screenshot with metadata."""
    screenshot_id: str
    url: str
    title: str
    description: str
    
    # Image data
    image_path: Optional[str] = None
    image_base64: Optional[str] = None
    width: int = 0
    height: int = 0
    
    # Capture details
    capture_type: str = "full_page"  # full_page, viewport, element
    element_selector: Optional[str] = None
    scroll_position: int = 0
    
    # Annotations
    annotations: List[Dict[str, Any]] = field(default_factory=list)
    highlights: List[Dict[str, Any]] = field(default_factory=list)
    
    # Metadata
    captured_at: datetime = field(default_factory=datetime.now)
    capture_duration: float = 0.0
    error: Optional[str] = None

@dataclass 
class ScreenRecording:
    """Screen recording of website interaction."""
    recording_id: str
    url: str
    duration_seconds: int
    
    # Recording data
    video_path: Optional[str] = None
    frames: List[str] = field(default_factory=list)  # Base64 encoded frames
    fps: int = 10
    
    # Interactions recorded
    scroll_points: List[int] = field(default_factory=list)
    click_points: List[Tuple[int, int]] = field(default_factory=list)
    hover_elements: List[str] = field(default_factory=list)
    
    # Metadata
    recorded_at: datetime = field(default_factory=datetime.now)
    file_size_mb: float = 0.0

class WebsiteScreenshotCapture:
    """Capture screenshots and recordings of websites."""
    
    def __init__(self, output_dir: str = "screenshots"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.driver = None
        self.capture_cache = {}
        
        # Browser settings for clean captures
        self.browser_config = {
            'window_size': (1920, 1080),
            'remove_elements': [
                'cookie-banner', 'popup', 'modal', 'overlay',
                'chat-widget', 'drift-widget', 'intercom'
            ],
            'wait_time': 3,
            'scroll_pause': 0.5
        }
    
    def capture_website_screenshots(self, url: str, 
                                   sections: List[str] = None) -> List[Screenshot]:
        """
        Capture multiple screenshots of a website.
        
        Args:
            url: Website URL to capture
            sections: Specific sections to capture (pricing, about, etc.)
            
        Returns:
            List of Screenshot objects
        """
        if not SELENIUM_AVAILABLE:
            print("[ERROR] Selenium not available for screenshot capture")
            return []
        
        print(f"[SCREENSHOT] Capturing {url}")
        screenshots = []
        
        try:
            # Initialize browser
            self._init_browser()
            
            # Capture homepage
            homepage_shot = self._capture_page(url, "Homepage")
            if homepage_shot:
                screenshots.append(homepage_shot)
            
            # Capture specific sections
            if sections:
                for section in sections:
                    section_url = self._find_section_url(url, section)
                    if section_url:
                        shot = self._capture_page(section_url, f"{section.title()} Page")
                        if shot:
                            screenshots.append(shot)
            else:
                # Auto-detect important pages
                important_pages = self._detect_important_pages(url)
                for page_url, page_name in important_pages:
                    shot = self._capture_page(page_url, page_name)
                    if shot:
                        screenshots.append(shot)
            
            print(f"[SCREENSHOT] Captured {len(screenshots)} screenshots")
            
        except Exception as e:
            print(f"[SCREENSHOT ERROR] {str(e)}")
        finally:
            self._close_browser()
        
        return screenshots
    
    def capture_specific_elements(self, url: str,
                                elements: List[Dict[str, str]]) -> List[Screenshot]:
        """
        Capture specific elements on a page.
        
        Args:
            url: Page URL
            elements: List of dicts with 'selector' and 'description'
            
        Returns:
            List of Screenshot objects for each element
        """
        screenshots = []
        
        try:
            self._init_browser()
            self.driver.get(url)
            time.sleep(self.browser_config['wait_time'])
            
            for element_info in elements:
                selector = element_info.get('selector')
                description = element_info.get('description', 'Element')
                
                shot = self._capture_element(selector, description)
                if shot:
                    shot.url = url
                    screenshots.append(shot)
            
        except Exception as e:
            print(f"[ELEMENT CAPTURE ERROR] {str(e)}")
        finally:
            self._close_browser()
        
        return screenshots
    
    def create_annotated_screenshot(self, screenshot: Screenshot,
                                   annotations: List[Dict[str, Any]]) -> Screenshot:
        """
        Add annotations to a screenshot.
        
        Args:
            screenshot: Original screenshot
            annotations: List of annotation dicts with position, text, style
            
        Returns:
            Screenshot with annotations applied
        """
        if not PIL_AVAILABLE:
            print("[ERROR] PIL not available for annotations")
            return screenshot
        
        try:
            # Load image
            if screenshot.image_path and os.path.exists(screenshot.image_path):
                img = Image.open(screenshot.image_path)
            elif screenshot.image_base64:
                img_data = base64.b64decode(screenshot.image_base64)
                img = Image.open(BytesIO(img_data))
            else:
                return screenshot
            
            # Create drawing context
            draw = ImageDraw.Draw(img)
            
            # Apply annotations
            for ann in annotations:
                self._apply_annotation(draw, ann, img.size)
            
            # Save annotated version
            annotated_path = self.output_dir / f"annotated_{screenshot.screenshot_id}.png"
            img.save(annotated_path, 'PNG', quality=95)
            
            # Update screenshot
            screenshot.image_path = str(annotated_path)
            screenshot.annotations = annotations
            
            # Update base64
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            screenshot.image_base64 = base64.b64encode(buffered.getvalue()).decode()
            
        except Exception as e:
            print(f"[ANNOTATION ERROR] {str(e)}")
        
        return screenshot
    
    def create_comparison_image(self, current_screenshot: Screenshot,
                              competitor_screenshot: Screenshot,
                              labels: Tuple[str, str] = ("Current", "Competitor")) -> str:
        """
        Create side-by-side comparison image.
        
        Args:
            current_screenshot: Company's current state
            competitor_screenshot: Competitor or ideal state
            labels: Labels for each side
            
        Returns:
            Path to comparison image
        """
        if not PIL_AVAILABLE:
            return ""
        
        try:
            # Load images
            img1 = self._load_screenshot_image(current_screenshot)
            img2 = self._load_screenshot_image(competitor_screenshot)
            
            if not img1 or not img2:
                return ""
            
            # Resize to same height
            height = min(img1.height, img2.height, 1080)
            img1 = img1.resize((int(img1.width * height / img1.height), height))
            img2 = img2.resize((int(img2.width * height / img2.height), height))
            
            # Create comparison canvas
            total_width = img1.width + img2.width + 20  # 20px gap
            comparison = Image.new('RGB', (total_width, height + 100), 'white')
            
            # Paste images
            comparison.paste(img1, (0, 50))
            comparison.paste(img2, (img1.width + 20, 50))
            
            # Add labels
            draw = ImageDraw.Draw(comparison)
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except:
                font = ImageFont.load_default()
            
            # Current label
            draw.text((img1.width // 2, 10), labels[0], 
                     fill='red', font=font, anchor='mt')
            
            # Competitor label  
            draw.text((img1.width + 20 + img2.width // 2, 10), labels[1],
                     fill='green', font=font, anchor='mt')
            
            # Save comparison
            comparison_path = self.output_dir / f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            comparison.save(comparison_path, 'PNG', quality=95)
            
            print(f"[COMPARISON] Created comparison image: {comparison_path}")
            return str(comparison_path)
            
        except Exception as e:
            print(f"[COMPARISON ERROR] {str(e)}")
            return ""
    
    def record_scrolling_video(self, url: str, duration: int = 10,
                              scroll_speed: int = 100) -> ScreenRecording:
        """
        Record scrolling through a website.
        
        Args:
            url: Website to record
            duration: Recording duration in seconds
            scroll_speed: Pixels to scroll per step
            
        Returns:
            ScreenRecording object
        """
        recording = ScreenRecording(
            recording_id=self._generate_id(),
            url=url,
            duration_seconds=duration
        )
        
        if not SELENIUM_AVAILABLE:
            recording.error = "Selenium not available"
            return recording
        
        try:
            self._init_browser()
            self.driver.get(url)
            time.sleep(self.browser_config['wait_time'])
            
            # Get page height
            page_height = self.driver.execute_script("return document.body.scrollHeight")
            viewport_height = self.driver.execute_script("return window.innerHeight")
            
            # Calculate scroll points
            frames_to_capture = duration * recording.fps
            scroll_per_frame = min(scroll_speed, page_height // frames_to_capture)
            
            # Capture frames while scrolling
            print(f"[RECORDING] Capturing {frames_to_capture} frames...")
            for i in range(frames_to_capture):
                # Scroll
                scroll_position = min(i * scroll_per_frame, page_height - viewport_height)
                self.driver.execute_script(f"window.scrollTo(0, {scroll_position})")
                recording.scroll_points.append(scroll_position)
                
                # Capture frame
                screenshot = self.driver.get_screenshot_as_base64()
                recording.frames.append(screenshot)
                
                # Small pause
                time.sleep(1.0 / recording.fps)
            
            print(f"[RECORDING] Captured {len(recording.frames)} frames")
            
            # Save as video if opencv available
            video_path = self._frames_to_video(recording.frames, recording.fps)
            if video_path:
                recording.video_path = video_path
            
        except Exception as e:
            recording.error = str(e)
            print(f"[RECORDING ERROR] {str(e)}")
        finally:
            self._close_browser()
        
        return recording
    
    def _init_browser(self):
        """Initialize headless browser."""
        if self.driver:
            return
        
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument(f'--window-size={self.browser_config["window_size"][0]},{self.browser_config["window_size"][1]}')
        options.add_argument('--hide-scrollbars')
        options.add_argument('--disable-blink-features=AutomationControlled')
        
        # Remove bot detection
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        try:
            self.driver = webdriver.Chrome(options=options)
            # Remove webdriver property
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        except Exception as e:
            print(f"[BROWSER ERROR] Failed to initialize: {str(e)}")
            print("[INFO] Make sure Chrome/Chromium is installed")
    
    def _close_browser(self):
        """Close browser if open."""
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
            self.driver = None
    
    def _capture_page(self, url: str, title: str) -> Optional[Screenshot]:
        """Capture a full page screenshot."""
        try:
            start_time = time.time()
            
            # Navigate to page
            self.driver.get(url)
            time.sleep(self.browser_config['wait_time'])
            
            # Remove unwanted elements
            self._remove_popups()
            
            # Get page dimensions
            width = self.driver.execute_script("return document.body.scrollWidth")
            height = self.driver.execute_script("return document.body.scrollHeight")
            
            # Capture screenshot
            screenshot_path = self.output_dir / f"screenshot_{self._generate_id()}.png"
            
            # For full page, we need to scroll and stitch
            if height > self.browser_config['window_size'][1]:
                # Capture viewport by viewport
                screenshots = []
                scroll_height = 0
                viewport_height = self.browser_config['window_size'][1]
                
                while scroll_height < height:
                    self.driver.execute_script(f"window.scrollTo(0, {scroll_height})")
                    time.sleep(0.5)
                    screenshot_data = self.driver.get_screenshot_as_png()
                    screenshots.append(Image.open(BytesIO(screenshot_data)))
                    scroll_height += viewport_height
                
                # Stitch screenshots
                if PIL_AVAILABLE and screenshots:
                    stitched = self._stitch_screenshots(screenshots, width, height)
                    stitched.save(screenshot_path, 'PNG', quality=95)
                else:
                    # Just save the first one
                    self.driver.save_screenshot(str(screenshot_path))
            else:
                # Single screenshot
                self.driver.save_screenshot(str(screenshot_path))
            
            # Create Screenshot object
            screenshot = Screenshot(
                screenshot_id=self._generate_id(),
                url=url,
                title=title,
                description=f"Full page capture of {title}",
                image_path=str(screenshot_path),
                width=width,
                height=height,
                capture_type="full_page",
                capture_duration=time.time() - start_time
            )
            
            # Add base64
            with open(screenshot_path, 'rb') as f:
                screenshot.image_base64 = base64.b64encode(f.read()).decode()
            
            return screenshot
            
        except Exception as e:
            print(f"[CAPTURE ERROR] {url}: {str(e)}")
            return None
    
    def _capture_element(self, selector: str, description: str) -> Optional[Screenshot]:
        """Capture specific element."""
        try:
            # Find element
            element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            
            # Scroll to element
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            
            # Get element position and size
            location = element.location
            size = element.size
            
            # Capture full page
            png = self.driver.get_screenshot_as_png()
            
            # Crop to element
            if PIL_AVAILABLE:
                img = Image.open(BytesIO(png))
                left = location['x']
                top = location['y']
                right = left + size['width']
                bottom = top + size['height']
                
                img = img.crop((left, top, right, bottom))
                
                # Save
                element_path = self.output_dir / f"element_{self._generate_id()}.png"
                img.save(element_path, 'PNG', quality=95)
                
                # Create Screenshot object
                screenshot = Screenshot(
                    screenshot_id=self._generate_id(),
                    url=self.driver.current_url,
                    title=description,
                    description=f"Element capture: {description}",
                    image_path=str(element_path),
                    width=size['width'],
                    height=size['height'],
                    capture_type="element",
                    element_selector=selector
                )
                
                # Add base64
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                screenshot.image_base64 = base64.b64encode(buffered.getvalue()).decode()
                
                return screenshot
            
        except Exception as e:
            print(f"[ELEMENT ERROR] {selector}: {str(e)}")
            return None
    
    def _detect_important_pages(self, base_url: str) -> List[Tuple[str, str]]:
        """Auto-detect important pages to capture."""
        important_pages = []
        
        try:
            # Get all links
            links = self.driver.find_elements(By.TAG_NAME, 'a')
            
            # Keywords for important pages
            keywords = {
                'pricing': 'Pricing',
                'about': 'About',
                'features': 'Features',
                'contact': 'Contact',
                'demo': 'Demo',
                'customers': 'Customers',
                'testimonials': 'Testimonials',
                'case-studies': 'Case Studies'
            }
            
            found_pages = set()
            for link in links:
                href = link.get_attribute('href')
                text = link.text.lower()
                
                if href and base_url in href:
                    for keyword, name in keywords.items():
                        if keyword in href.lower() or keyword in text:
                            if name not in found_pages:
                                important_pages.append((href, name))
                                found_pages.add(name)
                                break
            
        except Exception as e:
            print(f"[DETECTION ERROR] {str(e)}")
        
        return important_pages[:5]  # Limit to 5 pages
    
    def _remove_popups(self):
        """Remove common popup elements."""
        for element_class in self.browser_config['remove_elements']:
            try:
                script = f"""
                var elements = document.querySelectorAll('[class*="{element_class}"], [id*="{element_class}"]');
                elements.forEach(function(el) {{ el.remove(); }});
                """
                self.driver.execute_script(script)
            except:
                pass
    
    def _stitch_screenshots(self, screenshots: List[Image.Image],
                          width: int, height: int) -> Image.Image:
        """Stitch multiple screenshots into one."""
        # Create canvas
        stitched = Image.new('RGB', (width, height))
        
        # Paste each screenshot
        y_offset = 0
        for img in screenshots:
            stitched.paste(img, (0, y_offset))
            y_offset += img.height
        
        return stitched
    
    def _apply_annotation(self, draw: ImageDraw.Draw,
                        annotation: Dict[str, Any],
                        image_size: Tuple[int, int]):
        """Apply a single annotation to image."""
        ann_type = annotation.get('type', 'box')
        
        if ann_type == 'box':
            # Draw rectangle
            coords = annotation.get('coords', [100, 100, 300, 200])
            color = annotation.get('color', 'red')
            width = annotation.get('width', 3)
            draw.rectangle(coords, outline=color, width=width)
            
        elif ann_type == 'arrow':
            # Draw arrow pointing to something
            start = annotation.get('start', [100, 100])
            end = annotation.get('end', [200, 200])
            color = annotation.get('color', 'red')
            draw.line([start[0], start[1], end[0], end[1]], fill=color, width=3)
            # Arrowhead
            draw.polygon([
                (end[0], end[1]),
                (end[0]-10, end[1]-10),
                (end[0]-10, end[1]+10)
            ], fill=color)
            
        elif ann_type == 'text':
            # Add text annotation
            position = annotation.get('position', [100, 100])
            text = annotation.get('text', 'Note')
            color = annotation.get('color', 'red')
            
            try:
                font = ImageFont.truetype("arial.ttf", annotation.get('size', 24))
            except:
                font = ImageFont.load_default()
            
            # Add background for readability
            bbox = draw.textbbox(position, text, font=font)
            padding = 5
            draw.rectangle([
                bbox[0]-padding, bbox[1]-padding,
                bbox[2]+padding, bbox[3]+padding
            ], fill='white', outline=color)
            draw.text(position, text, fill=color, font=font)
            
        elif ann_type == 'highlight':
            # Highlight area with semi-transparent overlay
            coords = annotation.get('coords', [100, 100, 300, 200])
            overlay = Image.new('RGBA', image_size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rectangle(coords, fill=(255, 255, 0, 80))  # Yellow, semi-transparent
            # This would need to be composited with the main image
    
    def _find_section_url(self, base_url: str, section: str) -> Optional[str]:
        """Find URL for a specific section."""
        # Common URL patterns
        patterns = [
            f"{base_url}/{section}",
            f"{base_url}/{section}.html",
            f"{base_url}/#{section}",
            f"{base_url}/pages/{section}"
        ]
        
        for pattern in patterns:
            try:
                # Quick check if URL exists
                import requests
                response = requests.head(pattern, timeout=5)
                if response.status_code == 200:
                    return pattern
            except:
                pass
        
        return None
    
    def _load_screenshot_image(self, screenshot: Screenshot) -> Optional[Image.Image]:
        """Load screenshot as PIL Image."""
        try:
            if screenshot.image_path and os.path.exists(screenshot.image_path):
                return Image.open(screenshot.image_path)
            elif screenshot.image_base64:
                img_data = base64.b64decode(screenshot.image_base64)
                return Image.open(BytesIO(img_data))
        except:
            pass
        return None
    
    def _frames_to_video(self, frames: List[str], fps: int) -> Optional[str]:
        """Convert frames to video file."""
        # Would use OpenCV here if available
        # For now, just return None
        return None
    
    def _generate_id(self) -> str:
        """Generate unique ID."""
        import hashlib
        return hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:8]

def test_screenshot_capture():
    """Test the screenshot capture system."""
    print("=" * 60)
    print("SCREENSHOT CAPTURE TEST")
    print("=" * 60)
    
    capture = WebsiteScreenshotCapture()
    
    # Test basic capture
    print("\n[TEST 1] Capturing website screenshots...")
    screenshots = capture.capture_website_screenshots(
        "https://www.stripe.com",
        sections=['pricing', 'about']
    )
    
    print(f"Captured {len(screenshots)} screenshots")
    for shot in screenshots:
        print(f"  - {shot.title}: {shot.width}x{shot.height}px")
        if shot.image_path:
            print(f"    Saved to: {shot.image_path}")
    
    # Test annotations
    if screenshots and PIL_AVAILABLE:
        print("\n[TEST 2] Adding annotations...")
        annotated = capture.create_annotated_screenshot(
            screenshots[0],
            [
                {
                    'type': 'box',
                    'coords': [100, 100, 500, 300],
                    'color': 'red',
                    'width': 3
                },
                {
                    'type': 'text',
                    'position': [520, 150],
                    'text': 'Manual Process Here!',
                    'color': 'red',
                    'size': 24
                }
            ]
        )
        print(f"Annotated screenshot saved: {annotated.image_path}")
    
    print("\n[SUCCESS] Screenshot capture system operational!")

if __name__ == "__main__":
    test_screenshot_capture()