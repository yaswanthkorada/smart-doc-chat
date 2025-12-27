# 🚨 Gemini API Quota Issue - Solution Guide

## Problem
Your Gemini API has **ZERO quota** (limit: 0), meaning:
- ❌ You've exceeded the free tier daily limit (1500 embeddings/day)
- ❌ Both chat and embeddings are blocked
- ⏳ You need to wait 24 hours OR upgrade to paid plan

## Why Embeddings Still Use Gemini When You Switch to OpenAI

### The Root Cause:
When you upload a PDF, it creates **embeddings** and stores them in ChromaDB. The vector store is persistent and tied to the embedding model used when it was created.

**What happens:**
1. You upload PDF with Gemini → Creates ChromaDB with Gemini embeddings
2. You switch dropdown to OpenAI → Changes the LLM but vector store still exists
3. You try to query → It tries to use OpenAI embeddings on Gemini-created vectors = **MISMATCH ERROR**

## ✅ Solutions

### Solution 1: Delete Existing Vector Store (Quick Fix)
Delete the ChromaDB folder to force recreation with new embeddings:

```powershell
# Stop the app first
# Then delete the chroma data
Remove-Item -Recurse -Force "data\chroma_data\user_1"
```

Then restart the app and re-upload your documents.

### Solution 2: Use OpenAI Only (Recommended)
Change the default provider to OpenAI in `.env`:

```bash
AI_PROVIDER=openai
EMBEDDING_PROVIDER=openai
```

This ensures you start with OpenAI from the beginning.

### Solution 3: Wait for Gemini Quota Reset
Gemini free tier resets every 24 hours. Check your quota at:
👉 https://ai.dev/usage?tab=rate-limit

## 🔧 How to Fix Your Current Gemini API

### Option A: Check Your Current Quota
1. Go to: https://aistudio.google.com/apikey
2. Click on your API key
3. Check "Quota & Limits" section
4. See when it resets (usually 24 hours)

### Option B: Create a New Gemini API Key
If your current key is blocked or has issues:

1. **Go to Google AI Studio:**
   - Visit: https://aistudio.google.com/
   - Sign in with your Google account

2. **Create New API Key:**
   - Click "Get API Key" (top right)
   - Click "Create API Key"
   - Choose "Create API key in new project" OR select existing project
   - Copy the new API key

3. **Update Your .env File:**
   ```bash
   GEMINI_API_KEY=your_new_api_key_here
   ```

4. **Restart the app**

### Option C: Use OpenAI Instead (Costs Money)
If you have OpenAI credits:

1. Get OpenAI API key from: https://platform.openai.com/api-keys
2. Update `.env`:
   ```bash
   OPENAI_API_KEY=your_openai_key_here
   AI_PROVIDER=openai
   EMBEDDING_PROVIDER=openai
   ```
3. Delete old vector store:
   ```powershell
   Remove-Item -Recurse -Force "data\chroma_data\user_1"
   ```
4. Restart and re-upload documents

## 📊 Gemini Free Tier Limits

| Feature | Free Tier Limit |
|---------|----------------|
| Chat Requests | 15 requests/minute, 1500/day |
| Embeddings | 100 requests/minute, 1500/day |
| Input Tokens | 32,000 tokens/minute |
| Output Tokens | 8,000 tokens/minute |

**Reset Time:** 24 hours from when you hit the limit

## ⚠️ Why Your Limit Shows "0"

If `limit: 0` appears, it means:
1. You've hit your **daily quota** (1500 requests)
2. Need to wait until **tomorrow** (same time)
3. OR upgrade to **paid plan** ($0.001 per 1K tokens)

## 🎯 Best Practice Going Forward

1. **Choose ONE provider** at the start (don't switch mid-project)
2. **Use OpenAI** if you need reliability (paid but stable)
3. **Use Gemini** if you're on free tier (watch your quota)
4. **Monitor your usage** regularly

## 🔍 How to Monitor Your Usage

### For Gemini:
- Dashboard: https://ai.dev/usage
- Check daily usage before hitting limits

### For OpenAI:
- Dashboard: https://platform.openai.com/usage
- Set spending limits to avoid surprises

## 📝 Quick Commands

```powershell
# Check if app is running
Get-Process -Name streamlit

# Stop the app
Stop-Process -Name streamlit -Force

# Delete vector store
Remove-Item -Recurse -Force "data\chroma_data\user_1"

# Start app again
streamlit run app.py
```

## 💡 Pro Tip
Create a **separate Google account** for testing to get another free Gemini API key with fresh quotas!
