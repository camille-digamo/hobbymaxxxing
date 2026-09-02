# YouTube Hobby Maxxxer Discord Bot

A personal Discord bot that learns your interests and automatically delivers tailored YouTube video recommendations using AI.

## What It Does

🎯 **Smart Recommendations**: Uses AI (Claude) to find YouTube videos matching your evolving interests and current skill level

📊 **Learning System**: Tracks your feedback on recommended videos to improve future suggestions and discover new topics

⚡ **On-Demand Requests**: Ask for videos anytime with natural language like "can you recommend me something" or "surprise me"

📅 **Daily Automation**: Automatically posts a curated video recommendation every day at 9:17 AM EDT

🗂️ **Topic Management**: Intelligently manages 80+ hobby topics, rotating through interests and expanding into new areas based on your feedback

## Architecture

### Current Implementation: Monolithic (Recommended)

**Decision**: After testing both architectures, the monolithic approach proved superior for this use case.

**Why Monolithic Won:**
- ✅ **Reliable deployment** - Works perfectly on Railway
- ✅ **All features preserved** - Manual requests, reflection questions, scheduling  
- ✅ **Simple debugging** - Everything in one file, easy to trace
- ✅ **Cost effective** - Deploys without complexity

**Event-Driven Attempt:**
- ❌ Railway import failures: `"name 'build' is not defined"`
- ❌ Complex deployment debugging
- ❌ Added complexity without clear benefit at personal bot scale

**Key Insight**: Scale matters. Event-driven makes sense for 100+ users, multiple services, or large teams. For a personal hobby bot, monolithic is the right choice.

## Deployment Architecture

### Current Setup: Two-Service Railway

**Service 1: Persistent Listener**
- **Command**: `python main.py --railway-listener`
- **Purpose**: Handle Discord reactions, manual requests, topic exploration
- **Always running**: Responds to user interactions
- **Cost**: ~$2-3/month

**Service 2: Daily Video Cron** 
- **Command**: `python main.py --github-daily-job`
- **Purpose**: Post video recommendations, then exit
- **Schedule**: Every 15 minutes (testing) / Daily at 9:17 AM EDT (production)
- **Cost**: ~$0-1/month (only runs briefly)

### Alternative Deployment Options

**Local Setup** (FREE):
```bash
# Daily cron job
0 17 13 * * * cd /path/to/hobbymaxxxing && python main.py --daily-job

# Persistent listener  
python main.py --railway-listener
```

**GitHub Actions + Railway Hybrid** ($0-3/month):
- GitHub Actions: Free daily job execution
- Railway: Minimal listener service

## Key Files

### Core Implementation
- **`main.py`** (111KB) - Complete monolithic bot implementation
- **`requirements.txt`** - Python dependencies
- **`.env`** - Environment variables (not committed)

### Deployment Configuration  
- **`railway.json`** - Listener service configuration
- **`railway-cron.json`** - Daily video cron service configuration
- **`.github/workflows/daily-hobby.yml`** - GitHub Actions (disabled, backup)

### Authentication & Config
- **`auth/hobbymaxxxing-service-account.json`** - Google Sheets service account
- **`config/`** - Configuration files
- **`.env.example`** - Environment variable template

### Documentation
- **`docs/api-setup/`** - API setup guides (YouTube, Discord, Anthropic, Google Sheets)
- **`docs/deployment/`** - Deployment guides for different platforms
- **`docs/algorithm/`** - Algorithm documentation (topic selection, feedback learning)

## Environment Variables

Required for all deployments:

```bash
# YouTube Data API
YOUTUBE_API_KEY=your_youtube_api_key

# Discord Bot
DISCORD_BOT_TOKEN=your_discord_bot_token  
DISCORD_CHANNEL_ID=your_channel_id
DISCORD_USER_ID=your_user_id

# Anthropic Claude API
ANTHROPIC_API_KEY=your_anthropic_api_key

# Google Sheets API
GOOGLE_SHEETS_ID=your_google_sheets_id
GOOGLE_SERVICE_ACCOUNT_FILE=./auth/hobbymaxxxing-service-account.json
GOOGLE_SERVICE_ACCOUNT_JSON='{...service_account_json_content...}'
```

## Bot Commands & Modes

### Command Line Arguments
```bash
# Single run (local testing)
python main.py

# Daily job (posts video, exits)
python main.py --daily-job

# Persistent listener (handles reactions)  
python main.py --railway-listener

# GitHub Actions mode (cloud daily job)
python main.py --github-daily-job
```

