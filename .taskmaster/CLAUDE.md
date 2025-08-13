# TaskMaster Integration for VideoReach AI

## Project Context
VideoReach AI is an automated video prospecting platform following the ZAD Development Mandate and Core-First methodology.

## TaskMaster Commands

### Core Commands
```bash
# Research before implementation
task-master research "[topic]"

# Task management
task-master add-task --prompt="[task description]" --research
task-master list
task-master next
task-master show [task-id]
task-master set-status --id=[task-id] --status=[pending|in-progress|done]
task-master expand --id=[task-id] --research --force
```

### Project-Specific Workflows

#### 1. Core Function Validation (ZAD Mandate Step 1)
```bash
# Research and create core test script
task-master research "AI avatar video generation APIs HeyGen D-ID implementation"
task-master add-task --prompt="Create core_test.py for avatar video generation" --priority=critical --research
```

#### 2. API Wrapper Development (ZAD Mandate Step 2)
```bash
task-master add-task --prompt="Build minimal API wrapper for proven core function" --priority=high
```

#### 3. E2E Testing (ZAD Mandate Step 3)
```bash
task-master add-task --prompt="Implement Selenium E2E test for video generation pipeline" --priority=high
```

## Development Priorities (Following Core-First Mandate)

### PHASE 1: Core Engine Validation (MUST COMPLETE FIRST)
1. **Core Video Generation** (`core_test.py`)
   - HeyGen API integration
   - Script to video conversion
   - Hardcoded test data
   - Direct terminal output

### PHASE 2: API Exposure
2. **Minimal API Wrapper**
   - Single endpoint
   - JSON input matching test data
   - Return video URL

### PHASE 3: E2E Validation
3. **Browser Automation Test**
   - Selenium/Playwright test
   - Full pipeline validation
   - Must pass before proceeding

### PHASE 4: Full Implementation (ONLY AFTER 1-3 COMPLETE)
4. **Supporting Features**
   - Web UI
   - Database
   - Authentication
   - Advanced features

## Critical Path Components

### Research Engine Requirements
- Website scraping (Puppeteer/Playwright)
- Company enrichment (Clearbit/Apollo)
- LinkedIn data (Sales Navigator API)
- Tech stack detection (BuiltWith)

### Script Generation Requirements
- GPT-4 integration
- Template system
- Personalization variables
- 45-second max duration

### Video Pipeline Requirements
- Avatar APIs: HeyGen (primary), D-ID (backup)
- Website capture: Puppeteer
- Video assembly: FFmpeg
- Storage: S3 + CloudFront CDN

### Distribution Requirements
- SMTP integration
- Video thumbnail generation
- Tracking pixel embedding
- Landing page generation

## Task Validation Criteria

### Core Test Success Metrics
- [ ] Avatar API returns video URL
- [ ] Script converts to speech successfully
- [ ] Video duration < 60 seconds
- [ ] Cost per video < $0.50
- [ ] Generation time < 45 seconds

### E2E Test Success Metrics
- [ ] Browser can submit prospect data
- [ ] API processes request
- [ ] Video URL is returned
- [ ] Video plays successfully
- [ ] All components communicate

## Error Handling Requirements

### API Failures
- Implement provider fallback (HeyGen → D-ID → Synthesia)
- Exponential backoff retry logic
- Queue failed jobs for retry
- Alert on repeated failures

### Performance Targets
- P95 response time < 60s
- Success rate > 95%
- Concurrent video generation: 100+
- Daily volume capacity: 1000+ videos

## Development Rules (From ZAD Mandate)

1. **NO FEATURES BEFORE CORE WORKS**
   - Do not build UI before core_test.py works
   - Do not add authentication before core works
   - Do not optimize before core works

2. **REAL DATA ONLY**
   - No mock data in core_test.py
   - Must use actual API keys
   - Must generate real videos
   - Must validate actual output

3. **SEQUENTIAL VALIDATION**
   - Complete each phase before moving to next
   - Manual verification required between phases
   - E2E test is the gatekeeper to full development

## Cost Optimization Priorities

### Per-Video Cost Breakdown Target
- Avatar API: $0.15
- GPT-4 Script: $0.02
- Web Scraping: $0.03
- Storage/CDN: $0.05
- Compute: $0.05
- **Total Target: $0.30**

## Integration Points

### Required API Keys (Store in .env)
```
HEYGEN_API_KEY=
HEYGEN_AVATAR_ID=
OPENAI_API_KEY=
SCRAPERAPI_KEY=
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
SMTP_HOST=
SMTP_USER=
SMTP_PASS=
```

## Testing Checkpoints

### Before Moving to Next Phase
1. Run core_test.py successfully 10 times
2. Verify video quality manually
3. Check cost per video is under target
4. Confirm generation time < 45 seconds
5. Document any API limitations discovered

## Support Resources
- HeyGen API Docs: https://docs.heygen.com
- D-ID API Docs: https://docs.d-id.com
- GPT-4 API: https://platform.openai.com/docs
- Puppeteer: https://pptr.dev
- FFmpeg: https://ffmpeg.org/documentation.html

## Monitoring & Alerts

### Key Metrics to Track
- Video generation success rate
- Average generation time
- Cost per video
- API quota usage
- Error rates by component

### Alert Thresholds
- Generation failure rate > 5%
- Generation time > 60 seconds
- Cost per video > $0.50
- API quota < 10% remaining

---

**Remember: The Core-First Mandate is LAW. No exceptions.**