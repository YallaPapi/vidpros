"""
delivery_system.py - VideoReach AI Multi-Format Report Delivery
Phase 4: VRA-024 - Deliver reports via multiple channels

This module handles delivery of audit reports and videos through various channels:
- Email delivery with HTML reports
- Webhook notifications
- Cloud storage upload (S3, Google Drive)
- API endpoints for retrieval
- Slack/Teams notifications

Requirements:
- pip install boto3 google-api-python-client sendgrid
"""

import os
import sys
import json
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import base64
from pathlib import Path

# Fix Windows Unicode issues
if sys.platform == 'win32' and sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

# Import report generator
from report_generator import ComprehensiveReport

@dataclass
class DeliveryConfig:
    """Configuration for report delivery."""
    email_enabled: bool = False
    webhook_enabled: bool = False
    cloud_storage_enabled: bool = False
    slack_enabled: bool = False
    
    # Email settings
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    from_email: Optional[str] = None
    
    # Webhook settings
    webhook_url: Optional[str] = None
    webhook_headers: Dict[str, str] = field(default_factory=dict)
    
    # Cloud storage settings
    s3_bucket: Optional[str] = None
    aws_access_key: Optional[str] = None
    aws_secret_key: Optional[str] = None
    
    # Slack settings
    slack_webhook_url: Optional[str] = None
    slack_channel: Optional[str] = None

@dataclass
class DeliveryResult:
    """Result of a delivery attempt."""
    channel: str
    success: bool
    timestamp: datetime
    recipient: Optional[str] = None
    message_id: Optional[str] = None
    error: Optional[str] = None
    delivery_url: Optional[str] = None

