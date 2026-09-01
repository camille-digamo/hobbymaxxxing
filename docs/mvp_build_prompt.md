# YouTube Hobby Maxxxer — MVP Build Prompt

Paste this whole thing into Claude Code as your first message in the project folder.

---

I'm building a Discord bot that recommends YouTube videos based on my interests. This is the **first milestone only** — a minimal end-to-end script, not the full system. Please build **only** what's described below and stop there. Do not add a hobby tree, Google Sheets logging, note-taking/accountability prompts, scheduling, or any multi-step agent/tool-use loop — those come in later phases and I'll ask for them separately.

## What to build

A single Python script that does the following, in order, when run once from the command line:

1. Use a **hard-coded topic string** at the top of the script (e.g. `TOPIC = "hand sewing techniques"`) — no dynamic topic selection yet.
2. Call the **YouTube Data API v3** `search.list` endpoint with that topic as the query. Retrieve the top 5–8 results (title, description, channel title, video ID, thumbnail URL).
3. Send those candidates to the **Claude API** (Anthropic Python SDK) in a single prompt. Ask Claude to pick the single best video for someone starting to learn about the topic, and write a short (2–3 sentence) engaging blurb explaining why it's worth watching. Have Claude return its answer as JSON (video ID + blurb) so it's trivial to parse — don't make me regex the response.
4. Format a **Discord embed** (title, link to `https://www.youtube.com/watch?v={video_id}`, thumbnail image, description = Claude's blurb) and **POST it to a Discord webhook URL**.

## Tech requirements

- Python 3.11+
- Libraries: `anthropic`, `google-api-python-client`, `requests`, `python-dotenv`
- Load all credentials from a `.env` file (never hard-code secrets), using these exact variable names:
  - `YOUTUBE_API_KEY`
  - `ANTHROPIC_API_KEY`
  - `DISCORD_WEBHOOK_URL`
- Create a `.gitignore` that excludes `.env`
- Create a `requirements.txt`
- Use the **Claude Haiku 4.5** model for this step — it's cheap and more than capable of picking a video and writing a blurb; no need for a larger model here.

## File structure

Keep this to **one file** (`main.py`) plus `.env.example`, `.gitignore`, and `requirements.txt`. Don't split into modules yet — that's premature for a script this small and just adds friction while I'm still testing the core loop.

## Acceptance criteria

Running `python main.py` once, with no manual steps beyond having the `.env` filled in, should: search YouTube for the hard-coded topic, get Claude's pick + blurb, and post one formatted message to my Discord channel. Print a short status line at each stage (searching, got N results, Claude picked X, posting to Discord, done) so I can see where it is if something breaks.

## Explicitly out of scope — do not build these yet

- Hobby tree / branching topic logic
- Google Sheets or Docs integration
- Note-taking / accountability prompts
- Scheduling (cron, GitHub Actions, etc.)
- Multi-topic rotation
- Tool-use / agentic decision loop — a plain sequential script is correct for this step
