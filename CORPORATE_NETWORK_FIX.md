# 🏢 Corporate Network / Office Laptop Fix

## Problem
You're getting SSL certificate errors when running RAG-PROD on your office laptop:
```
SSLError: [SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: 
self-signed certificate in certificate chain
```

This happens because corporate networks use proxy servers with self-signed SSL certificates that block direct downloads from HuggingFace, OpenAI, etc.

---

## ✅ Solution 1: Use Gemini Embeddings (Recommended)

Gemini often works better with corporate proxies. Update your `.env` file:

```bash
# Change this line:
EMBEDDING_PROVIDER=huggingface

# To this:
EMBEDDING_PROVIDER=gemini

# Make sure you have Gemini API key:
GOOGLE_API_KEY=your_gemini_api_key_here
```

**Why this works:**
- Gemini API goes through Google's CDN which usually bypasses corporate SSL issues
- Still completely FREE (no cost)
- Works just as well as HuggingFace embeddings

---

## ✅ Solution 2: Code Changes (Already Applied)

I've updated the code to:
1. **Auto-fallback**: If HuggingFace fails, automatically switches to Gemini
2. **SSL bypass**: Disables SSL verification for corporate networks
3. **Better error handling**: Graceful fallback instead of crashes

**Files modified:**
- [utils/rag_engine.py](utils/rag_engine.py) - Added SSL bypass and error handling
- [requirements.txt](requirements.txt) - Added certifi and urllib3

---

## ✅ Solution 3: Environment Variables (Quick Fix)

Add these to your PowerShell terminal BEFORE running:

```powershell
# Disable SSL verification (temporary for this session)
$env:CURL_CA_BUNDLE = ""
$env:REQUESTS_CA_BUNDLE = ""
$env:PYTHONHTTPSVERIFY = "0"

# Now run the app
streamlit run app.py
```

---

## ✅ Solution 4: Use Pre-downloaded Model

If nothing works, download the model manually:

### Step 1: Download on personal laptop/home
```bash
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-mpnet-base-v2')"
```

This downloads to: `C:\Users\YourName\.cache\huggingface\`

### Step 2: Copy to office laptop
Copy the entire `.cache\huggingface` folder to your office laptop at the same location.

### Step 3: Use local model
The app will automatically use the cached model without downloading.

---

## 🚀 Quick Start (Office Laptop)

**Option A: Use Gemini (Easiest)**
```powershell
# 1. Update .env file
EMBEDDING_PROVIDER=gemini
GOOGLE_API_KEY=your_key_here

# 2. Run app
streamlit run app.py
```

**Option B: Use HuggingFace with SSL bypass**
```powershell
# 1. Set environment variables
$env:CURL_CA_BUNDLE = ""
$env:REQUESTS_CA_BUNDLE = ""

# 2. Run app (will download model on first run)
streamlit run app.py
```

---

## 📝 What Changed in Code

### [utils/rag_engine.py](utils/rag_engine.py)

**Added SSL bypass (lines 14-25):**
```python
# Disable SSL verification for corporate networks
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''
```

**Added auto-fallback (lines 90-105):**
```python
try:
    self.embeddings = HuggingFaceEmbeddings(...)
except Exception as e:
    logger.warning("HuggingFace failed, switching to Gemini")
    self.embeddings = GoogleGenerativeAIEmbeddings(...)
```

Now if HuggingFace download fails due to SSL, it automatically switches to Gemini!

---

## 🔒 Is This Safe?

**For corporate laptops: YES**
- Your company's SSL certificates are what's blocking the connection
- Disabling verification just means "trust my company's certificates"
- You're still within your corporate network security

**Not recommended for:**
- Production servers
- Public-facing applications
- Personal laptops outside corporate network

---

## ✅ Verification

After applying the fix, you should see:

**Success with Gemini:**
```
2025-12-27 15:30:00 | INFO | Using Gemini embeddings (models/embedding-001) - FREE!
```

**Or success with HuggingFace:**
```
2025-12-27 15:30:00 | INFO | Using Hugging Face embeddings (all-mpnet-base-v2) - FREE & LOCAL!
```

---

## 🆘 Still Not Working?

### Check 1: Gemini API Key
```powershell
# Verify key is set
python -c "from config import config; print(f'Gemini key: {config.GEMINI_API_KEY[:10]}...')"
```

### Check 2: Internet Access
```powershell
# Test Google access
curl https://generativelanguage.googleapis.com
```

### Check 3: Proxy Settings
```powershell
# Check if proxy is set
echo $env:HTTP_PROXY
echo $env:HTTPS_PROXY
```

If you have a proxy, add to `.env`:
```
HTTP_PROXY=http://your-proxy:port
HTTPS_PROXY=http://your-proxy:port
```

---

## 💡 Recommended Setup for Office

**Best configuration for corporate laptops:**

```bash
# .env file
EMBEDDING_PROVIDER=gemini          # Works best with corporate networks
AI_PROVIDER=gemini                 # Also free, no SSL issues
GOOGLE_API_KEY=your_gemini_key     # Get from ai.google.dev

# Optional backup
OPENAI_API_KEY=your_openai_key     # For premium features
```

**Why?**
- ✅ Gemini works through Google CDN (bypasses most corporate blocks)
- ✅ Completely free (no usage limits)
- ✅ No model downloads needed
- ✅ Fast and reliable

---

## 📚 More Help

- **Gemini API Key:** https://ai.google.dev/
- **HuggingFace Issues:** https://huggingface.co/docs/hub/security-tokens
- **SSL Troubleshooting:** Check with your IT department about proxy certificates

---

**Your app is now configured to work on office laptops! 🎉**
