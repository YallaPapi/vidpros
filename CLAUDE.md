# CLAUDE.md - AI Video Prospecting Platform

## Project Overview
VideoReach AI is an automated video prospecting platform that generates personalized sales videos at scale using AI avatars, intelligent research, and multi-channel distribution. The system analyzes prospects' websites, generates contextual scripts highlighting automation opportunities, creates AI avatar videos with screen recordings, and distributes them through email, LinkedIn, and SMS.

## Core Value Proposition
- **Speed**: Generate 100+ personalized videos daily (vs 4-6 manual videos)
- **Scale**: Leverage 300+ existing email mailboxes for distribution  
- **Conversion**: 8-10x higher response rates than text-only outreach
- **Cost**: <$0.50 per video vs $50+ for manual creation

## Technical Architecture

### System Components
```
Frontend (Next.js) → API Gateway → Service Mesh
                                    ├── Research Service (Python)
                                    ├── Script Generator (GPT-4)
                                    ├── Video Engine (FFmpeg/HeyGen)
                                    ├── Distribution Service (Node.js)
                                    └── Analytics Service (ClickHouse)
```

### Core Technologies
- **Frontend**: Next.js 14, TypeScript, TailwindCSS, Shadcn/ui
- **Backend**: Node.js, Express, Bull Queue for job processing
- **Database**: PostgreSQL (main), Redis (queue), S3 (videos), ClickHouse (analytics)
- **AI/ML**: OpenAI GPT-4, HeyGen API, D-ID, ElevenLabs
- **Infrastructure**: AWS/Kubernetes, CloudFront CDN, Docker

## Project Structure
```
videoreach-ai/
├── apps/
│   ├── web/                 # Next.js dashboard
│   ├── api/                 # Express API gateway
│   ├── worker/              # Background job processor
│   └── analytics/           # Analytics service
├── packages/
│   ├── database/            # Prisma schemas
│   ├── ui/                  # Shared UI components
│   ├── lib/                 # Shared utilities
│   │   ├── research/        # Scraping & enrichment
│   │   ├── ai/              # AI service wrappers
│   │   ├── video/           # Video processing
│   │   └── distribution/    # Multi-channel sending
│   └── types/               # TypeScript definitions
├── infrastructure/
│   ├── docker/              # Dockerfiles
│   ├── k8s/                 # Kubernetes configs
│   └── terraform/           # Infrastructure as code
├── .taskmaster/             # Task Master config
│   ├── config.json
│   ├── tasks/
│   └── docs/
└── scripts/                 # Automation scripts
```

## Development Guidelines

### Video Generation Pipeline
```javascript
// Core pipeline flow with timing targets
async function generateVideo(prospect) {
  // 1. Research Phase (5-10s)
  const research = await scrapeWebsite(prospect.url);
  const enrichment = await enrichProspect(prospect);
  
  // 2. Script Generation (3-5s)
  const context = analyzeBusinessNeeds(research, enrichment);
  const script = await generateScript(context, template);
  
  // 3. Website Capture (5-8s)
  const screenshots = await captureWebsite(prospect.url, {
    scrollPoints: script.references,
    annotations: script.highlights
  });
  
  // 4. Avatar Recording (15-20s)
  const avatarVideo = await generateAvatar({
    script: script.text,
    voice: script.voiceId,
    avatar: user.avatarId
  });
  
  // 5. Video Assembly (8-10s)
  const finalVideo = await assembleVideo({
    avatar: avatarVideo,
    screenshots: screenshots,
    branding: user.brandAssets,
    captions: script.captions
  });
  
  // Total: 36-53 seconds target
  return finalVideo;
}
```

### Research Engine Rules
```javascript
// Critical data points to extract
const researchPriorities = {
  tier1: [
    'company_size',        // Employee count
    'tech_stack',          // Current tools
    'industry',            // Vertical/niche
    'recent_funding',      // Growth signals
    'job_postings'         // Hiring = growth pain
  ],
  tier2: [
    'competitors',         // Positioning angle
    'social_presence',     // Engagement level
    'content_topics',      // Pain points they discuss
    'leadership_changes'   // Trigger events
  ],
  tier3: [
    'website_updates',     // Recent changes
    'press_mentions',      // PR opportunities
    'customer_reviews'     // Satisfaction gaps
  ]
};
```

