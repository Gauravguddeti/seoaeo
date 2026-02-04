"""
Scoring system for SEO and AEO analysis
Transparent, reproducible, weighted scoring
"""
from typing import Dict, List
import config


class ScoringEngine:
    """Calculates final scores from analysis checks"""
    
    @staticmethod
    def calculate_seo_score(checks: List[Dict]) -> Dict:
        """
        Calculate weighted SEO score from checks
        Returns score (0-100) and breakdown
        """
        if not checks:
            return {
                'score': 0,
                'grade': 'F',
                'breakdown': {},
                'explanation': 'No checks completed'
            }
        
        # Map check names to weight keys
        check_weights = {
            'Page Title': config.SEO_WEIGHTS['title'],
            'Meta Description': config.SEO_WEIGHTS['meta_description'],
            'H1 Heading': config.SEO_WEIGHTS['h1_count'],
            'Heading Hierarchy': config.SEO_WEIGHTS['heading_hierarchy'],
            'Content Length': config.SEO_WEIGHTS['content_length'],
            'Internal Links': config.SEO_WEIGHTS['internal_links'],
            'External Links': config.SEO_WEIGHTS['external_links'],
            'Readability': config.SEO_WEIGHTS['readability'],
            'Page Size': config.SEO_WEIGHTS['html_size'],
            'Keyword Balance': config.SEO_WEIGHTS['keyword_density'],
            'Image Optimization': config.SEO_WEIGHTS['images'],
            'Social Media (Open Graph)': config.SEO_WEIGHTS['open_graph'],
            'Structured Data (Schema)': config.SEO_WEIGHTS['schema_markup'],
        }
        
        total_score = 0
        total_weight = 0
        breakdown = {}
        
        for check in checks:
            check_name = check['name']
            check_score = check['score']
            weight = check_weights.get(check_name, 0)
            
            if weight > 0:
                weighted_score = (check_score / 100) * weight
                total_score += weighted_score
                total_weight += weight
                
                breakdown[check_name] = {
                    'raw_score': check_score,
                    'weight': weight,
                    'weighted_score': round(weighted_score, 2),
                    'status': check['status']
                }
        
        # Normalize to 0-100
        final_score = round(total_score, 1) if total_weight > 0 else 0
        grade = ScoringEngine._score_to_grade(final_score)
        
        return {
            'score': final_score,
            'grade': grade,
            'breakdown': breakdown,
            'explanation': ScoringEngine._generate_seo_explanation(final_score, checks)
        }
    
    @staticmethod
    def calculate_aeo_score(checks: List[Dict]) -> Dict:
        """
        Calculate weighted AEO score from checks
        Returns score (0-100) and breakdown
        """
        if not checks:
            return {
                'score': 0,
                'grade': 'F',
                'breakdown': {},
                'explanation': 'No checks completed'
            }
        
        # Map check names to weight keys
        check_weights = {
            'Question-Style Headings': config.AEO_WEIGHTS['question_headings'],
            'Direct Answers': config.AEO_WEIGHTS['direct_answers'],
            'Answer Length': config.AEO_WEIGHTS['answer_length'],
            'Definition Clarity': config.AEO_WEIGHTS['definition_clarity'],
            'Structured Content': config.AEO_WEIGHTS['structured_content'],
            'Fluff Detection': config.AEO_WEIGHTS['fluff_detection'],
        }
        
        total_score = 0
        total_weight = 0
        breakdown = {}
        
        for check in checks:
            check_name = check['name']
            check_score = check['score']
            weight = check_weights.get(check_name, 0)
            
            if weight > 0:
                weighted_score = (check_score / 100) * weight
                total_score += weighted_score
                total_weight += weight
                
                breakdown[check_name] = {
                    'raw_score': check_score,
                    'weight': weight,
                    'weighted_score': round(weighted_score, 2),
                    'status': check['status']
                }
        
        # Normalize to 0-100
        final_score = round(total_score, 1) if total_weight > 0 else 0
        grade = ScoringEngine._score_to_grade(final_score)
        
        return {
            'score': final_score,
            'grade': grade,
            'breakdown': breakdown,
            'explanation': ScoringEngine._generate_aeo_explanation(final_score, checks)
        }
    
    @staticmethod
    def _score_to_grade(score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    @staticmethod
    def _generate_seo_explanation(score: float, checks: List[Dict]) -> str:
        """Generate human-readable explanation of SEO score"""
        if score >= 90:
            return "Excellent SEO fundamentals. Your page follows best practices and is well-optimized for search engines."
        elif score >= 80:
            return "Good SEO foundation with minor areas for improvement. Address warnings to reach excellent status."
        elif score >= 70:
            return "Decent SEO but several important optimizations are missing. Focus on failed checks first."
        elif score >= 60:
            return "Basic SEO structure exists but needs significant improvement. Multiple critical issues need attention."
        else:
            return "Poor SEO foundation. Major elements are missing or incorrect. Immediate action needed on failed checks."
    
    @staticmethod
    def _generate_aeo_explanation(score: float, checks: List[Dict]) -> str:
        """Generate human-readable explanation of AEO score"""
        if score >= 90:
            return "Excellent answer-readiness. AI engines will easily extract and use your content for answers."
        elif score >= 80:
            return "Good AEO structure. Minor improvements will make content even more AI-friendly."
        elif score >= 70:
            return "Moderate answer optimization. Content exists but isn't optimally formatted for AI extraction."
        elif score >= 60:
            return "Weak AEO. Content may be found but likely won't be used by AI engines due to format issues."
        else:
            return "Poor answer optimization. AI engines will likely skip this content in favor of better-structured alternatives."
    
    @staticmethod
    def generate_priority_recommendations(seo_checks: List[Dict], aeo_checks: List[Dict], seo_score: float, aeo_score: float) -> List[Dict]:
        """Generate prioritized list of recommendations"""
        all_issues = []
        
        # Collect failed and warning checks
        for check in seo_checks:
            if check['status'] in ['fail', 'warning']:
                priority = 'high' if check['status'] == 'fail' else 'medium'
                if check['score'] < 50:
                    priority = 'high'
                
                all_issues.append({
                    'type': 'SEO',
                    'priority': priority,
                    'name': check['name'],
                    'issue': check['explanation'],
                    'fix': check['recommendation'],
                    'score': check['score']
                })
        
        for check in aeo_checks:
            if check['status'] in ['fail', 'warning']:
                priority = 'high' if check['status'] == 'fail' else 'medium'
                if check['score'] < 50:
                    priority = 'high'
                
                all_issues.append({
                    'type': 'AEO',
                    'priority': priority,
                    'name': check['name'],
                    'issue': check['explanation'],
                    'fix': check['recommendation'],
                    'score': check['score']
                })
        
        # Sort by priority and score
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        all_issues.sort(key=lambda x: (priority_order[x['priority']], x['score']))
        
        return all_issues
    
    @staticmethod
    def generate_action_checklist(recommendations: List[Dict]) -> List[str]:
        """Generate actionable checklist from recommendations"""
        checklist = []
        
        # Group by priority
        high_priority = [r for r in recommendations if r['priority'] == 'high']
        medium_priority = [r for r in recommendations if r['priority'] == 'medium']
        
        if high_priority:
            checklist.append("🔴 Critical Actions:")
            for rec in high_priority[:5]:  # Top 5 critical
                checklist.append(f"  • {rec['name']}: {rec['fix']}")
        
        if medium_priority:
            checklist.append("\n🟡 Important Improvements:")
            for rec in medium_priority[:5]:  # Top 5 important
                checklist.append(f"  • {rec['name']}: {rec['fix']}")
        
        return checklist