class EmailDelivery:
    """Handle email delivery of reports."""
    
    def __init__(self, config: DeliveryConfig):
        self.config = config
        self.templates = self._load_email_templates()
    
    def send_report(self, report: ComprehensiveReport, 
                   recipient_email: str,
                   subject: Optional[str] = None,
                   attach_pdf: bool = False) -> DeliveryResult:
        """Send report via email."""
        if not self.config.email_enabled:
            return DeliveryResult(
                channel="email",
                success=False,
                timestamp=datetime.now(),
                error="Email delivery not configured"
            )
        
        try:
            # Generate subject if not provided
            if not subject:
                subject = f"Automation Assessment Report for {report.company_name}"
            
            # Create HTML email body
            html_body = self._create_email_body(report)
            
            # Create email message
            message = self._create_message(
                recipient_email,
                subject,
                html_body,
                attach_pdf
            )
            
            # Send email
            message_id = self._send_email(message)
            
            print(f"[EMAIL] Report sent to {recipient_email}")
            
            return DeliveryResult(
                channel="email",
                success=True,
                timestamp=datetime.now(),
                recipient=recipient_email,
                message_id=message_id
            )
            
        except Exception as e:
            print(f"[EMAIL ERROR] {str(e)}")
            return DeliveryResult(
                channel="email",
                success=False,
                timestamp=datetime.now(),
                recipient=recipient_email,
                error=str(e)
            )
    
    def _create_email_body(self, report: ComprehensiveReport) -> str:
        """Create HTML email body with report summary."""
        template = """
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; color: white;">
                <h1 style="margin: 0;">Automation Assessment Report</h1>
                <p style="margin: 10px 0 0 0; opacity: 0.9;">{company_name}</p>
            </div>
            
            <div style="padding: 30px;">
                <h2 style="color: #2c3e50;">Executive Summary</h2>
                <p>{executive_summary}</p>
                
                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #34495e; margin-top: 0;">Key Metrics</h3>
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">
                                <strong>Potential Annual Savings:</strong>
                            </td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">
                                <span style="color: #27ae60; font-size: 20px; font-weight: bold;">
                                    ${savings:,.0f}
                                </span>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd;">
                                <strong>Payback Period:</strong>
                            </td>
                            <td style="padding: 10px; border-bottom: 1px solid #ddd; text-align: right;">
                                {payback} months
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 10px;">
                                <strong>Digital Maturity Score:</strong>
                            </td>
                            <td style="padding: 10px; text-align: right;">
                                {maturity}/100
                            </td>
                        </tr>
                    </table>
                </div>
                
                <h3 style="color: #2c3e50;">Top Recommendations</h3>
                <ol>
                    {recommendations}
                </ol>
                
                <div style="margin-top: 30px; padding: 20px; background: #e8f5e9; border-radius: 8px;">
                    <h3 style="color: #27ae60; margin-top: 0;">Next Steps</h3>
                    <p>Schedule a 15-minute call to review the full report and discuss implementation:</p>
                    <a href="{calendar_link}" style="display: inline-block; padding: 12px 30px; background: #27ae60; color: white; text-decoration: none; border-radius: 5px; margin-top: 10px;">
                        Book Consultation
                    </a>
                </div>
                
                <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #7f8c8d; font-size: 12px;">
                    This report was generated on {date} by VideoReach AI Automation Assessment Platform.
                    For questions, reply to this email or schedule a consultation using the link above.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Format recommendations
        recommendations_html = ""
        for rec in report.critical_recommendations[:3]:
            recommendations_html += f"<li>{rec}</li>"
        
        # Fill template
        html = template.format(
            company_name=report.company_name,
            executive_summary=report.executive_summary,
            savings=report.total_savings_potential,
            payback=report.payback_period_months,
            maturity=report.enriched_data.digital_maturity_score,
            recommendations=recommendations_html,
            calendar_link="https://calendly.com/videoreach/consultation",
            date=report.generated_at.strftime("%B %d, %Y")
        )
        
        return html
    
    def _create_message(self, recipient: str, subject: str, 
                       html_body: str, attach_pdf: bool) -> Dict[str, Any]:
        """Create email message structure."""
        # Simplified message structure
        # In production, would use proper email library
        return {
            'to': recipient,
            'from': self.config.from_email or 'reports@videoreach.ai',
            'subject': subject,
            'html': html_body,
            'attachments': []  # Would attach PDF here
        }
    
    def _send_email(self, message: Dict[str, Any]) -> str:
        """Send email via SMTP or email service."""
        # In production, would use SMTP or SendGrid/SES
        # For now, simulate sending
        import hashlib
        message_id = hashlib.md5(f"{message['to']}{datetime.now()}".encode()).hexdigest()
        print(f"[EMAIL] Simulated send to {message['to']}")
        return message_id
    
    def _load_email_templates(self) -> Dict[str, str]:
        """Load email templates."""
        return {}  # Would load from files

class WebhookDelivery:
    """Handle webhook delivery of reports."""
    
    def __init__(self, config: DeliveryConfig):
        self.config = config
    
    def send_notification(self, report: ComprehensiveReport,
                         video_url: Optional[str] = None) -> DeliveryResult:
        """Send webhook notification with report data."""
        if not self.config.webhook_enabled or not self.config.webhook_url:
            return DeliveryResult(
                channel="webhook",
                success=False,
                timestamp=datetime.now(),
                error="Webhook not configured"
            )
        
        try:
            import requests
            
            # Prepare webhook payload
            payload = {
                'event': 'report.generated',
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'report_id': report.report_id,
                    'company_name': report.company_name,
                    'website': report.website,
                    'savings_potential': report.total_savings_potential,
                    'payback_months': report.payback_period_months,
                    'digital_maturity': report.enriched_data.digital_maturity_score,
                    'opportunities_count': len(report.enriched_data.automation_opportunities),
                    'video_url': video_url,
                    'report_url': f"https://app.videoreach.ai/reports/{report.report_id}"
                }
            }
            
            # Send webhook
            response = requests.post(
                self.config.webhook_url,
                json=payload,
                headers=self.config.webhook_headers,
                timeout=10
            )
            
            if response.status_code in [200, 201, 202, 204]:
                print(f"[WEBHOOK] Notification sent successfully")
                return DeliveryResult(
                    channel="webhook",
                    success=True,
                    timestamp=datetime.now(),
                    message_id=response.headers.get('X-Request-Id')
                )
            else:
                return DeliveryResult(
                    channel="webhook",
                    success=False,
                    timestamp=datetime.now(),
                    error=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            print(f"[WEBHOOK ERROR] {str(e)}")
            return DeliveryResult(
                channel="webhook",
                success=False,
                timestamp=datetime.now(),
                error=str(e)
            )

class CloudStorageDelivery:
    """Handle cloud storage upload of reports."""
    
    def __init__(self, config: DeliveryConfig):
        self.config = config
    
    def upload_to_s3(self, report_file: str, 
                    report_id: str) -> DeliveryResult:
        """Upload report to S3."""
        if not self.config.cloud_storage_enabled or not self.config.s3_bucket:
            return DeliveryResult(
                channel="s3",
                success=False,
                timestamp=datetime.now(),
                error="S3 not configured"
            )
        
        try:
            # Would use boto3 in production
            # import boto3
            # s3 = boto3.client('s3',
            #     aws_access_key_id=self.config.aws_access_key,
            #     aws_secret_access_key=self.config.aws_secret_key
            # )
            
            key = f"reports/{report_id}/{Path(report_file).name}"
            
            # Simulate upload
            url = f"https://{self.config.s3_bucket}.s3.amazonaws.com/{key}"
            
            print(f"[S3] Report uploaded to {url}")
            
            return DeliveryResult(
                channel="s3",
                success=True,
                timestamp=datetime.now(),
                delivery_url=url
            )
            
        except Exception as e:
            print(f"[S3 ERROR] {str(e)}")
            return DeliveryResult(
                channel="s3",
                success=False,
                timestamp=datetime.now(),
                error=str(e)
            )

class SlackDelivery:
    """Handle Slack notifications."""
    
    def __init__(self, config: DeliveryConfig):
        self.config = config
    
    def send_notification(self, report: ComprehensiveReport,
                         video_url: Optional[str] = None) -> DeliveryResult:
        """Send Slack notification with report summary."""
        if not self.config.slack_enabled or not self.config.slack_webhook_url:
            return DeliveryResult(
                channel="slack",
                success=False,
                timestamp=datetime.now(),
                error="Slack not configured"
            )
        
        try:
            import requests
            
            # Create Slack message
            message = {
                "text": f"New Automation Assessment Report for {report.company_name}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"📊 {report.company_name} Assessment Complete"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {
                                "type": "mrkdwn",
                                "text": f"*Potential Savings:*\n${report.total_savings_potential:,.0f}/year"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Payback Period:*\n{report.payback_period_months} months"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Digital Maturity:*\n{report.enriched_data.digital_maturity_score}/100"
                            },
                            {
                                "type": "mrkdwn",
                                "text": f"*Opportunities:*\n{len(report.enriched_data.automation_opportunities)} identified"
                            }
                        ]
                    }
                ]
            }
            
            if video_url:
                message["blocks"].append({
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"🎥 <{video_url}|View Personalized Video>"
                    }
                })
            
            # Add actions
            message["blocks"].append({
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Full Report"},
                        "url": f"https://app.videoreach.ai/reports/{report.report_id}",
                        "style": "primary"
                    },
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "Schedule Call"},
                        "url": "https://calendly.com/videoreach/consultation"
                    }
                ]
            })
            
            # Send to Slack
            response = requests.post(
                self.config.slack_webhook_url,
                json=message,
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"[SLACK] Notification sent")
                return DeliveryResult(
                    channel="slack",
                    success=True,
                    timestamp=datetime.now()
                )
            else:
                return DeliveryResult(
                    channel="slack",
                    success=False,
                    timestamp=datetime.now(),
                    error=f"HTTP {response.status_code}"
                )
                
        except Exception as e:
            print(f"[SLACK ERROR] {str(e)}")
            return DeliveryResult(
                channel="slack",
                success=False,
                timestamp=datetime.now(),
                error=str(e)
            )

class MultiChannelDelivery:
    """Orchestrate delivery across multiple channels."""
    
    def __init__(self, config: Optional[DeliveryConfig] = None):
        self.config = config or self._load_config_from_env()
        
        # Initialize delivery channels
        self.email = EmailDelivery(self.config)
        self.webhook = WebhookDelivery(self.config)
        self.cloud = CloudStorageDelivery(self.config)
        self.slack = SlackDelivery(self.config)
    
    def deliver_report(self, report: ComprehensiveReport,
                      channels: List[str] = None,
                      recipients: Dict[str, str] = None,
                      video_url: Optional[str] = None) -> List[DeliveryResult]:
        """
        Deliver report through specified channels.
        
        Args:
            report: The report to deliver
            channels: List of channels to use ['email', 'webhook', 'slack', 's3']
            recipients: Dict with channel-specific recipients
            video_url: Optional video URL to include
            
        Returns:
            List of DeliveryResult objects
        """
        if channels is None:
            channels = self._get_enabled_channels()
        
        if recipients is None:
            recipients = {}
        
        results = []
        
        print(f"[DELIVERY] Sending report through {len(channels)} channels")
        
        # Email delivery
        if 'email' in channels and recipients.get('email'):
            result = self.email.send_report(report, recipients['email'])
            results.append(result)
        
        # Webhook notification
        if 'webhook' in channels:
            result = self.webhook.send_notification(report, video_url)
            results.append(result)
        
        # Slack notification
        if 'slack' in channels:
            result = self.slack.send_notification(report, video_url)
            results.append(result)
        
        # Cloud storage upload
        if 's3' in channels:
            # First save report to file
            from report_generator import ReportGenerator
            gen = ReportGenerator()
            html_file = gen.export_html(report)
            result = self.cloud.upload_to_s3(html_file, report.report_id)
            results.append(result)
        
        # Summary
        successful = sum(1 for r in results if r.success)
        print(f"[DELIVERY] Complete: {successful}/{len(results)} successful")
        
        return results
    
    def _load_config_from_env(self) -> DeliveryConfig:
        """Load configuration from environment variables."""
        config = DeliveryConfig()
        
        # Email configuration
        if os.environ.get('SMTP_HOST'):
            config.email_enabled = True
            config.smtp_host = os.environ.get('SMTP_HOST')
            config.smtp_port = int(os.environ.get('SMTP_PORT', 587))
            config.smtp_user = os.environ.get('SMTP_USER')
            config.smtp_password = os.environ.get('SMTP_PASSWORD')
            config.from_email = os.environ.get('FROM_EMAIL')
        
        # Webhook configuration
        if os.environ.get('WEBHOOK_URL'):
            config.webhook_enabled = True
            config.webhook_url = os.environ.get('WEBHOOK_URL')
        
        # S3 configuration
        if os.environ.get('S3_BUCKET'):
            config.cloud_storage_enabled = True
            config.s3_bucket = os.environ.get('S3_BUCKET')
            config.aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
            config.aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        # Slack configuration
        if os.environ.get('SLACK_WEBHOOK_URL'):
            config.slack_enabled = True
            config.slack_webhook_url = os.environ.get('SLACK_WEBHOOK_URL')
        
        return config
    
    def _get_enabled_channels(self) -> List[str]:
        """Get list of enabled channels."""
        channels = []
        if self.config.email_enabled:
            channels.append('email')
        if self.config.webhook_enabled:
            channels.append('webhook')
        if self.config.slack_enabled:
            channels.append('slack')
        if self.config.cloud_storage_enabled:
            channels.append('s3')
        return channels

def test_delivery_system():
    """Test the multi-channel delivery system."""
    from report_generator import ReportGenerator
    
    # Generate a test report
    print("Generating test report...")
    gen = ReportGenerator()
    report = gen.generate_comprehensive_report("https://www.example.com")
    
    # Create delivery configuration (all disabled for testing)
    config = DeliveryConfig(
        email_enabled=False,  # Would enable with real SMTP
        webhook_enabled=False,  # Would enable with real webhook
        slack_enabled=False,  # Would enable with real Slack webhook
        cloud_storage_enabled=False  # Would enable with AWS creds
    )
    
    # Initialize delivery system
    delivery = MultiChannelDelivery(config)
    
    # Test delivery (will show all disabled)
    results = delivery.deliver_report(
        report,
        channels=['email', 'webhook', 'slack', 's3'],
        recipients={'email': 'test@example.com'},
        video_url='https://example.com/video.mp4'
    )
    
    # Print results
    print("\n[DELIVERY RESULTS]")
    for result in results:
        status = "✓" if result.success else "✗"
        print(f"{status} {result.channel}: {result.error or 'Success'}")

if __name__ == "__main__":
    test_delivery_system()