"""
Groq AI Client for content rewriting and explanation
AI is used ONLY for:
- Rewriting content examples
- Explaining recommendations in natural language
- Converting technical findings to user-friendly text

AI is NOT used for:
- Scoring
- Deciding correctness
- Making ranking claims
"""
from typing import Dict, List, Optional
from groq import Groq
import config


class GroqClient:
    """Handles all interactions with Groq API"""
    
    def __init__(self):
        if not config.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set. AI features will be disabled.")
        
        self.client = Groq(api_key=config.GROQ_API_KEY)
        self.model = config.GROQ_MODEL
    
    def generate_content_rewrite(self, original_content: str, issue_type: str, recommendations: List[str]) -> Optional[str]:
        """
        Generate a rewritten version of content based on identified issues
        
        Args:
            original_content: The original content block to rewrite
            issue_type: Type of issue (e.g., "too long", "lacks clarity", "no direct answer")
            recommendations: List of specific improvements to make
        
        Returns:
            Rewritten content or None if AI fails
        """
        try:
            recommendations_text = "\n".join(f"- {rec}" for rec in recommendations)
            
            prompt = f"""You are a content optimization expert. Rewrite the following content to fix specific issues.

ORIGINAL CONTENT:
{original_content[:1000]}  

ISSUES TO FIX:
{recommendations_text}

REQUIREMENTS:
- Keep the rewrite concise (40-80 words for answers)
- Start with a direct answer if it's a question
- Remove fluff and filler phrases
- Use clear, simple language
- Make it easy for AI to extract
- Maintain factual accuracy

OUTPUT ONLY THE REWRITTEN CONTENT, nothing else."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,  # Low temperature for consistency
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"AI rewrite failed: {e}")
            return None
    
    def explain_recommendations(self, recommendations: List[Dict], score: float, score_type: str) -> Optional[str]:
        """
        Generate user-friendly explanation of recommendations
        
        Args:
            recommendations: List of recommendation dicts with issue and fix
            score: The overall score (0-100)
            score_type: "SEO" or "AEO"
        
        Returns:
            Natural language explanation or None if AI fails
        """
        try:
            # Take top 3 recommendations
            top_recs = recommendations[:3]
            recs_text = "\n".join(
                f"{i+1}. {rec['name']}: {rec['issue']}"
                for i, rec in enumerate(top_recs)
            )
            
            prompt = f"""You are an SEO/AEO expert explaining analysis results to a business owner.

SCORE: {score}/100 ({score_type})

TOP ISSUES:
{recs_text}

Write a 2-3 sentence explanation that:
- Is honest and direct (no sugar-coating)
- Explains WHY these issues matter for {score_type}
- Focuses on impact, not technical jargon
- Doesn't promise rankings or guarantees

Write in second person ("Your content..."). Be helpful but realistic."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            print(f"AI explanation failed: {e}")
            return None
    
    def generate_faq_suggestions(self, content: Dict, missing_questions: List[str]) -> Optional[List[Dict]]:
        """
        Generate FAQ suggestions based on content topic
        
        Args:
            content: Extracted content dict with title, paragraphs, etc.
            missing_questions: Types of questions not answered (e.g., "what", "how", "why")
        
        Returns:
            List of suggested FAQ pairs or None if AI fails
        """
        try:
            title = content.get('title', '')
            first_para = content.get('paragraphs', [''])[0][:500]
            
            prompt = f"""Based on this content, suggest 3 FAQ questions that should be answered for better AEO.

PAGE TITLE: {title}

CONTENT PREVIEW:
{first_para}

MISSING QUESTION TYPES: {', '.join(missing_questions)}

Generate 3 specific questions that:
- Users would actually search for
- Are directly relevant to this page
- Include the missing question types
- Are answerable in 40-80 words

Format:
Q: [question]
A: [suggested answer based on context]

Be specific to this topic, not generic."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=400
            )
            
            # Parse response into FAQ pairs
            response_text = response.choices[0].message.content.strip()
            faqs = []
            
            lines = response_text.split('\n')
            current_q = None
            current_a = None
            
            for line in lines:
                line = line.strip()
                if line.startswith('Q:'):
                    if current_q and current_a:
                        faqs.append({'question': current_q, 'answer': current_a})
                    current_q = line[2:].strip()
                    current_a = None
                elif line.startswith('A:'):
                    current_a = line[2:].strip()
            
            # Add last pair
            if current_q and current_a:
                faqs.append({'question': current_q, 'answer': current_a})
            
            return faqs if faqs else None
        
        except Exception as e:
            print(f"AI FAQ generation failed: {e}")
            return None
    
    def generate_before_after_example(self, content: Dict, top_issue: Dict) -> Optional[Dict]:
        """
        Generate a before/after content example based on top issue
        
        Args:
            content: Extracted content
            top_issue: The highest priority issue to demonstrate
        
        Returns:
            Dict with 'before', 'after', and 'explanation' or None
        """
        try:
            # Find suitable content to use as "before"
            paragraphs = content.get('paragraphs', [])
            headings = content.get('headings', {})
            
            # Use first substantial paragraph as example
            before_text = paragraphs[0] if paragraphs else content.get('title', 'No content available')
            
            # Get first heading for context
            h1 = headings.get('h1', [''])[0] if headings.get('h1') else ''
            h2 = headings.get('h2', [''])[0] if headings.get('h2') else ''
            context_heading = h1 or h2 or 'Content Section'
            
            prompt = f"""Create a before/after content example demonstrating this improvement:

ISSUE: {top_issue['name']}
PROBLEM: {top_issue['issue']}
FIX: {top_issue['fix']}

CONTEXT: This is from a section about "{context_heading}"

BEFORE (current content):
{before_text[:400]}

Create:
1. A cleaned "AFTER" version (40-80 words if it's an answer, similar length otherwise)
2. A brief explanation of what changed and why it's better

Format:
AFTER:
[improved content]

WHAT CHANGED:
[2 sentence explanation]"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=400
            )
            
            response_text = response.choices[0].message.content.strip()
            
            # Parse response
            after_start = response_text.find('AFTER:')
            changed_start = response_text.find('WHAT CHANGED:')
            
            if after_start >= 0 and changed_start >= 0:
                after_text = response_text[after_start + 6:changed_start].strip()
                explanation = response_text[changed_start + 13:].strip()
                
                return {
                    'before': before_text[:300],
                    'after': after_text,
                    'explanation': explanation,
                    'issue_fixed': top_issue['name']
                }
            
            return None
        
        except Exception as e:
            print(f"AI example generation failed: {e}")
            return None
