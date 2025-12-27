# 🔄 Dynamic AI Provider Switching - User Guide

## ✨ New Feature: Switch Between Gemini & OpenAI

You can now **switch AI providers on-the-fly** using a dropdown in the sidebar!

---

## 🎯 How to Use

### Step 1: Open the Sidebar
Look for the **🤖 AI Provider** section at the top of the sidebar.

### Step 2: Select Your Provider
Choose from the dropdown:
- **🌟 Gemini (Free)** - Google's free AI, unlimited usage
- **🚀 OpenAI (Premium)** - GPT-4 quality, pay-per-use

### Step 3: Start Chatting!
The system automatically:
- ✅ Switches **both LLM and Embeddings** to your choice
- ✅ Updates immediately (no restart needed)
- ✅ Shows you current models and costs

---

## 📊 What Changes When You Switch?

### When You Select **Gemini**:
```
📊 LLM: gemini-2.0-flash-exp
🧮 Embeddings: models/embedding-001  
💰 Cost: $0/month
```

**Benefits:**
- ✅ Completely FREE
- ✅ Unlimited queries
- ✅ Works better on corporate networks
- ✅ Fast responses
- ✅ Good for everyday use

---

### When You Select **OpenAI**:
```
📊 LLM: gpt-4
🧮 Embeddings: text-embedding-3-small
💰 Pay-per-use
```

**Benefits:**
- ✅ GPT-4 quality
- ✅ Better at complex reasoning
- ✅ More accurate embeddings
- ✅ Premium features
- ⚠️ Costs money per query

---

## 🔧 Technical Details

### What Happens Behind the Scenes?

When you change the dropdown:

1. **Session State Updated**: Your choice is saved in `st.session_state.ai_provider`

2. **RAG Engine Switches**:
   ```python
   # Automatically called in app.py
   rag_engine.update_provider(selected_provider)
   ```

3. **Both Components Change**:
   - **LLM Model**: For generating answers
   - **Embeddings Model**: For searching documents

4. **Immediate Effect**: Next query uses new provider!

---

## 💡 Use Cases

### Use Gemini When:
- 📚 Reading/searching documents
- ❓ Simple Q&A
- 📊 Data analysis
- 🆓 You want zero cost
- 🏢 On office laptop (corporate network)

### Use OpenAI When:
- 🧠 Complex reasoning needed
- 📝 Creative writing
- 🔬 Technical analysis
- 💎 Premium quality required
- 💰 Budget allows

---

## ⚡ Quick Switching Tips

### 1. **No Restart Needed**
Just select from dropdown → system updates instantly!

### 2. **Per-Query Basis**
You can switch for **every single query** if you want:
- Use Gemini for simple searches
- Switch to OpenAI for complex analysis
- Switch back to Gemini to save money

### 3. **Test Both**
Ask the same question to both providers and compare:
1. Ask with Gemini → see answer
2. Switch to OpenAI → ask again
3. Compare quality vs cost

---

## 🎨 UI Indicators

### Current Provider Display:
```
🤖 AI Provider
┌─────────────────────────┐
│ 🌟 Gemini (Free)       │ ← Selected
│ 🚀 OpenAI (Premium)     │
└─────────────────────────┘

📊 LLM: gemini-2.0-flash-exp
🧮 Embeddings: models/embedding-001
💰 Cost: $0/month
```

### When Switching:
```
✅ Switched to Gemini
🔄 Both LLM and Embeddings updated!
```

---

## 🔒 API Key Requirements

### For Gemini:
- ✅ Already set in `.env`: `GEMINI_API_KEY`
- ✅ Free from https://ai.google.dev/

### For OpenAI:
- ✅ Already set in `.env`: `OPENAI_API_KEY`  
- 💳 Requires payment setup
- Get from https://platform.openai.com/

---

## 🐛 Troubleshooting

### Provider Switch Fails?

**Check 1**: Verify API keys in `.env`
```bash
GEMINI_API_KEY=AIza...  # For Gemini
OPENAI_API_KEY=sk-...   # For OpenAI
```

**Check 2**: Check terminal logs
```
INFO | ✅ Switched to Gemini: LLM=gemini-2.0-flash-exp, Embeddings=models/embedding-001
```

**Check 3**: If OpenAI fails, you'll auto-fallback to Gemini
```
ERROR | Error switching provider: OpenAI API key not set
WARNING | Falling back to Gemini
```

---

## 📈 Cost Comparison

| Feature | Gemini (Free) | OpenAI (Paid) |
|---------|---------------|---------------|
| **LLM** | gemini-2.0-flash-exp | gpt-4 |
| **Embeddings** | models/embedding-001 | text-embedding-3-small |
| **Cost per 1M tokens** | $0.00 | ~$10.00 |
| **Monthly Limit** | Unlimited | Pay-as-you-go |
| **Best For** | Most queries | Complex tasks |
| **Quality** | Very Good ⭐⭐⭐⭐ | Excellent ⭐⭐⭐⭐⭐ |

---

## 🚀 Advanced: Programmatic Switching

### In Code:
```python
# app.py automatically handles this
selected_provider = st.session_state.get('ai_provider', 'gemini')

if selected_provider != rag_engine.current_ai_provider:
    rag_engine.update_provider(selected_provider)
```

### Manual Testing:
```python
# Test both providers
rag_engine.update_provider('gemini')
response1 = rag_engine.query(user_id, "What is this document about?")

rag_engine.update_provider('openai')
response2 = rag_engine.query(user_id, "What is this document about?")

# Compare responses
print(f"Gemini: {response1[0][:100]}")
print(f"OpenAI: {response2[0][:100]}")
```

---

## 💰 Cost Optimization Strategy

### Recommended Approach:

1. **Default to Gemini (Free)**
   - Use for 90% of queries
   - Perfect for most tasks
   - Zero cost

2. **Switch to OpenAI When Needed**
   - Complex reasoning
   - Critical accuracy needed
   - Creative tasks

3. **Switch Back to Gemini**
   - After complex query
   - Resume free usage

### Example Workflow:
```
1. Regular search → Gemini (Free)
2. Regular search → Gemini (Free)
3. Complex analysis → Switch to OpenAI (Premium)
4. Regular search → Switch back to Gemini (Free)
```

**Savings:** ~95% cost reduction vs always using OpenAI!

---

## 🎉 Summary

**You now have:**
- ✅ One-click provider switching
- ✅ Both LLM and Embeddings change together
- ✅ Real-time updates (no restart)
- ✅ Cost visibility
- ✅ Model information display
- ✅ Automatic fallback on errors

**Result:** Maximum flexibility + cost control! 🎯

---

## 📚 Related Files

- **Sidebar UI**: [components/sidebar.py](components/sidebar.py#L21-L58)
- **Provider Switching**: [utils/rag_engine.py](utils/rag_engine.py#L165-L218)
- **Query Logic**: [app.py](app.py#L345-L358)

---

**Enjoy your flexible AI-powered document chat! 🚀**
