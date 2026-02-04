"""
Advanced NLP-based Intelligence Extraction
Uses spaCy for entity recognition and pattern matching
"""

import re
import logging
from typing import Dict, List, Set

logger = logging.getLogger(__name__)

class NLPIntelligenceExtractor:
    """Advanced NLP-based intelligence extraction"""
    
    def __init__(self):
        self.nlp = None
        self._load_spacy()
        
        # Enhanced patterns
        self.patterns = {
            'upiIds': [
                r'\b[\w\.-]+@(?:paytm|phonepe|googlepay|amazonpay|ybl|okaxis|okhdfcbank|okicici|oksbi|okhsbc|axl|ibl|airtel|fbl|pnb|boi|cnrb|cbin|ubin|kkbk|mahb|sbin|pytm|yesbank)\b',
                r'\b\d{10}@\w+\b',
                r'\b[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\b'
            ],
            'phoneNumbers': [
                r'\+91[-\s]?\d{10}',
                r'\b[6-9]\d{9}\b',
                r'(?:call|contact|phone|mobile|whatsapp).*?(\d{10})',
                r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})',
                r'(?:91)?[-\s]?[6-9]\d{9}'
            ],
            'bankAccounts': [
                r'\b\d{9,18}\b',
                r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
                r'(?:account|acc|a/c).*?(\d{10,18})',
                r'IFSC.*?([A-Z]{4}0[A-Z0-9]{6})'
            ],
            'phishingLinks': [
                r'https?://[^\s]+',
                r'www\.[^\s]+',
                r'\w+\.(?:com|in|org|net|co\.in|xyz|tk|ml|ga|cf)/[^\s]*',
                r'(?:click|visit|go to|open).*?([\w-]+\.(?:com|in|org|net))',
                r'bit\.ly/\w+',
                r'tinyurl\.com/\w+'
            ],
            'emails': [
                r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            ],
            'amounts': [
                r'₹\s*[\d,]+(?:\.\d{2})?',
                r'Rs\.?\s*[\d,]+',
                r'\b\d+\s*(?:lakh|crore|thousand|hundred)\b',
                r'\b\d+\s*rupees?\b'
            ]
        }
        
        # Scam keywords categorized
        self.keyword_categories = {
            'urgency': ['urgent', 'immediate', 'quickly', 'now', 'today', 'asap', 'hurry', 'fast'],
            'threats': ['block', 'suspend', 'freeze', 'close', 'terminate', 'legal action', 'police', 'arrest'],
            'credentials': ['otp', 'pin', 'cvv', 'password', 'passcode', 'security code', 'verification code'],
            'financial': ['transfer', 'pay', 'send', 'money', 'amount', 'rupees', 'account', 'bank', 'upi'],
            'verification': ['verify', 'confirm', 'update', 'validate', 'authenticate', 'kyc', 'details'],
            'rewards': ['won', 'prize', 'winner', 'congratulations', 'reward', 'cashback', 'refund', 'lottery'],
            'authority': ['rbi', 'government', 'bank', 'police', 'tax', 'income tax', 'gst', 'customs']
        }
    
    def _load_spacy(self):
        """Load spaCy model"""
        try:
            import spacy
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("✅ spaCy model loaded")
        except:
            logger.warning("⚠️ spaCy not available, using regex only")
            self.nlp = None
    
    def extract_with_nlp(self, text: str) -> Dict:
        """Extract entities using spaCy NER"""
        if not self.nlp:
            return {}
        
        doc = self.nlp(text)
        
        entities = {
            'persons': [],
            'organizations': [],
            'locations': [],
            'dates': [],
            'money': []
        }
        
        for ent in doc.ents:
            if ent.label_ == 'PERSON':
                entities['persons'].append(ent.text)
            elif ent.label_ == 'ORG':
                entities['organizations'].append(ent.text)
            elif ent.label_ == 'GPE' or ent.label_ == 'LOC':
                entities['locations'].append(ent.text)
            elif ent.label_ == 'DATE':
                entities['dates'].append(ent.text)
            elif ent.label_ == 'MONEY':
                entities['money'].append(ent.text)
        
        return entities
    
    def extract_with_regex(self, text: str) -> Dict:
        """Extract using regex patterns"""
        extracted = {}
        
        for intel_type, patterns in self.patterns.items():
            matches: Set[str] = set()
            for pattern in patterns:
                try:
                    found = re.findall(pattern, text, re.IGNORECASE)
                    if found:
                        matches.update([str(m) for m in found])
                except Exception as e:
                    logger.error(f"Regex error for {intel_type}: {e}")
            
            extracted[intel_type] = list(matches)
        
        return extracted
    
    def categorize_keywords(self, text: str) -> Dict:
        """Categorize suspicious keywords"""
        text_lower = text.lower()
        
        categorized = {}
        for category, keywords in self.keyword_categories.items():
            found = [kw for kw in keywords if kw in text_lower]
            if found:
                categorized[category] = found
        
        return categorized
    
    def calculate_scam_score(self, text: str, categorized_keywords: Dict) -> int:
        """Calculate comprehensive scam score"""
        score = 0
        
        # Keyword category weights
        weights = {
            'urgency': 15,
            'threats': 20,
            'credentials': 25,
            'financial': 15,
            'verification': 10,
            'rewards': 12,
            'authority': 10
        }
        
        for category, keywords in categorized_keywords.items():
            score += len(keywords) * weights.get(category, 5)
        
        # Additional patterns
        text_lower = text.lower()
        
        if 'click' in text_lower and 'link' in text_lower:
            score += 20
        
        if any(word in text_lower for word in ['otp', 'pin', 'cvv']):
            score += 25
        
        if 'transfer' in text_lower and 'money' in text_lower:
            score += 20
        
        # Multiple exclamation marks
        score += min(text.count('!') * 5, 15)
        
        # All caps words
        caps_words = len([w for w in text.split() if w.isupper() and len(w) > 3])
        score += min(caps_words * 5, 20)
        
        return min(score, 100)
    
    def extract_full_intelligence(self, conversation_history: List[Dict]) -> Dict:
        """Extract complete intelligence from conversation"""
        all_text = ' '.join([msg.get('text', '') for msg in conversation_history])
        
        # Regex extraction
        regex_intel = self.extract_with_regex(all_text)
        
        # NLP extraction
        nlp_intel = self.extract_with_nlp(all_text) if self.nlp else {}
        
        # Keyword categorization
        categorized = self.categorize_keywords(all_text)
        
        # Calculate scam score
        scam_score = self.calculate_scam_score(all_text, categorized)
        
        # Combine all intelligence
        intelligence = {
            **regex_intel,
            'nlp_entities': nlp_intel,
            'keyword_categories': categorized,
            'scamScore': scam_score,
            'suspiciousKeywords': [kw for kws in categorized.values() for kw in kws],
            'total_messages': len(conversation_history),
            'conversation_length': len(all_text)
        }
        
        return intelligence
    
    def get_scam_tactics(self, intelligence: Dict) -> List[str]:
        """Identify scammer tactics"""
        tactics = []
        
        categories = intelligence.get('keyword_categories', {})
        
        if 'urgency' in categories:
            tactics.append('urgency_pressure')
        
        if 'threats' in categories:
            tactics.append('intimidation')
        
        if 'credentials' in categories:
            tactics.append('credential_theft')
        
        if 'financial' in categories:
            tactics.append('payment_fraud')
        
        if 'rewards' in categories:
            tactics.append('prize_scam')
        
        if 'authority' in categories:
            tactics.append('authority_impersonation')
        
        if intelligence.get('phishingLinks'):
            tactics.append('phishing')
        
        if intelligence.get('scamScore', 0) > 70:
            tactics.append('high_risk_scam')
        
        return list(set(tactics))