### Script Generation Patterns
```javascript
// Effective video script structure (45 seconds max)
const scriptTemplate = {
  hook: {
    duration: '0-5s',
    pattern: 'I noticed [SPECIFIC_DETAIL] on [COMPANY]\'s website...',
    goal: 'Prove you did research'
  },
  problem: {
    duration: '5-15s',
    pattern: 'Most [INDUSTRY] companies struggle with [PAIN_POINT]...',
    goal: 'Resonate with their challenge'
  },
  solution: {
    duration: '15-35s',
    pattern: 'We helped [SIMILAR_COMPANY] automate this, saving [METRIC]...',
    goal: 'Show tangible value'
  },
  cta: {
    duration: '35-45s',
    pattern: 'Worth a quick 15-minute call to explore? [CALENDAR_LINK]',
    goal: 'Clear next step'
  }
};
```

### Avatar & Voice Best Practices
```javascript
// Avatar configuration for authenticity
const avatarSettings = {
  professional: {
    background: 'office_blur',
    clothing: 'business_casual',
    expression: 'friendly_confident',
    gestures: 'natural_moderate'
  },
  voice: {
    pace: 140,          // Words per minute
    pitch: 1.0,         // Natural tone
    emphasis: 'moderate',
    pauses: 'natural'   // After punctuation
  },
  positioning: {
    size: '30%',        // Of frame
    location: 'bottom_right',
    opacity: 0.95
  }
};
```

## Task Master Configuration

Task Master has been initialized for this project.

- Configuration: `.taskmaster/config.json`
- Tasks DB: `.taskmaster/tasks/tasks.json`
- PRD: `.taskmaster/docs/prd.txt`

### Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines, treat as if import is in the main CLAUDE.md file.**
@./.taskmaster/CLAUDE.md

## Error Handling Cycles

### API Rate Limit Errors
```javascript
// Intelligent retry with provider fallback
async function handleAvatarGeneration(script, attempt = 1) {
  const providers = ['heygen', 'd-id', 'synthesia'];
  const provider = providers[(attempt - 1) % providers.length];
  
  try {
    return await generateWithProvider(provider, script);
  } catch (error) {
    if (error.code === 'RATE_LIMIT') {
      await delay(Math.pow(2, attempt) * 1000); // Exponential backoff
      return handleAvatarGeneration(script, attempt + 1);
    }
    throw error;
  }
}
```

### Website Scraping Failures
```javascript
// Multi-strategy scraping approach
const scrapingStrategies = [
  { method: 'puppeteer', timeout: 10000 },
  { method: 'playwright', timeout: 15000 },
  { method: 'scraperapi', timeout: 20000 },
  { method: 'cached_google', timeout: 5000 }
];

// Fallback through strategies
for (const strategy of scrapingStrategies) {
  try {
    return await scrapeWithStrategy(url, strategy);
  } catch (error) {
    console.log(`Strategy ${strategy.method} failed, trying next...`);
  }
}
```

### Video Processing Errors
- **Memory Issues**: Stream processing, chunked uploads
- **Format Errors**: Multiple output formats (MP4, WebM)
- **Quality Issues**: Automatic re-encoding with adjusted bitrate
- **Storage Failures**: Multi-region S3 with fallback to B2

## Context Management (Context7 Pattern)

### Campaign Context
```typescript
interface CampaignContext {
  id: string;
  status: 'draft' | 'processing' | 'active' | 'completed';
  prospects: {
    total: number;
    processed: number;
    successful: number;
    failed: Array<{
      prospectId: string;
      error: string;
      retryCount: number;
    }>;
  };
  videos: {
    generated: number;
    sent: number;
    viewed: number;
    engaged: number;
  };
  performance: {
    avgGenerationTime: number;
    avgViewDuration: number;
    responseRate: number;
    bookingRate: number;
  };
}
```

