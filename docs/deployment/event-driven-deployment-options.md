# Event-Driven Bot Deployment Options

## Overview

This document outlines low-cost deployment strategies for the event-driven YouTube Hobby Maxxxer, focusing on cost optimization while maintaining the benefits of the new architecture.

---

## 🤔 Lambda Reality Check

**❌ Why AWS Lambda isn't ideal for Discord bots:**

- **Persistent connections required**: Discord bots need WebSocket connections that stay alive
- **15-minute execution limit**: Your bot needs to listen 24/7 for reactions  
- **Cold starts**: Would cause delays in Discord responses
- **State management**: Lambda is stateless, but your bot tracks user sessions

**✅ Lambda could work for specific components** in a hybrid approach (scheduled tasks, API processing).

---

## 💰 Deployment Options (Ranked by Cost)

### **1. GitHub Actions + Railway Hybrid** - **$0-3/month** ⭐ **CHEAPEST**

**Current setup enhanced for event-driven:**

```
┌─────────────────────┐    ┌──────────────────────┐
│   GitHub Actions    │───▶│     Railway App      │
│   (FREE)           │    │   ($0-3/month)       │
│                     │    │                      │
│ • Daily job trigger │    │ • Event bus          │
│ • Topic selection   │    │ • Discord listener   │
│ • Video search      │    │ • Session manager    │
│ • Claude recommendation│  │ • Reaction handling  │
│ • Post to Discord   │    │ • Notes collection   │
└─────────────────────┘    └──────────────────────┘
```

**Benefits:**
- Already working in your current setup
- **FREE** daily video recommendations via GitHub Actions
- **Railway free tier** covers persistent listener
- Event-driven architecture reduces Railway resource usage

**Setup:**
```yaml
# .github/workflows/daily-hobby-events.yml
name: Daily Hobby Video (Event-Driven)
on:
  schedule:
    - cron: '0 14 * * *'  # 2 PM UTC
jobs:
  daily-video:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: python3 event_driven/main.py --daily-job
        env:
          YOUTUBE_API_KEY: ${{ secrets.YOUTUBE_API_KEY }}
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          DISCORD_BOT_TOKEN: ${{ secrets.DISCORD_BOT_TOKEN }}
          DISCORD_CHANNEL_ID: ${{ secrets.DISCORD_CHANNEL_ID }}
          DISCORD_USER_ID: ${{ secrets.DISCORD_USER_ID }}
          GOOGLE_SHEETS_ID: ${{ secrets.GOOGLE_SHEETS_ID }}
          GOOGLE_SERVICE_ACCOUNT_JSON: ${{ secrets.GOOGLE_SERVICE_ACCOUNT_JSON }}
```

```json
// config/railway.json (Updated for event-driven)
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python3 event_driven/main.py --railway-listener",
    "restartPolicyType": "ON_FAILURE", 
    "restartPolicyMaxRetries": 3
  }
}
```

---

### **2. Fly.io** - **$0-5/month** ⭐ **DEVELOPER-FRIENDLY**

**Perfect for Discord bots with event-driven architecture:**

**Setup Files:**

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy event-driven code
COPY event_driven/ ./event_driven/
COPY auth/ ./auth/
COPY .env .

# Health check endpoint
EXPOSE 8080

# Run event-driven listener
CMD ["python3", "event_driven/main.py", "--listen", "--health-port", "8080"]
```

```toml
# fly.toml
app = "hobby-maxxxer"
primary_region = "iad"

[build]

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true

[[vm]]
  cpu_kind = "shared"
  cpus = 1
  memory_mb = 256

[processes]
  app = "python3 event_driven/main.py --listen --health-port 8080"
```

**Benefits:**
- **$0/month** for small bots (free tier: 256MB RAM)
- **Global edge locations**: Better Discord response times
- **Persistent connections**: Perfect for Discord WebSocket
- **Easy deployment**: `fly deploy`
- **Built-in metrics** and health checks

**Deployment Commands:**
```bash
# One-time setup
fly auth login
fly launch --name hobby-maxxxer --region iad

