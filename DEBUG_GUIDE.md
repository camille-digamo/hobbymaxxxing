# YouTube Hobby Maxxxer - Debugging Guide

## YouTube Search Debugging

If the bot says "No videos found" but you can find videos manually on YouTube, use this debugging tool:

### Quick Test Command
```bash
python3 debug_youtube_search.py "your topic here"
```

### Examples
```bash
# Test basic search
python3 debug_youtube_search.py "beginner kayaking"

# Test with parent topic
python3 debug_youtube_search.py "food history" "cooking"

# Test specific topic that's failing
python3 debug_youtube_search.py "guitar techniques" "music"
```

### What the Debug Tool Shows
- ✅ API key status
- 📝 Search parameters (topic, parent topic, final query)
- 📊 Number of results found
- 📺 Detailed video information (title, channel, URL, description)
- ❌ Error details if search fails

### Common Issues and Solutions

#### ✅ Debug Tool Finds Videos BUT Bot Says "No Videos Found"
**Likely Causes:**
1. **Rate limiting** - Too many API calls hitting limits
2. **Filtering issues** - All videos marked as "watched" 
3. **Parent topic mismatch** - Bot using different search query
4. **Exception handling** - Errors being caught and hidden

**Solutions:**
- Check Railway logs for actual error messages
- Wait a few minutes if rate limited
- Verify topic exists in Google Sheets with correct parent topic
- Use debug tool to test exact search query the bot would use

#### ❌ Debug Tool Also Fails
**Likely Causes:**
1. **Invalid API key** - YouTube API key not working
2. **Quota exceeded** - Daily API limit reached
3. **Network issues** - Connection problems
4. **API service disruption** - YouTube API temporarily down

**Solutions:**
- Verify `YOUTUBE_API_KEY` in `.env` file
- Check [YouTube API Console](https://console.developers.google.com/) for quota usage
- Try again later if quota exceeded
- Test basic internet connectivity

### Debug Workflow for "No Videos Found" Issues

1. **Test the exact search term:**
   ```bash
   python3 debug_youtube_search.py "beginner kayaking"
   ```

2. **If debug tool finds videos but bot doesn't:**
   - Check if topic exists in your Google Sheets
   - Look for rate limiting errors in logs
   - Verify the bot is using the same search parameters

3. **Check your Google Sheets:**
   - Does the topic exist in your topics sheet?
   - What parent topic is assigned to it?
   - Are all videos for this topic marked as watched?

4. **Test with parent topic:**
   ```bash
   python3 debug_youtube_search.py "beginner kayaking" "water sports"
   ```

### Advanced Debugging

#### Check Watched Videos Filter
If YouTube search works but all videos are filtered out:
```python
# Test locally
from src.sheets_service import get_watched_videos
watched = get_watched_videos()
print(f"Total watched videos: {len(watched)}")
```

#### Check Rate Limiting
Look for these patterns in logs:
- `🔑 Using Google service account JSON content` (multiple times rapidly)
- `❌ Error reading feedback history: APIError: [429]`  
- `quota exceeded for quota metric 'Read requests'`

#### Verify Topic Data
```python
# Check what parent topic a topic has
from src.sheets_service import get_google_sheets_client
# ... check topics worksheet for parent_topic column
```

## Common Error Patterns

### Pattern 1: Rate Limiting Storm
```
🔑 Using Google service account JSON content
❌ Error reading feedback history: APIError: [429]
🔑 Using Google service account JSON content  
❌ Error reading videos from Google Sheets: APIError: [429]
```
**Solution:** Wait 5-10 minutes, we added retry logic but sometimes need manual pause.

### Pattern 2: Search Works But No Available Videos
```
🔍 Searching YouTube for: 'beginner kayaking'...
✅ Found 8 video results
⏭️ Skipping already watched video: [title]
⏭️ Skipping already watched video: [title]
❌ No available videos after filtering
```
**Solution:** Topic has all videos marked as watched, suggest related topics.

### Pattern 3: Hidden Exceptions
```
❌ No videos found for 'topic'
❌ There was an error finding a video
```
**Solution:** Check logs for actual exception details, recent fix shows real errors.

## Getting Help

If debugging doesn't solve the issue:
1. Run the debug tool and share the output
2. Check Railway logs for error details  
3. Verify the exact topic name and parent topic in Google Sheets
4. Test the same search manually on YouTube.com to confirm videos exist