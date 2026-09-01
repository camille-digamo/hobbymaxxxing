# 🎯 YouTube Hobby Maxxxer

An AI-powered Discord bot that intelligently recommends YouTube videos to accelerate your hobby learning journey!

## ✨ What It Does

🔍 **Smart Topic Analysis** - Analyzes your interests and learning patterns  
🎯 **Personalized Recommendations** - Claude AI picks videos tailored to your current focus  
📤 **Discord Integration** - Posts recommendations with interactive feedback buttons  
📊 **Learning Tracking** - Records your progress and feedback in Google Sheets  
🧠 **Adaptive Intelligence** - Learns from your reactions to improve future suggestions  
💭 **Natural Conversations** - Discovers new interests from your casual Discord messages  

## 🚀 Quick Start

### 1. Set Up Your APIs (15-20 minutes)

Follow these step-by-step guides to get your API keys:

- 📺 **[YouTube Data API Setup](docs/api-setup/youtube-api-setup.md)** - Free video search access
- 📊 **[Google Sheets API Setup](docs/api-setup/google-sheets-setup.md)** - Track your progress  
- 🤖 **[Discord Bot Setup](docs/api-setup/discord-bot-setup.md)** - Create your bot
- 🧠 **[Anthropic API Setup](docs/api-setup/anthropic-api-setup.md)** - AI recommendations (~$1-3/month)

### 2. Choose Your Deployment

Pick the option that best fits your technical comfort and budget:

| Option | Cost | Best For | Setup Time |
|--------|------|----------|------------|
| **[💻 Local](docs/deployment/local-setup.md)** | FREE | Tech-savvy users | 20 min |
| **[🏠 Raspberry Pi](docs/deployment/raspberry-pi-setup.md)** | ~$35 one-time | Makers & tinkerers | 30 min |
| **[☁️ GitHub + Railway](docs/deployment/github-actions-railway.md)** | $0-3/month | Non-technical friends | 15 min |

### 3. Test Your Setup

```bash
# Test your configuration
python main.py --help

# Get your first video recommendation
python main.py --daily-job

# Start persistent listening (Ctrl+C to stop)  
python main.py --listen
```

## 🎮 How to Use

### Daily Video Flow
1. Bot analyzes your learning patterns from Google Sheets
2. Finds YouTube videos on topics you're interested in
3. Claude AI picks the best one with personalized reasoning
4. Posts to Discord with 👍 👎 ❤️ 😴 reaction buttons

### Give Feedback
- **👍 Liked** - Good video, similar content welcome
- **❤️ Loved** - Amazing video, more like this please!
- **👎 Didn't Like** - Not helpful, avoid similar content
- **😴 Boring** - Uninteresting, try different angles

### Add Your Notes
- React to any video and the bot will ask what you learned
- Your insights get saved to help with future recommendations

### Explore New Topics
- Chat naturally: "I'm interested in woodworking"
- Bot suggests related topics and asks for confirmation
- Builds a smart topic tree based on your interests

## 🛠️ Deployment Modes

### For Scheduled Daily Videos:
```bash
python main.py --daily-job        # Local cron job
python main.py --github-daily-job # GitHub Actions (cloud)
```

### For Persistent Listening:
```bash  
python main.py --listen           # Local background service
python main.py --railway-listener # Railway cloud service
```

### For Testing:
```bash
python main.py                    # Single run: post video, wait for feedback, exit
```

## 📊 Google Sheets Structure

