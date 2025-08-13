"""
hybrid_video_generator.py - Cost-Optimized Hybrid Video Generation
Combines AI avatar, voice-only narration, and screen recordings

Strategy to reduce costs from $1.00 to $0.25 per 5-minute video:
- 30s AI avatar intro ($0.10)
- 3-4 min voice narration + screen recording ($0.05)
- 30s AI avatar outro/CTA ($0.10)

Requirements:
- D-ID/HeyGen API for avatar segments
- ElevenLabs/Amazon Polly for voice-only
- FFmpeg for video assembly
- pip install moviepy pydub boto3
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
import subprocess
from enum import Enum

# Fix Windows Unicode issues
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

# Import our modules
from intelligent_script_generator import DetailedVideoScript, VideoSection
from screenshot_capture import WebsiteScreenshotCapture, Screenshot
from core_test import generate_video_did

# Try to import video libraries
try:
    from moviepy.editor import VideoFileClip, AudioFileClip, ImageClip, CompositeVideoClip, concatenate_videoclips, TextClip
    MOVIEPY_AVAILABLE = True
except ImportError:
    MOVIEPY_AVAILABLE = False
    print("[WARNING] MoviePy not available - video assembly disabled")

try:
    import boto3
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    print("[WARNING] Boto3 not available - Amazon Polly disabled")

class VideoSegmentType(Enum):
    """Types of video segments."""
    AVATAR_INTRO = "avatar_intro"          # AI avatar speaking
    AVATAR_OUTRO = "avatar_outro"          # AI avatar CTA
    SCREEN_RECORDING = "screen_recording"  # Website screenshots
    VOICE_NARRATION = "voice_narration"    # Voice-only with visuals
    DATA_VISUALIZATION = "data_viz"        # Charts and graphs
    COMPARISON = "comparison"               # Side-by-side comparison

@dataclass
class VideoSegment:
    """Individual video segment."""
    segment_id: str
    segment_type: VideoSegmentType
    duration_seconds: int
    
    # Content
    script_text: Optional[str] = None
    visuals: List[str] = field(default_factory=list)  # Image/video paths
    
    # Generated assets
    video_path: Optional[str] = None
    audio_path: Optional[str] = None
    
    # Cost tracking
    generation_cost: float = 0.0
    provider: Optional[str] = None
    
    # Metadata
    generated_at: Optional[datetime] = None
    error: Optional[str] = None

@dataclass
class HybridVideo:
    """Complete hybrid video with all segments."""
    video_id: str
    company_name: str
    total_duration: int
    
    # Segments
    segments: List[VideoSegment] = field(default_factory=list)
    
    # Final video
    output_path: Optional[str] = None
    output_url: Optional[str] = None
    
    # Cost breakdown
    total_cost: float = 0.0
    cost_breakdown: Dict[str, float] = field(default_factory=dict)
    
    # Performance
    generation_time: float = 0.0
    file_size_mb: float = 0.0
    
    # Metadata
    created_at: datetime = field(default_factory=datetime.now)
    script_id: Optional[str] = None

class VoiceGenerator:
    """Generate voice narration using various providers."""
    
    def __init__(self):
        self.providers = self._init_providers()
        self.voice_cache = {}
    
    def _init_providers(self) -> Dict[str, Any]:
        """Initialize available voice providers."""
        providers = {}
        
        # Amazon Polly
        if BOTO3_AVAILABLE and os.environ.get('AWS_ACCESS_KEY_ID'):
            try:
                providers['polly'] = boto3.client(
                    'polly',
                    region_name='us-east-1',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY')
                )
                print("[VOICE] Amazon Polly available")
            except:
                pass
        
        # ElevenLabs
        if os.environ.get('ELEVENLABS_API_KEY'):
            providers['elevenlabs'] = {
                'api_key': os.environ.get('ELEVENLABS_API_KEY'),
                'voice_id': os.environ.get('ELEVENLABS_VOICE_ID', 'pNInz6obpgDQGcFmaJgB')  # Adam
            }
            print("[VOICE] ElevenLabs available")
        
        # Google TTS (would add if API key available)
        
        return providers
    
    def generate_voice(self, text: str, output_path: str,
                      voice_settings: Dict[str, Any] = None) -> Tuple[bool, float]:
        """
        Generate voice narration from text.
        
        Args:
            text: Script text to narrate
            output_path: Where to save audio file
            voice_settings: Voice configuration
            
        Returns:
            (success, cost) tuple
        """
        # Try providers in order of cost preference
        if 'polly' in self.providers:
            return self._generate_polly(text, output_path, voice_settings)
        elif 'elevenlabs' in self.providers:
            return self._generate_elevenlabs(text, output_path, voice_settings)
        else:
            print("[VOICE] No voice providers available")
            return False, 0.0
    
    def _generate_polly(self, text: str, output_path: str,
                       settings: Dict[str, Any] = None) -> Tuple[bool, float]:
        """Generate using Amazon Polly (cheapest option)."""
        try:
            polly = self.providers['polly']
            
            # Default settings
            voice_id = settings.get('voice_id', 'Matthew') if settings else 'Matthew'
            engine = settings.get('engine', 'neural') if settings else 'neural'
            
            # Generate speech
            response = polly.synthesize_speech(
                Text=text,
                OutputFormat='mp3',
                VoiceId=voice_id,
                Engine=engine
            )
            
            # Save audio
            with open(output_path, 'wb') as f:
                f.write(response['AudioStream'].read())
            
            # Calculate cost (~$0.016 per 1000 chars for neural)
            char_count = len(text)
            cost = (char_count / 1000) * 0.016
            
            print(f"[POLLY] Generated {char_count} chars for ${cost:.3f}")
            return True, cost
            
        except Exception as e:
            print(f"[POLLY ERROR] {str(e)}")
            return False, 0.0
    
    def _generate_elevenlabs(self, text: str, output_path: str,
                           settings: Dict[str, Any] = None) -> Tuple[bool, float]:
        """Generate using ElevenLabs (better quality, higher cost)."""
        try:
            import requests
            
            config = self.providers['elevenlabs']
            voice_id = settings.get('voice_id', config['voice_id']) if settings else config['voice_id']
            
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": config['api_key']
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                
                # Calculate cost (~$0.30 per 1000 chars)
                char_count = len(text)
                cost = (char_count / 1000) * 0.30
                
                print(f"[ELEVENLABS] Generated {char_count} chars for ${cost:.3f}")
                return True, cost
            else:
                print(f"[ELEVENLABS ERROR] {response.status_code}: {response.text}")
                return False, 0.0
                
        except Exception as e:
            print(f"[ELEVENLABS ERROR] {str(e)}")
            return False, 0.0

class HybridVideoGenerator:
    """Generate cost-optimized hybrid videos."""
    
    def __init__(self, output_dir: str = "videos"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.voice_generator = VoiceGenerator()
        self.screenshot_capture = WebsiteScreenshotCapture()
        
        # Cost configuration (per second)
        self.cost_per_second = {
            VideoSegmentType.AVATAR_INTRO: 0.003,      # ~$0.10 for 30s
            VideoSegmentType.AVATAR_OUTRO: 0.003,      
            VideoSegmentType.VOICE_NARRATION: 0.0003,  # ~$0.01 for 30s
            VideoSegmentType.SCREEN_RECORDING: 0.0001,  # Minimal cost
            VideoSegmentType.DATA_VISUALIZATION: 0.0001,
            VideoSegmentType.COMPARISON: 0.0001
        }
    
    def generate_hybrid_video(self, script: DetailedVideoScript,
                            website_url: str,
                            optimization_level: str = "balanced") -> HybridVideo:
        """
        Generate complete hybrid video from script.
        
        Args:
            script: Detailed video script
            website_url: Company website for screenshots
            optimization_level: "quality", "balanced", or "cost"
            
        Returns:
            HybridVideo object with all segments
        """
        print(f"[HYBRID] Generating video for {script.company_name}")
        print(f"[HYBRID] Optimization: {optimization_level}")
        
        start_time = time.time()
        
        # Create video object
        video = HybridVideo(
            video_id=self._generate_video_id(),
            company_name=script.company_name,
            total_duration=script.total_duration_seconds,
            script_id=script.script_id
        )
        
        # Plan segments based on optimization level
        segment_plan = self._plan_segments(script, optimization_level)
        
        # Capture screenshots for visual segments
        print("[HYBRID] Capturing website screenshots...")
        screenshots = self.screenshot_capture.capture_website_screenshots(website_url)
        
        # Generate each segment
        for segment_config in segment_plan:
            segment = self._generate_segment(segment_config, script, screenshots)
            video.segments.append(segment)
            video.total_cost += segment.generation_cost
            video.cost_breakdown[segment.segment_type.value] = segment.generation_cost
        
        # Assemble final video
        if MOVIEPY_AVAILABLE:
            print("[HYBRID] Assembling final video...")
            video.output_path = self._assemble_video(video)
        else:
            print("[HYBRID] MoviePy not available - segments generated but not assembled")
        
        video.generation_time = time.time() - start_time
        
        # Summary
        print(f"\n[HYBRID COMPLETE]")
        print(f"Duration: {video.total_duration}s")
        print(f"Segments: {len(video.segments)}")
        print(f"Total Cost: ${video.total_cost:.2f}")
        print(f"Generation Time: {video.generation_time:.1f}s")
        
        if video.output_path:
            print(f"Output: {video.output_path}")
        
        return video
    
    def _plan_segments(self, script: DetailedVideoScript,
                      optimization_level: str) -> List[Dict[str, Any]]:
        """Plan video segments based on optimization level."""
        
        if optimization_level == "cost":
            # Minimum avatar, maximum voice-only
            return [
                {
                    'type': VideoSegmentType.AVATAR_INTRO,
                    'duration': 15,
                    'sections': [VideoSection.HOOK]
                },
                {
                    'type': VideoSegmentType.VOICE_NARRATION,
                    'duration': 210,  # 3.5 minutes
                    'sections': [
                        VideoSection.CREDIBILITY,
                        VideoSection.PROBLEM_DEEP_DIVE,
                        VideoSection.OPPORTUNITY_1,
                        VideoSection.OPPORTUNITY_2,
                        VideoSection.OPPORTUNITY_3,
                        VideoSection.ROI_BREAKDOWN
                    ]
                },
                {
                    'type': VideoSegmentType.AVATAR_OUTRO,
                    'duration': 15,
                    'sections': [VideoSection.CTA]
                }
            ]
            
        elif optimization_level == "quality":
            # More avatar time for engagement
            return [
                {
                    'type': VideoSegmentType.AVATAR_INTRO,
                    'duration': 30,
                    'sections': [VideoSection.HOOK, VideoSection.CREDIBILITY]
                },
                {
                    'type': VideoSegmentType.SCREEN_RECORDING,
                    'duration': 60,
                    'sections': [VideoSection.PROBLEM_DEEP_DIVE]
                },
                {
                    'type': VideoSegmentType.AVATAR_INTRO,  # Mid-video avatar
                    'duration': 30,
                    'sections': [VideoSection.OPPORTUNITY_1]
                },
                {
                    'type': VideoSegmentType.VOICE_NARRATION,
                    'duration': 90,
                    'sections': [VideoSection.OPPORTUNITY_2, VideoSection.OPPORTUNITY_3]
                },
                {
                    'type': VideoSegmentType.DATA_VISUALIZATION,
                    'duration': 30,
                    'sections': [VideoSection.ROI_BREAKDOWN]
                },
                {
                    'type': VideoSegmentType.AVATAR_OUTRO,
                    'duration': 30,
                    'sections': [VideoSection.URGENCY, VideoSection.CTA]
                }
            ]
            
        else:  # balanced
            return [
                {
                    'type': VideoSegmentType.AVATAR_INTRO,
                    'duration': 20,
                    'sections': [VideoSection.HOOK]
                },
                {
                    'type': VideoSegmentType.SCREEN_RECORDING,
                    'duration': 60,
                    'sections': [VideoSection.PROBLEM_DEEP_DIVE]
                },
                {
                    'type': VideoSegmentType.VOICE_NARRATION,
                    'duration': 120,
                    'sections': [
                        VideoSection.OPPORTUNITY_1,
                        VideoSection.OPPORTUNITY_2,
                        VideoSection.OPPORTUNITY_3,
                        VideoSection.ROI_BREAKDOWN
                    ]
                },
                {
                    'type': VideoSegmentType.AVATAR_OUTRO,
                    'duration': 20,
                    'sections': [VideoSection.CTA]
                }
            ]
    
    def _generate_segment(self, segment_config: Dict[str, Any],
                        script: DetailedVideoScript,
                        screenshots: List[Screenshot]) -> VideoSegment:
        """Generate individual video segment."""
        
        segment = VideoSegment(
            segment_id=self._generate_segment_id(),
            segment_type=segment_config['type'],
            duration_seconds=segment_config['duration']
        )
        
        # Get script text for this segment
        script_parts = []
        for section in segment_config['sections']:
            if section in script.sections:
                script_parts.append(script.sections[section])
        segment.script_text = " ".join(script_parts)
        
        # Generate based on type
        if segment.segment_type in [VideoSegmentType.AVATAR_INTRO, VideoSegmentType.AVATAR_OUTRO]:
            # Generate avatar video
            segment = self._generate_avatar_segment(segment)
            
        elif segment.segment_type == VideoSegmentType.VOICE_NARRATION:
            # Generate voice + visuals
            segment = self._generate_voice_segment(segment, screenshots)
            
        elif segment.segment_type == VideoSegmentType.SCREEN_RECORDING:
            # Generate screen recording with voice
            segment = self._generate_screen_segment(segment, screenshots)
            
        elif segment.segment_type == VideoSegmentType.DATA_VISUALIZATION:
            # Generate data viz with voice
            segment = self._generate_dataviz_segment(segment)
        
        # Calculate cost
        segment.generation_cost = self.cost_per_second[segment.segment_type] * segment.duration_seconds
        
        return segment
    
    def _generate_avatar_segment(self, segment: VideoSegment) -> VideoSegment:
        """Generate AI avatar video segment."""
        try:
            # Use D-ID for avatar
            result = generate_video_did(segment.script_text)
            
            if result and result.get('success'):
                segment.video_path = f"avatar_{segment.segment_id}.mp4"  # Would download
                segment.provider = "D-ID"
                print(f"[AVATAR] Generated {segment.duration_seconds}s avatar segment")
            else:
                segment.error = "Avatar generation failed"
                # Fallback to voice-only
                segment = self._generate_voice_segment(segment, [])
                
        except Exception as e:
            segment.error = str(e)
            print(f"[AVATAR ERROR] {str(e)}")
        
        return segment
    
    def _generate_voice_segment(self, segment: VideoSegment,
                              screenshots: List[Screenshot]) -> VideoSegment:
        """Generate voice narration with static visuals."""
        try:
            # Generate voice
            audio_path = self.output_dir / f"voice_{segment.segment_id}.mp3"
            success, cost = self.voice_generator.generate_voice(
                segment.script_text,
                str(audio_path)
            )
            
            if success:
                segment.audio_path = str(audio_path)
                segment.generation_cost = cost
                
                # Add screenshot visuals
                if screenshots:
                    segment.visuals = [s.image_path for s in screenshots[:3] if s.image_path]
                
                # Create video with audio + images
                if MOVIEPY_AVAILABLE and segment.visuals:
                    segment.video_path = self._create_voice_video(
                        segment.audio_path,
                        segment.visuals,
                        segment.duration_seconds
                    )
                
                print(f"[VOICE] Generated {segment.duration_seconds}s voice segment")
            else:
                segment.error = "Voice generation failed"
                
        except Exception as e:
            segment.error = str(e)
            print(f"[VOICE ERROR] {str(e)}")
        
        return segment
    
    def _generate_screen_segment(self, segment: VideoSegment,
                               screenshots: List[Screenshot]) -> VideoSegment:
        """Generate screen recording segment."""
        # For now, use screenshots as slideshow
        # In production, would use actual screen recording
        return self._generate_voice_segment(segment, screenshots)
    
    def _generate_dataviz_segment(self, segment: VideoSegment) -> VideoSegment:
        """Generate data visualization segment."""
        # Would generate charts/graphs here
        # For now, use voice segment
        return self._generate_voice_segment(segment, [])
    
    def _create_voice_video(self, audio_path: str,
                          image_paths: List[str],
                          duration: int) -> str:
        """Create video from audio + images."""
        if not MOVIEPY_AVAILABLE:
            return None
        
        try:
            # Load audio
            audio = AudioFileClip(audio_path)
            
            # Create image slideshow
            clips = []
            image_duration = duration / len(image_paths) if image_paths else duration
            
            for img_path in image_paths:
                if os.path.exists(img_path):
                    img_clip = ImageClip(img_path, duration=image_duration)
                    clips.append(img_clip)
            
            if clips:
                video = concatenate_videoclips(clips)
                video = video.set_audio(audio)
                
                # Save
                output_path = self.output_dir / f"voice_video_{self._generate_segment_id()}.mp4"
                video.write_videofile(str(output_path), fps=24, codec='libx264', audio_codec='aac')
                
                return str(output_path)
                
        except Exception as e:
            print(f"[VIDEO CREATE ERROR] {str(e)}")
        
        return None
    
    def _assemble_video(self, video: HybridVideo) -> str:
        """Assemble all segments into final video."""
        if not MOVIEPY_AVAILABLE:
            return None
        
        try:
            clips = []
            
            for segment in video.segments:
                if segment.video_path and os.path.exists(segment.video_path):
                    clip = VideoFileClip(segment.video_path)
                    clips.append(clip)
                elif segment.audio_path and segment.visuals:
                    # Create video from audio + images
                    video_path = self._create_voice_video(
                        segment.audio_path,
                        segment.visuals,
                        segment.duration_seconds
                    )
                    if video_path:
                        clip = VideoFileClip(video_path)
                        clips.append(clip)
            
            if clips:
                final_video = concatenate_videoclips(clips)
                output_path = self.output_dir / f"final_{video.video_id}.mp4"
                final_video.write_videofile(
                    str(output_path),
                    fps=24,
                    codec='libx264',
                    audio_codec='aac'
                )
                
                # Get file size
                video.file_size_mb = os.path.getsize(output_path) / (1024 * 1024)
                
                return str(output_path)
                
        except Exception as e:
            print(f"[ASSEMBLY ERROR] {str(e)}")
        
        return None
    
    def _generate_video_id(self) -> str:
        """Generate unique video ID."""
        import hashlib
        return hashlib.md5(f"{datetime.now().isoformat()}".encode()).hexdigest()[:8]
    
    def _generate_segment_id(self) -> str:
        """Generate unique segment ID."""
        import hashlib
        import random
        return hashlib.md5(f"{datetime.now().isoformat()}{random.random()}".encode()).hexdigest()[:8]

def calculate_cost_savings(traditional_cost: float, hybrid_cost: float,
                         videos_per_month: int) -> Dict[str, float]:
    """Calculate cost savings from hybrid approach."""
    
    monthly_traditional = traditional_cost * videos_per_month
    monthly_hybrid = hybrid_cost * videos_per_month
    monthly_savings = monthly_traditional - monthly_hybrid
    
    return {
        'traditional_cost_per_video': traditional_cost,
        'hybrid_cost_per_video': hybrid_cost,
        'savings_per_video': traditional_cost - hybrid_cost,
        'monthly_traditional': monthly_traditional,
        'monthly_hybrid': monthly_hybrid,
        'monthly_savings': monthly_savings,
        'annual_savings': monthly_savings * 12,
        'cost_reduction_percent': ((traditional_cost - hybrid_cost) / traditional_cost) * 100
    }

def test_hybrid_generation():
    """Test hybrid video generation."""
    from intelligent_script_generator import IntelligentScriptGenerator
    from enrichment_engine import DataEnrichmentEngine
    from audit_engine import AutomationAuditEngine
    
    print("=" * 60)
    print("HYBRID VIDEO GENERATION TEST")
    print("=" * 60)
    
    # Generate test script
    print("\n[1/3] Generating test script...")
    enrichment = DataEnrichmentEngine()
    company_data = enrichment.enrich_company("https://www.example.com")
    
    audit = AutomationAuditEngine()
    audit_report = audit.generate_audit("https://www.example.com")
    
    script_gen = IntelligentScriptGenerator()
    script = script_gen.generate_detailed_script(
        company_data,
        audit_report,
        prospect_name="John",
        target_duration=240
    )
    
    # Test hybrid generation
    print("\n[2/3] Generating hybrid video...")
    generator = HybridVideoGenerator()
    
    # Test different optimization levels
    for optimization in ["cost", "balanced", "quality"]:
        print(f"\n--- Testing {optimization} optimization ---")
        video = generator.generate_hybrid_video(
            script,
            "https://www.example.com",
            optimization_level=optimization
        )
        
        print(f"Cost: ${video.total_cost:.2f}")
        print(f"Segments: {len(video.segments)}")
    
    # Calculate savings
    print("\n[3/3] Cost Analysis...")
    savings = calculate_cost_savings(
        traditional_cost=1.00,  # All avatar
        hybrid_cost=0.25,       # Hybrid approach
        videos_per_month=1000
    )
    
    print(f"\nCOST SAVINGS ANALYSIS:")
    print(f"Traditional: ${savings['traditional_cost_per_video']:.2f}/video")
    print(f"Hybrid: ${savings['hybrid_cost_per_video']:.2f}/video")
    print(f"Savings: ${savings['savings_per_video']:.2f}/video ({savings['cost_reduction_percent']:.0f}%)")
    print(f"Monthly Savings: ${savings['monthly_savings']:,.0f}")
    print(f"Annual Savings: ${savings['annual_savings']:,.0f}")

if __name__ == "__main__":
    test_hybrid_generation()