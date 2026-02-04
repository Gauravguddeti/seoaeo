"""
AEO (Answer Engine Optimization) Analysis Engine
Focuses on answer-readiness for AI search engines
"""
from typing import Dict, List
import re
import config


class AEOCheck:
    """Represents a single AEO check result"""
    def __init__(self, name: str, status: str, explanation: str, recommendation: str, score: float, examples: List[str] = None):
        self.name = name
        self.status = status  # "pass", "warning", "fail"
        self.explanation = explanation
        self.recommendation = recommendation
        self.score = score  # 0-100 for this check
        self.examples = examples or []
    
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'status': self.status,
            'explanation': self.explanation,
            'recommendation': self.recommendation,
            'score': self.score,
            'examples': self.examples
        }


class AEOAnalyzer:
    """Analyzes content for Answer Engine Optimization"""
    
    def __init__(self, content: Dict):
        self.content = content
        self.checks: List[AEOCheck] = []
    
    def analyze(self) -> Dict:
        """Run all AEO checks"""
        self.checks = []
        
        self.check_question_headings()
        self.check_direct_answers()
        self.check_answer_length()
        self.check_definition_clarity()
        self.check_structured_content()
        self.check_fluff_detection()
        
        return {
            'checks': [check.to_dict() for check in self.checks],
            'summary': self._generate_summary(),
            'top_issues': self._identify_top_issues()
        }
    
    def check_question_headings(self):
        """Check if headings are formatted as questions"""
        all_headings = []
        headings_dict = self.content.get('headings', {})
        
        for level in ['h2', 'h3', 'h4']:
            all_headings.extend(headings_dict.get(level, []))
        
        if not all_headings:
            self.checks.append(AEOCheck(
                name="Question-Style Headings",
                status="fail",
                explanation="No H2-H4 headings found. AI engines look for question-based headings.",
                recommendation="Add headings that directly address user questions (What is...? How to...? Why...?).",
                score=0
            ))
            return
        
        # Check for question keywords
        question_headings = []
        question_keywords = config.AEO_THRESHOLDS['question_keywords']
        
        for heading in all_headings:
            heading_lower = heading.lower()
            if any(keyword in heading_lower for keyword in question_keywords) or '?' in heading:
                question_headings.append(heading)
        
        question_ratio = len(question_headings) / len(all_headings) if all_headings else 0
        
        if question_ratio == 0:
            self.checks.append(AEOCheck(
                name="Question-Style Headings",
                status="fail",
                explanation=f"None of your {len(all_headings)} headings are question-based. AI engines prioritize content that directly answers questions.",
                recommendation="Rewrite headings to address specific user questions. Examples: 'What is [topic]?', 'How to [task]?', 'Why [concept]?'",
                score=0,
                examples=all_headings[:3]
            ))
        elif question_ratio < 0.3:
            self.checks.append(AEOCheck(
                name="Question-Style Headings",
                status="warning",
                explanation=f"Only {len(question_headings)}/{len(all_headings)} headings are question-based ({question_ratio*100:.0f}%).",
                recommendation="Increase question-based headings to at least 30%. Structure content around common user questions.",
                score=40,
                examples=question_headings[:3]
            ))
        else:
            self.checks.append(AEOCheck(
                name="Question-Style Headings",
                status="pass",
                explanation=f"{len(question_headings)}/{len(all_headings)} headings are question-based ({question_ratio*100:.0f}%) - good for AI engines.",
                recommendation="Continue using question-based headings. Ensure they match real user search queries.",
                score=100,
                examples=question_headings[:3]
            ))
    
    def check_direct_answers(self):
        """Check if content provides direct answers after question headings"""
        headings_dict = self.content.get('headings', {})
        paragraphs = self.content.get('paragraphs', [])
        faqs = self.content.get('faqs', [])
        
        # FAQs are ideal for direct answers
        if faqs:
            faq_count = len(faqs)
            # Check if FAQ answers are concise
            concise_answers = sum(1 for faq in faqs if 20 <= len(faq.get('answer', '').split()) <= 100)
            
            if concise_answers / faq_count > 0.7:
                self.checks.append(AEOCheck(
                    name="Direct Answers",
                    status="pass",
                    explanation=f"Found {faq_count} FAQ pairs with concise answers - excellent for AI extraction.",
                    recommendation="Continue providing direct, concise answers. Ensure they can stand alone without context.",
                    score=100,
                    examples=[f"Q: {faq['question'][:60]}..." for faq in faqs[:2]]
                ))
                return
        
        # Check if content provides immediate answers after headings
        # This is a heuristic check
        if not paragraphs:
            self.checks.append(AEOCheck(
                name="Direct Answers",
                status="fail",
                explanation="No paragraph content found to provide answers.",
                recommendation="Add clear, direct answers immediately after each heading. First sentence should directly answer the question.",
                score=0
            ))
            return
        
        # Check first sentences of paragraphs for directness
        direct_indicators = ['is', 'are', 'means', 'refers to', 'involves', 'includes', 'can', 'will', 'should']
        direct_paragraphs = []
        
        for para in paragraphs[:5]:  # Check first few paragraphs
            first_sentence = para.split('.')[0].lower()
            if any(indicator in first_sentence for indicator in direct_indicators) and len(first_sentence.split()) < 30:
                direct_paragraphs.append(para[:80])
        
        if not direct_paragraphs:
            self.checks.append(AEOCheck(
                name="Direct Answers",
                status="warning",
                explanation="Content appears to lack direct, immediate answers. Answers seem buried in paragraphs.",
                recommendation="Start each section with a direct answer (1-2 sentences). Then elaborate. Format: [Question heading] → [Direct answer] → [Details].",
                score=30
            ))
        else:
            self.checks.append(AEOCheck(
                name="Direct Answers",
                status="pass",
                explanation=f"Found {len(direct_paragraphs)} sections with direct answers.",
                recommendation="Good use of direct answers. Ensure every major section starts with a clear, quotable answer.",
                score=80,
                examples=direct_paragraphs[:2]
            ))
    
    def check_answer_length(self):
        """Check if answers are optimal length for AI extraction (40-80 words)"""
        paragraphs = self.content.get('paragraphs', [])
        faqs = self.content.get('faqs', [])
        
        # Prioritize FAQ answers
        if faqs:
            answer_lengths = [len(faq.get('answer', '').split()) for faq in faqs]
            optimal_count = sum(1 for length in answer_lengths 
                              if config.AEO_THRESHOLDS['answer_min_words'] <= length <= config.AEO_THRESHOLDS['answer_max_words'])
            
            if not answer_lengths:
                score = 0
                status = "fail"
            else:
                optimal_ratio = optimal_count / len(answer_lengths)
                
                if optimal_ratio > 0.7:
                    status = "pass"
                    score = 100
                elif optimal_ratio > 0.4:
                    status = "warning"
                    score = 70
                else:
                    status = "warning"
                    score = 40
            
            avg_length = sum(answer_lengths) / len(answer_lengths) if answer_lengths else 0
            
            self.checks.append(AEOCheck(
                name="Answer Length",
                status=status,
                explanation=f"{optimal_count}/{len(answer_lengths)} FAQ answers are optimal length (40-80 words). Avg: {avg_length:.0f} words.",
                recommendation=f"Aim for {config.AEO_THRESHOLDS['answer_ideal_words']} words per answer. Too short = incomplete. Too long = won't be used.",
                score=score
            ))
        else:
            # Check paragraph lengths as proxy
            if not paragraphs:
                self.checks.append(AEOCheck(
                    name="Answer Length",
                    status="fail",
                    explanation="No content found to evaluate answer length.",
                    recommendation="Add FAQ sections or ensure each heading is followed by a 40-80 word answer block.",
                    score=0
                ))
                return
            
            para_lengths = [len(p.split()) for p in paragraphs]
            optimal_paras = sum(1 for length in para_lengths 
                              if config.AEO_THRESHOLDS['answer_min_words'] <= length <= config.AEO_THRESHOLDS['answer_max_words'])
            
            optimal_ratio = optimal_paras / len(para_lengths)
            
            if optimal_ratio > 0.5:
                status = "pass"
                score = 80
            elif optimal_ratio > 0.3:
                status = "warning"
                score = 60
            else:
                status = "warning"
                score = 40
            
            avg_length = sum(para_lengths) / len(para_lengths)
            
            self.checks.append(AEOCheck(
                name="Answer Length",
                status=status,
                explanation=f"{optimal_paras}/{len(para_lengths)} paragraphs are answer-length optimal. Avg: {avg_length:.0f} words.",
                recommendation="Aim for 40-80 word answer blocks. Consider adding explicit FAQ section for better AI extraction.",
                score=score
            ))
    
    def check_definition_clarity(self):
        """Check if page provides clear definitions in first sentence"""
        paragraphs = self.content.get('paragraphs', [])
        
        if not paragraphs:
            self.checks.append(AEOCheck(
                name="Definition Clarity",
                status="fail",
                explanation="No paragraph content found.",
                recommendation="Add a clear definition in the first paragraph. Format: '[Term] is [definition]'.",
                score=0
            ))
            return
        
        # Check first paragraph for definition patterns
        first_para = paragraphs[0].lower()
        first_sentence = first_para.split('.')[0]
        
        definition_patterns = [
            r'\b(is|are|means|refers to|defines|represents)\b',
            r'\b(is a|is an|are a|are an)\b'
        ]
        
        has_definition = any(re.search(pattern, first_sentence) for pattern in definition_patterns)
        
        # Check if first sentence is concise (definitions should be)
        first_sentence_words = len(first_sentence.split())
        
        if has_definition and first_sentence_words < 30:
            self.checks.append(AEOCheck(
                name="Definition Clarity",
                status="pass",
                explanation="First paragraph provides a clear, concise definition - ideal for AI extraction.",
                recommendation="Maintain this pattern. Clear definitions help AI engines generate accurate summaries.",
                score=100,
                examples=[paragraphs[0][:120]]
            ))
        elif has_definition:
            self.checks.append(AEOCheck(
                name="Definition Clarity",
                status="warning",
                explanation=f"First paragraph has definition language but is verbose ({first_sentence_words} words).",
                recommendation="Shorten the opening definition to under 30 words. Be more direct and specific.",
                score=70,
                examples=[paragraphs[0][:120]]
            ))
        else:
            self.checks.append(AEOCheck(
                name="Definition Clarity",
                status="warning",
                explanation="First paragraph doesn't provide a clear definition. AI engines prefer immediate clarity.",
                recommendation="Start with a direct definition: '[Topic] is [clear definition]'. Then elaborate in following paragraphs.",
                score=40,
                examples=[paragraphs[0][:120]]
            ))
    
    def check_structured_content(self):
        """Check for lists, steps, and structured data that AI engines prefer"""
        lists = self.content.get('lists', [])
        tables = self.content.get('tables', [])
        headings = self.content.get('headings', {})
        
        structure_score = 0
        structure_elements = []
        
        if lists:
            structure_score += 40
            structure_elements.append(f"{len(lists)} lists")
        
        if tables:
            structure_score += 30
            structure_elements.append(f"{len(tables)} tables")
        
        # Check for numbered/procedural content
        all_headings = []
        for level in ['h2', 'h3', 'h4']:
            all_headings.extend(headings.get(level, []))
        
        procedural_headings = [h for h in all_headings if re.search(r'\b(step|how to|guide|tutorial|process)\b', h.lower())]
        if procedural_headings:
            structure_score += 30
            structure_elements.append(f"{len(procedural_headings)} procedural headings")
        
        structure_score = min(structure_score, 100)
        
        if structure_score >= 80:
            status = "pass"
        elif structure_score >= 50:
            status = "warning"
        else:
            status = "warning"
        
        if structure_elements:
            self.checks.append(AEOCheck(
                name="Structured Content",
                status=status,
                explanation=f"Page includes {', '.join(structure_elements)} - helps AI extraction.",
                recommendation="Continue using structured formats. Add more step-by-step guides, comparison tables, or bullet lists where relevant.",
                score=structure_score
            ))
        else:
            self.checks.append(AEOCheck(
                name="Structured Content",
                status="fail",
                explanation="No structured content detected (lists, tables, steps). AI engines strongly prefer structured data.",
                recommendation="Add bullet points, numbered lists, comparison tables, or step-by-step guides. These are easy for AI to extract and display.",
                score=20
            ))
    
    def check_fluff_detection(self):
        """Detect fluffy, unnecessary language that doesn't add value"""
        paragraphs = self.content.get('paragraphs', [])
        
        if not paragraphs:
            self.checks.append(AEOCheck(
                name="Fluff Detection",
                status="pass",
                explanation="No content to analyze for fluff.",
                recommendation="When adding content, avoid filler phrases. Be direct and specific.",
                score=100
            ))
            return
        
        all_text = ' '.join(paragraphs).lower()
        fluff_phrases = config.AEO_THRESHOLDS['fluff_phrases']
        
        detected_fluff = []
        for phrase in fluff_phrases:
            if phrase in all_text:
                detected_fluff.append(phrase)
        
        # Check for other generic patterns
        generic_patterns = [
            r"it('s)? important to (note|understand|remember)",
            r"as (you )?( can|may) (know|see|imagine)",
            r"in (this|our) (blog post|article|guide)",
            r"(let('s)?|we('ll)?|we will) (take a look|explore|dive into|discuss)"
        ]
        
        for pattern in generic_patterns:
            if re.search(pattern, all_text):
                detected_fluff.append(f"Generic phrase: {pattern}")
        
        fluff_count = len(detected_fluff)
        
        if fluff_count == 0:
            self.checks.append(AEOCheck(
                name="Fluff Detection",
                status="pass",
                explanation="Content is direct and value-focused with minimal fluff.",
                recommendation="Maintain this concise, direct style. AI engines prefer substance over style.",
                score=100
            ))
        elif fluff_count <= 2:
            self.checks.append(AEOCheck(
                name="Fluff Detection",
                status="warning",
                explanation=f"Detected {fluff_count} instances of fluffy language.",
                recommendation="Remove unnecessary phrases. Get to the point faster. AI engines skip filler content.",
                score=70,
                examples=detected_fluff[:2]
            ))
        else:
            self.checks.append(AEOCheck(
                name="Fluff Detection",
                status="warning",
                explanation=f"Detected {fluff_count} instances of fluffy, generic language. This dilutes answer quality.",
                recommendation="Cut filler phrases. Start paragraphs with direct statements. Remove meta-commentary about the article itself.",
                score=40,
                examples=detected_fluff[:3]
            ))
    
    def _generate_summary(self) -> Dict:
        """Generate summary statistics"""
        total_checks = len(self.checks)
        passed = sum(1 for c in self.checks if c.status == "pass")
        warnings = sum(1 for c in self.checks if c.status == "warning")
        failed = sum(1 for c in self.checks if c.status == "fail")
        
        return {
            'total_checks': total_checks,
            'passed': passed,
            'warnings': warnings,
            'failed': failed
        }
    
    def _identify_top_issues(self) -> List[str]:
        """Identify top 3 reasons AI won't pick this page"""
        issues = []
        
        for check in self.checks:
            if check.status in ['fail', 'warning'] and check.score < 60:
                issues.append({
                    'name': check.name,
                    'reason': check.explanation,
                    'score': check.score
                })
        
        # Sort by score (lowest first = biggest issues)
        issues.sort(key=lambda x: x['score'])
        
        return issues[:3]