### Prospect Context
```typescript
interface ProspectContext {
  // Research data
  company: {
    name: string;
    website: string;
    industry: string;
    size: string;
    techStack: string[];
    fundingStage?: string;
  };
  
  // Contact info
  contact: {
    name: string;
    title: string;
    email: string;
    linkedin?: string;
    phone?: string;
  };
  
  // Personalization
  insights: {
    painPoints: string[];
    opportunities: string[];
    triggers: string[];
    competitors: string[];
  };
  
  // Generated content
  video: {
    url: string;
    thumbnail: string;
    duration: number;
    script: string;
    generatedAt: Date;
  };
  
  // Engagement tracking
  engagement: {
    sent: boolean;
    opened: boolean;
    played: boolean;
    watchTime: number;
    clicked: boolean;
    replied: boolean;
    booked: boolean;
  };
}
```

## API Integration Patterns

### HeyGen Avatar Generation
```javascript
// Optimal settings for B2B prospecting
const heygenConfig = {
  avatar_id: process.env.HEYGEN_AVATAR_ID,
  voice: {
    voice_id: process.env.HEYGEN_VOICE_ID,
    speed: 1.0,
    pitch: 0
  },
  background: {
    type: 'image',
    url: 'https://cdn/office-background.jpg'
  },
  video_settings: {
    resolution: '1080p',
    fps: 30,
    codec: 'h264'
  }
};

// Request with retry logic
async function generateHeyGenVideo(script) {
  const response = await axios.post('https://api.heygen.com/v2/video/generate', {
    script: script,
    ...heygenConfig
  }, {
    headers: {
      'X-Api-Key': process.env.HEYGEN_API_KEY
    },
    timeout: 30000
  });
  
  // Poll for completion
  return pollVideoStatus(response.data.video_id);
}
```

### GPT-4 Script Optimization
```javascript
// Few-shot prompt for consistent quality
const scriptPrompt = `
You are an expert B2B sales copywriter creating personalized video scripts.

Examples of high-converting scripts:
${exampleScripts}

Prospect Research:
${JSON.stringify(prospectData, null, 2)}

Create a 45-second video script that:
1. Opens with specific detail from their website
2. Identifies a clear automation opportunity
3. Mentions similar company success (anonymous)
4. Ends with soft CTA for 15-minute call

Script:
`;
```

## Performance Optimization

### Database Queries
```sql
-- Optimized prospect batch retrieval
WITH video_batch AS (
  SELECT p.*, 
         ROW_NUMBER() OVER (PARTITION BY p.company_domain 
                           ORDER BY p.priority DESC) as rn
  FROM prospects p
  WHERE p.status = 'pending'
    AND p.campaign_id = $1
    AND NOT EXISTS (
      SELECT 1 FROM videos v 
      WHERE v.prospect_id = p.id 
      AND v.created_at > NOW() - INTERVAL '7 days'
    )
  LIMIT 100
)
SELECT * FROM video_batch WHERE rn = 1;
```

### Video CDN Strategy
```javascript
// Multi-CDN with fallback
const cdnProviders = {
  primary: 'cloudfront',
  secondary: 'bunnycdn',
  fallback: 's3direct'
};

// Adaptive bitrate for bandwidth optimization
const videoQualities = [
  { label: '1080p', bitrate: '5000k', priority: 1 },
  { label: '720p', bitrate: '2500k', priority: 2 },
  { label: '480p', bitrate: '1000k', priority: 3 }
];
```

## Testing Strategy

### Unit Tests
```javascript
// Critical path testing
describe('Video Generation Pipeline', () => {
  test('generates script from prospect data', async () => {
    const prospect = mockProspectData();
    const script = await generateScript(prospect);
    expect(script.length).toBeLessThan(250); // ~45 seconds
    expect(script).toContain(prospect.company.name);
  });
  
  test('handles avatar API failures gracefully', async () => {
    mockHeyGenFailure();
    const video = await generateVideo(mockProspect);
    expect(video.provider).toBe('d-id'); // Fallback
  });
});
```