# Set environment variables
fly secrets set YOUTUBE_API_KEY="your_key"
fly secrets set ANTHROPIC_API_KEY="your_key"
fly secrets set DISCORD_BOT_TOKEN="your_token"
fly secrets set DISCORD_CHANNEL_ID="123456789"
fly secrets set DISCORD_USER_ID="987654321"
fly secrets set GOOGLE_SHEETS_ID="your_sheet_id"
fly secrets set GOOGLE_SERVICE_ACCOUNT_JSON='{"type":"service_account",...}'

# Deploy updates
fly deploy

# Monitor
fly logs
fly status
```

---

### **3. Google Cloud Run** - **$0-5/month** ⭐ **PAY-PER-USE**

**Excellent for event-driven workloads:**

```yaml
# cloud-run.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: hobby-maxxxer
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/minScale: "1"  # Keep 1 instance warm
        autoscaling.knative.dev/maxScale: "2"  # Scale up if needed
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 1
      containers:
      - image: gcr.io/your-project/hobby-bot:latest
        ports:
        - containerPort: 8080
        resources:
          limits:
            cpu: 1000m
            memory: 512Mi
        env:
        - name: PORT
          value: "8080"
```

```dockerfile
# Dockerfile for Cloud Run
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY event_driven/ ./event_driven/
COPY auth/ ./auth/
COPY .env .

# Cloud Run requires listening on PORT
EXPOSE $PORT

CMD python3 event_driven/main.py --listen --health-port $PORT
```

**Benefits:**
- **Pay-per-request** pricing
- **Automatic scaling** (including scale-to-zero)
- **Generous free tier**: 2 million requests/month
- **Global deployment** options

**Deployment:**
```bash
# Build and deploy
gcloud builds submit --tag gcr.io/your-project/hobby-bot
gcloud run deploy hobby-maxxxer --image gcr.io/your-project/hobby-bot --platform managed --region us-central1 --min-instances 1
```

---

### **4. Full Serverless Architecture** - **$2-10/month**

**Split event-driven components across serverless functions:**

```
┌─────────────────┐   ┌─────────────────┐   ┌─────────────────┐
│  CloudWatch     │──▶│  Lambda Daily   │──▶│   SQS Queue     │
│  (Scheduler)    │   │  Job Handler    │   │   (Events)      │
└─────────────────┘   └─────────────────┘   └─────────────────┘
                                                       │
┌─────────────────┐   ┌─────────────────┐   ┌─────────▼─────────┐
│  Discord Bot    │◀──│  Lambda Discord │◀──│  Lambda Event     │
│  (Webhook)      │   │  Handler        │   │  Processor        │
└─────────────────┘   └─────────────────┘   └───────────────────┘
```

**Component Breakdown:**

**Serverless Functions** (AWS Lambda/Vercel Functions):
- Daily recommendation trigger
- Topic analysis (Claude API calls) 
- YouTube search processing
- Individual event handlers

**Persistent Services** (Railway/Fly.io):
- Event bus coordinator
- Session state management
- Discord WebSocket listener

**Event Storage** (AWS SQS/Google Pub/Sub):
- Event queue between components
- Retry and dead letter handling

**Implementation:**
```python
# serverless/daily_job.py (AWS Lambda)
import json
import requests
from event_driven.events import DailyJobTriggered

def lambda_handler(event, context):
    # Process daily recommendation workflow
    daily_event = DailyJobTriggered(trigger_source="lambda")
    
    # Send to persistent event bus via webhook
    requests.post("https://your-railway-app.com/webhook/event", 
                 json=daily_event.to_dict())
    
    return {'statusCode': 200, 'body': 'Daily job triggered'}

# persistent/event_coordinator.py (Railway)
from fastapi import FastAPI
from event_driven.core.event_bus import get_event_bus

app = FastAPI()
event_bus = get_event_bus()

@app.post("/webhook/event")
async def handle_serverless_event(event_data: dict):
    # Receive events from serverless functions
    # Process through event bus
    await event_bus.publish_from_dict(event_data)
    return {"status": "processed"}
