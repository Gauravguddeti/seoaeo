# Local Test Website Guide

## Quick Start

### 1. Start the Test Server

In one terminal, run:
```powershell
python test_server.py
```

This will start a local server on port 8080 serving two test HTML pages.

### 2. Start the Analyzer

In another terminal, run:
```powershell
python main.py
```

This starts the analyzer on port 8000.

### 3. Test the Analyzer

Open your browser to: `http://localhost:8000`

Then analyze these local test URLs:

#### **Good Example** (Should score 75-85+)
```
http://localhost:8080/test_site_good.html
```

**What's good about it:**
- ✅ Proper title length (30-60 chars)
- ✅ Meta description present (120-160 chars)
- ✅ Single H1 heading
- ✅ Question-based headings (What, Why, How)
- ✅ Direct answers after questions
- ✅ Lists and structured content
- ✅ FAQ section with Q&A format
- ✅ Table for comparisons
- ✅ Good content length (800+ words)
- ✅ Internal and external links

**Expected Scores:**
- SEO: 80-90
- AEO: 75-85

---

#### **Poor Example** (Should score 40-60)
```
http://localhost:8080/test_site_poor.html
```

**What's wrong with it:**
- ❌ No meta description
- ❌ Title too short
- ❌ Multiple H1 headings
- ❌ Poor heading hierarchy (H2 then H4)
- ❌ No question-based headings
- ❌ Long, rambling paragraphs
- ❌ Lots of fluff ("in today's world", "it goes without saying")
- ❌ No direct answers
- ❌ No lists or structured content
- ❌ Vague, generic content

**Expected Scores:**
- SEO: 45-55
- AEO: 35-45

---

## What to Look For

### In the Good Example:
- Clear, question-based headings
- Direct answers immediately following questions
- Short, focused paragraphs (40-80 words)
- Lists and tables for easy scanning
- FAQ section with concise Q&A pairs
- No fluff or filler phrases

### In the Poor Example:
- Multiple H1s (bad for SEO)
- Broken heading hierarchy
- Generic, vague content
- Lots of fluff phrases detected
- Long, unfocused paragraphs
- No structure or organization
- Missing SEO basics (meta description)

---

## Testing Tips

1. **Compare the scores**: See how the good vs poor example differs
2. **Read the recommendations**: Check what specific issues are identified
3. **Review the before/after example**: AI should generate improved content
4. **Check the action checklist**: See prioritized fixes

---

## Troubleshooting

**Server won't start on port 8080?**
```powershell
# Change the port in test_server.py or kill existing process
netstat -ano | findstr :8080
taskkill /PID <process_id> /F
```

**Can't access localhost:8080?**
- Make sure test_server.py is running
- Try http://127.0.0.1:8080 instead

**Analyzer won't process local URLs?**
- The validator blocks localhost for security
- You can temporarily comment out the `_is_private_url` check in utils.py for testing
- Or upload test files to a real server

---

## Next Steps

1. Test both examples to see the difference
2. Modify test_site_poor.html to improve it
3. Re-analyze and see if scores improve
4. Create your own test HTML to practice

The test files show clear examples of what works and what doesn't!
