# Feedback System Implementation

## Updated Google Sheets Structure

### 'videos' sheet columns:
```
video_title | channel | video_url | topic | parent_topic | date_recommended | date_watched | rating | notes
```

### 'topics' sheet columns:
```
topic | parent_topic | date_added | date_watched | video_title
```

## Environment Variables Needed

Add to your `.env` file:
- `DISCORD_USER_ID` - Your Discord user ID (right-click your profile → Copy User ID)

## How It Works

1. **Bot posts video recommendation** with 4 reaction buttons
2. **You react** with your feedback:
   - 👍 **Liked** - Good video, marks as watched + updates topic date_watched
   - 👎 **Didn't Like** - Records negative rating, doesn't mark as watched  
   - ❤️ **Loved** - Amazing video, marks as watched + prioritizes similar content
   - 😴 **Boring** - Records boring rating, avoids similar content in future

3. **Bot updates Google Sheets** with your rating and channel info
4. **Bot asks follow-up question** - "What's something cool you learned?" or topic-specific reflection
5. **You reply with your thoughts** - Bot captures your response for the 'notes' column
6. **Topics sheet gets updated** when you give positive feedback (liked/loved)
7. **Future recommendations improve** based on your channel and content preferences

## Interactive Learning Notes

After you rate any video, the bot will ask thoughtful follow-up questions like:
- **Guitar topics**: "What's one technique you'll practice this week?"
- **Surf topics**: "What will you try on your next surf session?"
- **Cooking topics**: "What technique do you want to try in your kitchen?"
- **Generic topics**: "What's something cool you learned that you'll take with you?"

Your response gets automatically saved to the 'notes' column in your Google Sheet!

## Enhanced Channel Learning

The system now tracks:
- **Channel names** in the videos sheet for better record keeping
- **Channel preferences** from your ratings (loved channels get prioritized)
- **Channel avoidance** (channels you find boring get deprioritized)
- **Topic completion tracking** via date_watched updates

## Feedback Learning

The system learns your preferences:
- **Channels you love** → Prioritizes those channels in future searches
- **Keywords you enjoy** → Looks for similar content patterns
- **Channels you dislike** → Avoids recommending them
- **Boring keywords** → Filters out similar title patterns

## Running the Bot

```bash
python main.py
```

The bot will:
1. Analyze your rating history for personalized recommendations
2. Find next topic from your sheets using smart selection
3. Get personalized recommendation based on loved/disliked channels
4. Post to Discord with feedback buttons
5. Stay running to collect your ratings
6. Update both videos and topics sheets automatically

**If no new videos are available** for a topic, the bot will:
7. Generate related topic suggestions using Claude
8. Ask you to select new topics to explore
9. Add your selections to the topics sheet
10. Find a video from one of the new topics

Press Ctrl+C to stop the bot.

## Topic Expansion Feature

When you've exhausted all videos for a topic, the bot will automatically suggest 5-6 related topics:

### Example Interaction:
```
🤔 No more new videos found for 'beginner guitar'!

Here are some related topics you could explore next:

1. fingerpicking techniques
2. guitar chord progressions  
3. electric guitar basics
4. guitar maintenance and setup
5. music theory for guitarists
6. acoustic vs electric guitar

How to respond:
• Type the numbers of topics you want (e.g., "1 3 5") 
• Or type topic names directly (e.g., "fingerpicking")
• You can select multiple topics - I'll add them all!

What interests you? 🎯
```

### Your Response Options:
- **Numbers**: "1 3 5" (selects items 1, 3, and 5)
- **Topic names**: "fingerpicking guitar maintenance" 
- **Custom topics**: "jazz guitar improvisation"
- **Mixed**: Works with partial matches too!

The bot will add your selections to the topics sheet and immediately find a video from one of them.

## Organic Topic Interest Detection

**New Feature!** The bot now automatically detects when you naturally express interest in topics through conversation.

### Simply chat naturally:
- **"I'm interested in photography"** 
- **"I want to learn guitar"**
- **"I'm curious about cooking"**
- **"Thinking of getting into surfing"**

### The bot will:
1. **Detect your interest** automatically
2. **Analyze the topic** using Claude AI
3. **Suggest related subtopics** and intersections with your existing interests
4. **Guide you through topic selection** with intelligent conversation
5. **Add chosen topics** to your Google Sheets
6. **Include them** in future smart recommendations

### Example Interaction:
```
You: "I'm kind of interested in photography"

Bot: 💭 I see you're interested in 'photography'!

I think this falls under visual arts. Is that right?

Here are some specific areas you could explore:

Specific Topics:
• portrait photography basics
• landscape photography techniques
• street photography
• camera settings fundamentals

You: "yes, portrait and landscape sound good"

Bot: ✅ Awesome! Added 2 topics to explore:
• portrait photography basics  
• landscape photography techniques

These will show up in your smart topic recommendations! 🚀
```

See [ORGANIC_TOPIC_DETECTION.md](ORGANIC_TOPIC_DETECTION.md) for complete documentation.

## Bot Permissions Needed

Make sure your Discord bot has:
- Send Messages
- Embed Links  
- Add Reactions
- Read Message History
- Use External Emojis
- Manage Messages (to edit embeds after feedback)