### Load Testing
```bash
# K6 load test for video generation
k6 run --vus 100 --duration 30m video-generation-load.js

# Expected metrics:
# - P95 response time < 60s
# - Success rate > 95%
# - No memory leaks over 30min
```

## Deployment Pipeline

### CI/CD Workflow
```yaml
# GitHub Actions deployment
name: Deploy VideoReach
on:
  push:
    branches: [main]
    
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - run: npm test
      - run: npm run test:integration
      
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - run: docker build -t videoreach:${{ github.sha }}
      - run: kubectl rollout deploy/api
      - run: npm run migrate:prod
      - run: npm run health:check
```

### Monitoring & Alerts
```javascript
// Key metrics to track
const metrics = {
  business: [
    'videos_generated_per_hour',
    'cost_per_video',
    'video_to_meeting_rate',
    'revenue_per_video'
  ],
  technical: [
    'api_response_time',
    'video_generation_duration',
    'avatar_api_success_rate',
    'storage_usage_gb'
  ],
  alerts: [
    { metric: 'error_rate', threshold: 0.05, action: 'page' },
    { metric: 'generation_time', threshold: 60, action: 'slack' },
    { metric: 'api_quota_remaining', threshold: 100, action: 'email' }
  ]
};
```

## Security Considerations

### Data Privacy
- PII encryption at rest (AES-256)
- Video URLs with signed expiration (24 hours)
- GDPR compliance with data deletion
- No storage of scraped competitor data

### API Security
```javascript
// Rate limiting per customer
const rateLimits = {
  free: { videos: 10, period: 'day' },
  starter: { videos: 100, period: 'day' },
  growth: { videos: 500, period: 'day' },
  scale: { videos: 2000, period: 'day' }
};

// API key rotation
const apiKeyRotation = {
  heygen: 'monthly',
  openai: 'quarterly',
  scraperapi: 'monthly'
};
```

## Cost Optimization

### Per-Video Cost Breakdown
```javascript
const costStructure = {
  avatar: 0.15,      // HeyGen API
  script: 0.02,      // GPT-4
  scraping: 0.03,    // ScraperAPI
  storage: 0.05,     // S3 + CDN
  compute: 0.05,     // EC2/Lambda
  total: 0.30,       // Target COGS
  price: 2.99,       // Selling price
  margin: 2.69       // 90% gross margin
};
```

### Scale Optimizations
- Bulk API discounts at 1000+ videos/month
- Reserved compute instances for 60% savings
- Cached research data for repeat companies
- Template reuse reducing GPT-4 calls by 40%

## Support & Troubleshooting

### Common Issues
1. **"Avatar generation timeout"**: Increase timeout, check API status
2. **"Script too long for avatar"**: Implement auto-summarization
3. **"Website scraping blocked"**: Rotate proxies, try alternate methods
4. **"Video quality poor"**: Check bitrate settings, CDN configuration
5. **"High bounce rates"**: Review email deliverability, video thumbnails

### Debug Mode
```bash
# Enable verbose logging
export DEBUG=videoreach:*
export LOG_LEVEL=debug

# Test single video generation
npm run test:generate -- --prospect-id=123 --verbose

# Dry run campaign
npm run campaign:dryrun -- --campaign-id=456
```

## Future Enhancements

### Phase 2 Features
- Custom avatar training ($5k/customer)
- LinkedIn native video posts
- Interactive video elements (buttons, forms)
- Real-time personalization based on behavior
- Multilingual support (Spanish, French, German)

### Phase 3 Features  
- AI SDR conversations post-video
- Slack/Teams integration
- White-label solution
- Video email signatures
- Webinar clip personalization

---

*Last Updated: August 2025*
*Version: 1.0.0*
*Maintainer: Development Team*