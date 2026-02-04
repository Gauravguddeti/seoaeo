# Test Websites for SEO + AEO Analyzer

## Good for Testing Different Scenarios

### 1. **Wikipedia Articles** (Good SEO, Weak AEO)
```
https://en.wikipedia.org/wiki/Search_engine_optimization
```
**What to expect:**
- ✅ Good SEO: Proper titles, headings, content length
- ❌ Weak AEO: Long paragraphs, no direct answers, excessive detail
- Good for demonstrating the difference between SEO and AEO

### 2. **How-To Guides / Tutorials** (Strong AEO potential)
```
https://www.wikihow.com/Create-a-Website
```
**What to expect:**
- ✅ Good structure with steps
- ✅ Question-based headings
- ✅ Lists and numbered steps (AI-friendly)

### 3. **FAQ Pages** (Excellent AEO)
```
https://support.google.com/
```
**What to expect:**
- ✅ Direct question/answer format
- ✅ Concise answers
- ✅ High AEO score

### 4. **Tech Documentation** (Mixed Results)
```
https://docs.python.org/3/tutorial/
```
**What to expect:**
- ✅ Good heading hierarchy
- ⚠️ Technical language (may affect readability)
- ✅ Code examples and structured content

### 5. **Blog Posts** (Variable Quality)
```
https://www.smashingmagazine.com/articles/
```
**What to expect:**
- Variable SEO/AEO depending on article
- Good for testing content with images and formatting

### 6. **News Articles** (Weak AEO typically)
```
https://www.bbc.com/news
```
**What to expect:**
- ⚠️ Often lacks question headings
- ⚠️ No direct answers
- ✅ Usually good SEO basics

### 7. **E-commerce Product Pages** (Mixed)
```
https://www.amazon.com/
```
**What to expect:**
- ⚠️ May have minimal text content
- ✅ Usually structured data
- Variable results

### 8. **Landing Pages / Marketing Sites** (Often Weak SEO)
```
https://stripe.com/
```
**What to expect:**
- ⚠️ Often light on content
- ⚠️ Marketing fluff detected
- ✅ Good structure typically

## Recommended Testing Strategy

### Start with these simple, reliable tests:

1. **Test #1: Good Example**
   ```
   https://developer.mozilla.org/en-US/docs/Web/HTML
   ```
   - Should get decent scores (70-85 range)
   - Good technical content structure

2. **Test #2: FAQ Format**
   ```
   https://wordpress.org/support/article/faq/
   ```
   - Should score high on AEO (80+)
   - Direct Q&A format

3. **Test #3: Blog Post**
   ```
   https://css-tricks.com/
   ```
   - Variable but generally good SEO
   - Pick an article with how-to content

## Test Your Own Sites

The best test is **your own website**! Try:
- Your company homepage
- Blog posts
- Product pages
- Help/FAQ sections

Compare the scores and see which pages need improvement.

## What to Look For

### SEO Analysis Will Check:
- Title and meta description
- H1 count and heading hierarchy
- Content length (300+ words ideal)
- Internal and external links
- Readability and structure

### AEO Analysis Will Check:
- Question-style headings
- Direct, concise answers (40-80 words)
- Definition clarity in first sentence
- Lists, steps, tables (structured content)
- Fluff and unnecessary language

## Testing Tips

1. **Start simple**: Test a Wikipedia page first to see how it works
2. **Compare similar pages**: Test 2-3 competitor sites in your niche
3. **Test your own content**: Most valuable insights come from your own pages
4. **Focus on blog posts**: Usually the easiest to improve
5. **Avoid**: Login pages, checkout pages, very dynamic content

## Expected Analysis Time
- Simple pages: 10-15 seconds
- Complex pages: 15-20 seconds
- If it times out: Try a simpler page on that domain

## Troubleshooting

If a site fails to analyze:
- **JavaScript-heavy sites**: May not render properly (we use static HTML)
- **Blocked bots**: Some sites block automated access
- **Slow sites**: May timeout
- **Redirects**: Should work but may cause delays

Try the homepage first, then move to content pages.
