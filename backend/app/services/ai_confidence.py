"""
AI Confidence Scoring Service
Provides trust-grade AI with confidence metrics, source attribution, and validation.
"""
from typing import Dict, List, Any, Optional
import numpy as np
from datetime import datetime


class AIConfidenceScorer:
    """
    Calculates confidence scores for AI responses based on multiple factors.
    """
    
    def __init__(self):
        self.min_confidence_threshold = 0.75
        self.weights = {
            'source_quality': 0.3,
            'context_match': 0.25,
            'response_coherence': 0.25,
            'factual_grounding': 0.2
        }
    
    def calculate_confidence(
        self, 
        response: str, 
        sources: List[Dict], 
        context: Dict,
        query: str
    ) -> Dict[str, Any]:
        """
        Calculate overall confidence score and breakdown.
        
        Args:
            response: The AI-generated response text
            sources: List of source documents used
            context: Conversation context
            query: Original user query
            
        Returns:
            Dictionary with overall score, breakdown, and threshold status
        """
        scores = {
            'source_quality': self._score_sources(sources),
            'context_match': self._score_context_relevance(context, query, response),
            'response_coherence': self._score_coherence(response),
            'factual_grounding': self._score_grounding(sources, response)
        }
        
        # Calculate weighted average
        overall = sum(scores[k] * self.weights[k] for k in scores.keys())
        
        return {
            'overall': round(overall, 3),
            'breakdown': {k: round(v, 3) for k, v in scores.items()},
            'threshold_met': overall >= self.min_confidence_threshold,
            'level': self._categorize_confidence(overall),
            'calculated_at': datetime.utcnow().isoformat()
        }
    
    def _score_sources(self, sources: List[Dict]) -> float:
        """Score based on quality and quantity of sources."""
        if not sources:
            return 0.0
        
        # Check source count
        source_count_score = min(len(sources) / 3, 1.0)  # Ideal: 3+ sources
        
        # Check source relevance scores
        relevance_scores = [s.get('score', 0) for s in sources]
        avg_relevance = np.mean(relevance_scores) if relevance_scores else 0
        
        # Check source types (prefer multiple types)
        source_types = set(s.get('type', 'unknown') for s in sources)
        type_diversity = min(len(source_types) / 2, 1.0)  # Ideal: 2+ types
        
        return (source_count_score * 0.4 + avg_relevance * 0.4 + type_diversity * 0.2)
    
    def _score_context_relevance(self, context: Dict, query: str, response: str) -> float:
        """Score how well response matches context and query."""
        score = 0.5  # Base score
        
        # Check if response addresses the query
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        overlap = len(query_words & response_words) / max(len(query_words), 1)
        score += overlap * 0.3
        
        # Check context usage
        if context and context.get('previous_messages'):
            score += 0.2  # Bonus for using context
        
        return min(score, 1.0)
    
    def _score_coherence(self, response: str) -> float:
        """Score response coherence and quality."""
        score = 0.5  # Base score
        
        # Check length (not too short, not too long)
        word_count = len(response.split())
        if 10 <= word_count <= 200:
            score += 0.2
        
        # Check for complete sentences
        if response.strip().endswith(('.', '!', '?')):
            score += 0.1
        
        # Check for structure (paragraphs, lists)
        if '\n' in response or any(marker in response for marker in ['1.', '2.', '-', '*']):
            score += 0.1
        
        # Penalize very short responses
        if word_count < 5:
            score -= 0.3
        
        return max(min(score, 1.0), 0.0)
    
    def _score_grounding(self, sources: List[Dict], response: str) -> float:
        """Score how well response is grounded in sources."""
        if not sources:
            return 0.3  # Low score if no sources
        
        score = 0.5  # Base score
        
        # Check if response contains information from sources
        source_texts = [s.get('content', '') for s in sources]
        response_lower = response.lower()
        
        # Simple overlap check
        overlaps = []
        for source_text in source_texts:
            if source_text:
                source_words = set(source_text.lower().split())
                response_words = set(response_lower.split())
                overlap = len(source_words & response_words) / max(len(response_words), 1)
                overlaps.append(overlap)
        
        if overlaps:
            avg_overlap = np.mean(overlaps)
            score += avg_overlap * 0.5
        
        return min(score, 1.0)
    
    def _categorize_confidence(self, score: float) -> str:
        """Categorize confidence level."""
        if score >= 0.9:
            return 'VERY_HIGH'
        elif score >= 0.75:
            return 'HIGH'
        elif score >= 0.6:
            return 'MEDIUM'
        elif score >= 0.4:
            return 'LOW'
        else:
            return 'VERY_LOW'


