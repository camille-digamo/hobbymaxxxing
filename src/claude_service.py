"""
Anthropic Claude AI integration for video recommendations and topic analysis
"""

from anthropic import Anthropic
from typing import List, Dict, Any
import json
import re
from .utils import ANTHROPIC_API_KEY


def get_claude_recommendation(videos: List[Dict[str, Any]], topic: str, feedback_history: Dict[str, Any]) -> Dict[str, str]:
    """Ask Claude to pick the best video and write a blurb."""
    print("🤖 Asking Claude to pick the best video...")

    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)

        # Build video list for Claude
        video_list = ""
        for i, video in enumerate(videos, 1):
            video_list += f"{i}. \"{video['title']}\" by {video['channel_title']}\n   Description: {video['description'][:150]}...\n\n"

        # Build feedback context
        feedback_context = ""
        if feedback_history['total_feedback'] > 0:
            liked_channels = feedback_history.get('liked_channels', [])
            disliked_channels = feedback_history.get('disliked_channels', [])

            if liked_channels:
                feedback_context += f"You tend to enjoy videos from: {', '.join(liked_channels[:5])}\n"
            if disliked_channels:
                feedback_context += f"You tend to dislike videos from: {', '.join(disliked_channels[:3])}\n"

        prompt = f"""You are helping someone learn about {topic}. Here are {len(videos)} YouTube videos to choose from:

{video_list}

{feedback_context}

Pick the single best video for learning {topic} and explain why in an enthusiastic, personal way. Focus on what makes this video valuable for someone interested in {topic}.

Your response must be valid JSON only, no other text:
{{
    "video_id": "the_youtube_video_id",
    "blurb": "2-3 sentence explanation of why this video is perfect for learning {topic}"
}}

Make the blurb personal and exciting, using language typical of people who enjoy {topic} if the slang fits. Emphasize how the video can get them where they want to be in an aspirational and motivational way.
Avoid generic phrases like "this video is great" or "you should watch this". Instead, focus on the unique value of the video and how it can help the viewer achieve their goals in {topic}.

Your response must be valid JSON only, no other text."""

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",  # Claude Haiku 4.5
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse Claude's JSON response
        response_text = response.content[0].text.strip()

        # Extract JSON from markdown code blocks if present
        if response_text.startswith('```json'):
            # Find the JSON content between ```json and ```
            start_marker = '```json'
            end_marker = '```'

            start_index = response_text.find(start_marker) + len(start_marker)
            end_index = response_text.find(end_marker, start_index)

            if end_index != -1:
                response_text = response_text[start_index:end_index].strip()

        try:
            recommendation = json.loads(response_text)
            print(f"✅ Claude picked video ID: {recommendation['video_id']}")
            return recommendation
        except json.JSONDecodeError:
            print(f"❌ Error parsing Claude's response as JSON: {response_text}")
            # Fallback to first video
            fallback = {
                "video_id": videos[0]["video_id"],
                "blurb": f"A great video to help you learn more about {topic}!"
            }
            return fallback

    except Exception as e:
        print(f"❌ Error getting Claude recommendation: {e}")
        # Fallback to first video
        fallback = {
            "video_id": videos[0]["video_id"] if videos else "unknown",
            "blurb": f"An interesting video about {topic} to check out!"
        }
        return fallback


def analyze_topic_interest(raw_topic: str, existing_topics: List[str]) -> Dict[str, Any]:
    """Use Claude to analyze and expand topic interest."""
    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)

        existing_topics_text = "\n".join([f"- {topic}" for topic in existing_topics[:20]])

        prompt = f"""A user expressed interest in: "{raw_topic}"

Their existing interests include:
{existing_topics_text}

Please analyze this interest and provide suggestions. Consider:
- Is the topic specific enough for video recommendations?
- What parent category does this belong to?
- What related subtopics might they enjoy?
- How does it connect to their existing interests?

Respond with JSON only:
{{
  "is_specific": true/false,
  "suggested_parent": "category name",
  "specific_subtopics": ["topic 1", "topic 2", "topic 3"],
  "intersection_topics": ["topic that combines with existing interests"],
  "beginner_friendly": ["beginner version 1", "beginner version 2"]
}}

Focus on practical, learnable topics that would have good YouTube content."""

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=400,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = response.content[0].text.strip()

        # Extract JSON if in code block
        if '```json' in response_text:
            start = response_text.find('```json') + 7
            end = response_text.find('```', start)
            response_text = response_text[start:end].strip()

        return json.loads(response_text)

    except Exception as e:
        print(f"❌ Error analyzing topic interest: {e}")
        return {
            "is_specific": True,
            "suggested_parent": "general",
            "specific_subtopics": [raw_topic],
            "intersection_topics": [],
            "beginner_friendly": [f"beginner {raw_topic}"]
        }


def generate_topic_expansion(original_topic: str, parent_topic: str) -> List[str]:
    """Generate topic expansion suggestions using Claude."""
    try:
        client = Anthropic(api_key=ANTHROPIC_API_KEY)

        prompt = f"""The user wants to explore "{original_topic}" under the category "{parent_topic}".

Generate 8 specific, learnable topics they could explore. Make them:
- Specific enough for YouTube video searches
- Progressive from beginner to advanced
- Practical and actionable
- Different approaches/angles of the main topic

Return a simple numbered list:
1. [topic name]
2. [topic name]
etc.

No explanations, just the numbered list."""

        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=200,
            messages=[{"role": "user", "content": prompt}]
        )

        # Parse the response to extract topics
        response_text = response.content[0].text.strip()
        topics = []

        for line in response_text.split('\n'):
            line = line.strip()
            # Match numbered list items
            match = re.match(r'^\d+\.\s*(.+)', line)
            if match:
                topic = match.group(1).strip()
                if topic:
                    topics.append(topic)

        return topics[:8]  # Limit to 8 topics

    except Exception as e:
        print(f"❌ Error generating topic expansion: {e}")
        return [original_topic]  # Fallback to original topic