### Discord Interactions

**Manual Video Requests:**
- "can you recommend me something"
- "send me a video"  
- "i need something to watch"
- "surprise me"

**Feedback System:**
- React with ✅ (good video)
- React with ❌ (bad video)
- Bot asks follow-up questions for learning

**Topic Management:**
- Bot automatically rotates through 80+ topics
- Expands into new areas based on feedback
- Handles topic exhaustion gracefully

## Development Workflow

### Local Testing
```bash
# Test daily job
python main.py --daily-job

# Test listener mode
python main.py --railway-listener

# Debug YouTube search
python debug_youtube_search.py
```

### Deployment Process
```bash
# 1. Test locally
python main.py --daily-job

# 2. Commit changes
git add .
git commit -m "Description of changes"
git push

# 3. Railway auto-deploys both services
# 4. Monitor logs in Railway dashboard
```

## Key Algorithms

### Topic Selection Algorithm
1. **Load existing topics** from Google Sheets
2. **Filter by criteria**: interest level, days since last video, available videos
3. **Prioritize**: high interest + long time since last video  
4. **Expand topics** when exhausted using Claude AI
5. **Balance exploration vs exploitation**

### Video Recommendation System  
1. **Search YouTube** with targeted queries (topic + skill level + quality filters)
2. **AI Analysis**: Claude evaluates video relevance, quality, and educational value
3. **Personalization**: Incorporate user feedback history and preferences
4. **Deduplication**: Avoid already watched or pending videos
5. **Quality Filtering**: Prefer channels with good educational content

### Feedback Learning
1. **Capture reactions** (✅/❌) and detailed notes
2. **Store in Google Sheets** with video metadata  
3. **Pattern analysis** to understand preferences
4. **Topic scoring** adjustment based on feedback
5. **Channel quality** tracking for future recommendations

## Cost Analysis

### Current Two-Service Railway
- **Listener Service**: $2-3/month (always running)
- **Cron Service**: $0-1/month (brief executions)  
- **Total**: ~$3-4/month

### Alternatives
- **Local Setup**: $0/month (Raspberry Pi ~$35 one-time)
- **GitHub Actions + Minimal Railway**: $0-2/month
- **Full Railway Single Service**: $5/month

## Troubleshooting

### Common Issues

**Cron Not Running:**
- Check Railway dashboard for cron job registration
- Verify environment variables are set
- Use off-peak minutes (avoid :00) for GitHub Actions
- Consider Railway's two-service approach for reliability

**Import Errors on Railway:**
- Keep monolithic structure (avoid modular imports)
- Verify all dependencies in requirements.txt
- Check for typos in environment variables

**YouTube API Rate Limits:**  
- API key properly configured
- Not exceeding 10,000 units/day quota
- Implement backoff on rate limit errors

**Discord Connection Issues:**
- Bot token valid and has proper permissions
- Channel ID and User ID correct
- Bot added to Discord server with message permissions

### Debug Tools
```bash
# Check YouTube search  
python debug_youtube_search.py

# Validate environment
python main.py --daily-job  # Should show validation errors

# Test individual components
python -c "from main import search_youtube; print(search_youtube('guitar', 'music'))"
```

## Performance & Monitoring

### Key Metrics
- **Video recommendation accuracy** (tracked via feedback)
- **Topic coverage balance** (ensure all interests get attention)  
- **API usage** (stay within quotas)
- **Bot uptime** (Railway service health)

### Monitoring
- **Railway Dashboard**: Service health, logs, resource usage
- **Google Sheets**: Feedback trends, topic performance  
- **Discord**: User engagement, reaction patterns

## Future Considerations

### When to Consider Event-Driven
- **Multiple Discord servers** (10+ servers)
- **Many concurrent users** (100+ users)
- **Complex multi-step workflows** across services
- **Large development team** (5+ developers)

### Potential Enhancements
- **Additional integrations**: Spotify music, book recommendations
- **Advanced ML**: Better personalization algorithms  
- **Multi-user support**: Scale to friend groups
- **Analytics dashboard**: Web interface for feedback analysis

## Contributing

This is a personal project, but the architecture and patterns can be adapted for:
- **Educational purposes**: Learning Discord bot development
- **Similar hobby bots**: Book recommendations, music discovery, etc.  
- **Multi-user deployments**: Friend groups or communities

## License & Usage

Personal project - feel free to adapt the patterns and architecture for your own hobby automation needs!