# Anthropic API Setup Guide

## Step 1: Create an Anthropic Account

1. **Visit Anthropic Console**: Go to [console.anthropic.com](https://console.anthropic.com)
2. **Sign Up**: Create an account with your email
3. **Verify Email**: Check your email and click the verification link

## Step 2: Add Payment Method (Required)

**⚠️ Important**: Anthropic requires a payment method even for the free tier

1. **Go to Billing**: In the console, click "Billing" in the left sidebar
2. **Add Payment Method**: Add a credit/debit card
3. **Free Credits**: New accounts get $5 in free credits to start
   - This is enough for ~1,000-2,000 video recommendations
   - After free credits, costs are very low (~$0.01-0.03 per recommendation)

## Step 3: Create an API Key

1. **Navigate to API Keys**: Click "API Keys" in the left sidebar
2. **Create Key**:
   - Click "+ Create Key"
   - Name: `Hobby Maxxxer Bot`
   - Click "Create Key"
3. **Copy Your API Key**:
   - **IMPORTANT**: Copy the key immediately - you won't see it again!
   - Example: `sk-ant-api03-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7A8B9C0D1E2F3G4H5I6J7K8L9M0N`

## Step 4: Choose Your Model

The bot is configured to use **Claude 3.5 Sonnet** by default, which provides the best balance of:
- **Quality**: Excellent video recommendations and topic analysis
- **Speed**: Fast response times (~2-5 seconds)  
- **Cost**: Very affordable (~$0.01-0.03 per recommendation)

## Step 5: Monitor Usage

1. **Check Usage**: Go to "Usage" in the console to monitor your API calls
2. **Set Limits** (Optional): Set monthly spending limits to control costs
   - Recommended: $10/month limit (allows ~300-1,000 recommendations)

## Step 6: Add to Your Environment

Add to your `.env` file:
```env
ANTHROPIC_API_KEY=sk-ant-api03-1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t1u2v3w4x5y6z7A8B9C0D1E2F3G4H5I6J7K8L9M0N
```

## Cost Breakdown

**Typical Monthly Costs** (after free credits):
- **Light usage** (1 video/day): ~$0.30-0.90/month
- **Regular usage** (1-3 videos/day): ~$0.90-2.70/month  
- **Heavy usage** (5+ videos/day): ~$4.50-9.00/month

**What uses API calls**:
- Video recommendations: 1 call per recommendation
- Topic analysis: 1 call per new topic exploration
- Smart topic expansion: 1-2 calls per topic expansion

## Troubleshooting

**❌ "Invalid API key" error**:
- Double-check you copied the entire key (they're very long)
- Make sure there are no extra spaces before/after the key
- Regenerate a new key if needed

**❌ "Usage limit exceeded" error**:
- Check your billing dashboard for current usage
- Add more credits or increase your spending limit
- Free credits may be exhausted (check billing page)

**❌ "Payment method required" error**:
- You must add a payment method even for free tier usage
- Use any valid credit/debit card - you won't be charged until free credits run out

**❌ "Rate limit exceeded" error**:
- Wait a few minutes and try again
- The bot has built-in rate limiting to prevent this

**Need help?** Check the [troubleshooting guide](../troubleshooting/common-issues.md) for more solutions.