[Hobbymaxxxing Google Sheet Template](https://docs.google.com/spreadsheets/d/1arO0ihNWmN5gjsuWUScJUransPPNTnEnjT5f20FWd9c/edit?gid=398636454#gid=398636454)

The bot tracks your progress in two sheets:

**Topics Sheet:**
- `topic` - Specific interest (e.g., "JavaScript arrays")
- `parent_topic` - Broader category (e.g., "Programming")  
- `last_watched` - When you last got a video on this topic
- `videos_watched` - Total videos watched
- `interest_score` - How much you engage with this topic

**Videos Sheet:**
- `video_title` - Title of recommended video
- `channel` - YouTube channel name
- `video_url` - Direct link to video
- `topic` - What topic this covers
- `date_recommended` - When bot suggested it
- `date_watched` - When you gave feedback
- `rating` - Your reaction (liked, loved, etc.)
- `notes` - What you learned/found interesting

## 🧠 Smart Features

### Intelligent Topic Selection
- Prioritizes topics you haven't explored recently (15x boost)
- Balances between focused learning and topic diversity
- Avoids repeating the same topic too frequently

### Duplicate Prevention  
- Never recommends the same video twice
- Tracks by URL to handle title changes
- Maintains clean learning history

### Organic Interest Detection
- Recognizes natural expressions: "I'm interested in...", "I've been curious about..."
- Suggests related topics based on your existing interests
- Builds connections between different hobby areas

### Graceful Workflow Management
- Automatically stops after collecting your feedback
- Handles topic exhaustion by suggesting new areas
- Manages timeouts and error recovery

## 🔧 Advanced Configuration

### Environment Variables (.env file)
```env
# Required APIs
YOUTUBE_API_KEY=your_youtube_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key  
DISCORD_BOT_TOKEN=your_discord_bot_token

# Discord Configuration
DISCORD_CHANNEL_ID=123456789012345678
DISCORD_USER_ID=987654321098765432

# Google Sheets
GOOGLE_SHEETS_ID=your_spreadsheet_id
GOOGLE_SERVICE_ACCOUNT_FILE=auth/your-service-account.json

# Optional
DEBUG=true  # Enable detailed logging
```

### Algorithm Tuning
The bot uses sophisticated algorithms for topic selection and video filtering. See:
- [📈 Topic Selection Algorithm](docs/algorithm/topic-selection-algorithm.md)
- [🎯 Feedback System](docs/algorithm/feedback-system.md)  
- [🌱 Organic Topic Detection](docs/algorithm/organic-topic-detection.md)

## ❌ Troubleshooting

Having issues? Check our comprehensive troubleshooting guide:
- **[🔍 Common Issues & Solutions](docs/troubleshooting/common-issues.md)**

Quick diagnostics:
- Run the API test scripts in the troubleshooting guide
- Check that all API keys are properly set
- Verify Discord bot permissions
- Ensure Google Sheets is shared with service account

## 💰 Cost Breakdown

### Free Tier (Local Deployment):
- YouTube API: FREE (10,000 requests/day)
- Google Sheets API: FREE
- Discord API: FREE
- **Total: $0/month** ✨

### Paid Services:
- **Anthropic API**: ~$1-3/month (very efficient usage)
- **Railway Hosting**: ~$0-5/month (optional cloud deployment)
- **Total: $1-8/month** for full cloud setup

### One-Time Costs:
- **Raspberry Pi Setup**: ~$35-75 (optional dedicated device)

## 🤝 Sharing with Friends

Want to help friends set up their own Hobby Maxxxer? We've got you covered:

1. **Tech-savvy friends**: Share the [Local Setup Guide](docs/deployment/local-setup.md)
2. **Less technical friends**: Walk them through [GitHub + Railway Setup](docs/deployment/github-actions-railway.md)  
3. **Non-technical friends**: Help them with the one-click Railway deployment

Each friend needs their own API keys, but setup takes 15-30 minutes with our guides.

## 🛣️ Roadmap

Future enhancements we're considering:
- 📱 Mobile app integration
- 🎵 Spotify integration for hobby-related music
- 📚 Book recommendations alongside videos
- 👥 Community features for sharing discoveries
- 📈 Advanced analytics dashboard
- 🎮 Gamification with learning streaks

## 📄 License

MIT License - feel free to modify and share!

---

**Ready to supercharge your hobby learning?** Start with the [API Setup Guides](docs/api-setup/) and you'll be getting personalized video recommendations in 20 minutes! 🚀