class SourceAttributor:
    """
    Attributes AI responses to specific source documents.
    """
    
    def attribute_sources(
        self, 
        response: str, 
        retrieved_docs: List[Dict]
    ) -> Dict[str, Any]:
        """
        Create source attribution for a response.
        
        Args:
            response: The AI-generated response
            retrieved_docs: Documents retrieved from RAG system
            
        Returns:
            Dictionary with source attribution details
        """
        # Sort by relevance score
        sorted_docs = sorted(
            retrieved_docs, 
            key=lambda x: x.get('score', 0), 
            reverse=True
        )
        
        primary_sources = []
        for doc in sorted_docs[:5]:  # Top 5 sources
            source_info = {
                'document_id': doc.get('id'),
                'document_name': doc.get('name', 'Untitled'),
                'relevance_score': round(doc.get('score', 0), 3),
                'excerpt': self._extract_excerpt(doc.get('content', ''), response),
                'type': doc.get('type', 'document'),
                'url': doc.get('url') if doc.get('type') == 'web' else None,
                'created_at': doc.get('created_at')
            }
            primary_sources.append(source_info)
        
        return {
            'primary_sources': primary_sources,
            'citation_count': len(retrieved_docs),
            'source_types': self._categorize_sources(retrieved_docs),
            'attribution_confidence': self._calculate_attribution_confidence(primary_sources)
        }
    
    def _extract_excerpt(self, content: str, response: str, max_length: int = 200) -> str:
        """Extract relevant excerpt from source content."""
        if not content:
            return ""
        
        # Find most relevant section (simple approach)
        # In production, use more sophisticated matching
        words = content.split()
        if len(words) <= max_length // 5:
            return content
        
        # Return first chunk for now
        excerpt = ' '.join(words[:max_length // 5])
        return excerpt + '...' if len(words) > max_length // 5 else excerpt
    
    def _categorize_sources(self, docs: List[Dict]) -> Dict[str, int]:
        """Categorize sources by type."""
        categories = {}
        for doc in docs:
            doc_type = doc.get('type', 'unknown')
            categories[doc_type] = categories.get(doc_type, 0) + 1
        return categories
    
    def _calculate_attribution_confidence(self, sources: List[Dict]) -> float:
        """Calculate confidence in source attribution."""
        if not sources:
            return 0.0
        
        # Average relevance score
        scores = [s['relevance_score'] for s in sources]
        return round(np.mean(scores), 3)


class HallucinationGuard:
    """
    Validates AI responses to prevent hallucinations.
    """
    
    def __init__(self):
        self.min_source_grounding = 0.5
        self.min_confidence = 0.6
        self.high_risk_patterns = [
            'i think', 'i believe', 'probably', 'maybe',
            'not sure', 'could be', 'might be'
        ]
    
    def validate_response(
        self, 
        response: str, 
        sources: List[Dict], 
        query: str,
        confidence_score: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Validate response for potential hallucinations.
        
        Args:
            response: AI-generated response
            sources: Source documents used
            query: Original query
            confidence_score: Pre-calculated confidence scores
            
        Returns:
            Validation result with approval status and reasons
        """
        checks = {
            'has_sources': self._check_has_sources(sources),
            'source_grounding': self._check_grounding(response, sources),
            'confidence_threshold': self._check_confidence(confidence_score),
            'no_uncertainty_language': self._check_uncertainty(response),
            'domain_validity': self._check_domain(response, query)
        }
        
        failed_checks = [k for k, v in checks.items() if not v]
        
        if failed_checks:
            return {
                'approved': False,
                'failed_checks': failed_checks,
                'reason': self._get_failure_reason(failed_checks),
                'action': 'ESCALATE_TO_HUMAN',
                'severity': self._calculate_severity(failed_checks)
            }
        
        return {
            'approved': True,
            'checks_passed': list(checks.keys()),
            'action': 'PROCEED'
        }
    
    def _check_has_sources(self, sources: List[Dict]) -> bool:
        """Check if response has source backing."""
        return len(sources) > 0
    
    def _check_grounding(self, response: str, sources: List[Dict]) -> bool:
        """Check if response is grounded in sources."""
        if not sources:
            return False
        
        # Simple check: response should have some overlap with sources
        response_words = set(response.lower().split())
        
        for source in sources:
            content = source.get('content', '')
            source_words = set(content.lower().split())
            overlap = len(response_words & source_words) / max(len(response_words), 1)
            
            if overlap >= self.min_source_grounding:
                return True
        
        return False
    
    def _check_confidence(self, confidence_score: Optional[Dict]) -> bool:
        """Check if confidence meets threshold."""
        if not confidence_score:
            return False
        return confidence_score.get('overall', 0) >= self.min_confidence
    
    def _check_uncertainty(self, response: str) -> bool:
        """Check for uncertainty language."""
        response_lower = response.lower()
        return not any(pattern in response_lower for pattern in self.high_risk_patterns)
    
    def _check_domain(self, response: str, query: str) -> bool:
        """Check if response is within valid domain."""
        # Simple check: response should be related to query
        query_words = set(query.lower().split())
        response_words = set(response.lower().split())
        overlap = len(query_words & response_words) / max(len(query_words), 1)
        
        return overlap > 0.1  # At least some relevance
    
    def _get_failure_reason(self, failed_checks: List[str]) -> str:
        """Generate human-readable failure reason."""
        reasons = {
            'has_sources': 'No source documents found',
            'source_grounding': 'Response not grounded in sources',
            'confidence_threshold': 'Confidence score too low',
            'no_uncertainty_language': 'Response contains uncertainty language',
            'domain_validity': 'Response may be off-topic'
        }
        
        return '; '.join(reasons.get(check, check) for check in failed_checks)
    
    def _calculate_severity(self, failed_checks: List[str]) -> str:
        """Calculate severity of validation failure."""
        critical_checks = ['has_sources', 'source_grounding', 'confidence_threshold']
        
        if any(check in critical_checks for check in failed_checks):
            return 'HIGH'
        elif len(failed_checks) >= 2:
            return 'MEDIUM'
        else:
            return 'LOW'