```

---

## 🎯 Recommended Migration Strategy

### **Phase 1: Enhanced Hybrid** (Current - $0-3/month)
Keep your GitHub Actions + Railway setup, but upgrade it for event-driven:

```bash
# Update Railway to use event-driven system
railway up
railway env set START_COMMAND="python3 event_driven/main.py --railway-listener"
```

### **Phase 2: Fly.io Migration** ($0-5/month)
If you want better performance and global edge deployment:

```bash
# Migrate to Fly.io
fly launch
fly secrets import < .env
fly deploy
```

### **Phase 3: Serverless Hybrid** ($2-10/month)
Only if scaling to 100+ users or need extreme cost optimization:
- Move heavy processing to Lambda
- Keep Discord listener on persistent service
- Use event queues for coordination

---

## 💰 Cost Comparison

| Option | Monthly Cost | Best For | Setup Complexity |
|--------|-------------|----------|------------------|
| **GitHub Actions + Railway** | $0-3 | Current users, gradual migration | Low (already working) |
| **Fly.io** | $0-5 | Better performance, global reach | Medium |
| **Google Cloud Run** | $0-5 | Pay-per-use, automatic scaling | Medium |
| **Full Serverless** | $2-10 | High scale, extreme optimization | High |

---

## 🚀 Quick Start Commands

### **Enhance Current Setup (Event-Driven)**
```bash
# Test event-driven system locally
python3 test_event_system.py

# Update Railway deployment
railway login
railway link
railway env set START_COMMAND="python3 event_driven/main.py --railway-listener"
railway up
```

### **Try Fly.io**
```bash
fly auth login
fly launch --name hobby-maxxxer
fly secrets import < .env
fly deploy
fly status
```

### **Try Google Cloud Run**
```bash
gcloud auth login
gcloud builds submit --tag gcr.io/your-project/hobby-bot
gcloud run deploy --image gcr.io/your-project/hobby-bot --min-instances 1
```

---

## 🔧 Configuration for Event-Driven Architecture

### **Environment Variables (All Platforms)**
```env
# API Keys (existing)
YOUTUBE_API_KEY=your_youtube_key
ANTHROPIC_API_KEY=your_anthropic_key
DISCORD_BOT_TOKEN=your_discord_token
DISCORD_CHANNEL_ID=123456789
DISCORD_USER_ID=987654321
GOOGLE_SHEETS_ID=your_sheet_id
GOOGLE_SERVICE_ACCOUNT_JSON={"type":"service_account",...}

# Event-Driven Specific
EVENT_BUS_MODE=async  # async, sync, hybrid
SESSION_TIMEOUT_HOURS=24
CLEANUP_INTERVAL_MINUTES=30
HEALTH_CHECK_PORT=8080

# Platform Specific
DEPLOYMENT_PLATFORM=railway  # railway, fly, cloudrun, lambda
```

### **Health Check Endpoint** (Required for most platforms)
```python
# Add to event_driven/main.py
from fastapi import FastAPI
import uvicorn

health_app = FastAPI()

@health_app.get("/health")
async def health_check():
    stats = event_bus.get_stats()
    return {
        "status": "healthy" if stats["running"] else "unhealthy",
        "uptime": time.time() - start_time,
        "events_processed": stats["events_processed"],
        "active_sessions": len(session_manager.sessions)
    }

# Run health server alongside event system
if __name__ == "__main__":
    if "--health-port" in sys.argv:
        port = int(sys.argv[sys.argv.index("--health-port") + 1])
        uvicorn.run(health_app, host="0.0.0.0", port=port)
```

---

## 📊 Performance Considerations

### **Resource Requirements**
- **RAM**: 128-512MB (event-driven uses less memory than monolithic)
- **CPU**: 0.25-1 vCPU (async processing is CPU-efficient)  
- **Storage**: Minimal (session state is temporary)
- **Network**: Low bandwidth, persistent connections

### **Scaling Characteristics**
- **Horizontal**: Event bus scales with more handler instances
- **Vertical**: Session manager benefits from more RAM
- **Geographic**: Discord WebSocket benefits from edge deployment

### **Monitoring**
All platforms should monitor:
- Event processing latency
- Session creation/cleanup rates  
- Discord WebSocket connection health
- API rate limit usage

---

**Recommendation: Start with your current GitHub Actions + Railway hybrid enhanced for event-driven architecture. It's the lowest cost and lowest risk migration path.**