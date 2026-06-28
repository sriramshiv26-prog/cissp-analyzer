import re
from typing import Dict, Optional


class QuestionAnalyzer:
    """Analyzes questions to extract domain, topic, difficulty, type, and exam tricks"""

    # Official ISC2 CISSP Domains
    DOMAIN_KEYWORDS = {
        1: ['security', 'risk management', 'governance', 'risk assessment', 'risk analysis',
            'business continuity', 'disaster recovery', 'incident', 'response', 'compliance',
            'legal', 'regulatory', 'ethics', 'policy', 'planning', 'rpo', 'rto', 'backup'],
        2: ['asset', 'security', 'data protection', 'privacy', 'classification', 'data handling',
            'storage', 'data lifecycle', 'sanitization', 'destruction', 'purge', 'database',
            'data management', 'retention', 'disposal'],
        3: ['security architecture', 'engineering', 'cryptography', 'encryption', 'certificate',
            'pki', 'physical security', 'design', 'threat modeling', 'security model', 'common criteria',
            'fire suppression', 'access point', 'architectural pattern'],
        4: ['communication', 'network security', 'network', 'protocol', 'tcp', 'ip', 'osi', 'ethernet',
            'router', 'switch', 'vpn', 'ipsec', 'dns', 'dhcp', 'email', 'smtp', 'pop', 'imap',
            'ssl', 'tls', 'voip', 'sip', 'wireless', 'wifi', '802.11', 'mobile'],
        5: ['identity', 'access management', 'authentication', 'authorization', 'access control',
            'biometric', 'kerberos', 'ldap', 'radius', 'tacacs', 'iam', 'permission', 'privilege',
            'role-based', 'attribute-based', 'factor', 'mfa', 'password', 'credential'],
        6: ['security assessment', 'testing', 'vulnerability', 'penetration', 'code review',
            'audit', 'scan', 'attack', 'exploit', 'security testing', 'sast', 'dast', 'assessment'],
        7: ['security operations', 'incident response', 'forensic', 'logging', 'monitoring',
            'operation', 'maintenance', 'change management', 'patch', 'update', 'detection',
            'investigation', 'evidence', 'recovery'],
        8: ['software development', 'security', 'code', 'programming', 'sdlc', 'secure coding',
            'testing', 'review', 'architecture', 'design pattern', 'language', 'development'],
    }

    # ISC2 Official CISSP Topics (based on exam outline)
    TOPIC_KEYWORDS = {
        # Domain 1: Security & Risk Management
        'Governance': ['governance', 'policy', 'framework', 'standard', 'procedure'],
        'Risk Assessment': ['risk assessment', 'risk analysis', 'risk evaluation', 'asset valuation'],
        'Risk Management': ['risk management', 'risk mitigation', 'risk treatment', 'countermeasure'],
        'Compliance': ['compliance', 'regulation', 'legal', 'regulatory', 'audit'],
        'Business Continuity': ['business continuity', 'continuity planning', 'rpo', 'rto'],
        'Disaster Recovery': ['disaster recovery', 'recovery plan', 'backup', 'restoration'],
        'Incident Response': ['incident response', 'incident management', 'breach', 'compromise'],

        # Domain 2: Asset Security
        'Data Classification': ['classification', 'categorization', 'labeling', 'sensitivity'],
        'Data Protection': ['data protection', 'privacy', 'pii', 'sensitive data'],
        'Data Handling': ['handling', 'storage', 'transmission', 'processing'],
        'Data Lifecycle': ['lifecycle', 'retention', 'disposal', 'destruction', 'sanitization'],

        # Domain 3: Security Architecture & Engineering
        'Security Design': ['security design', 'architecture', 'engineering', 'design principle'],
        'Cryptography': ['cryptography', 'encryption', 'cipher', 'hash', 'signature'],
        'PKI': ['pki', 'certificate', 'ca', 'crl', 'ocsp', 'public key'],
        'Physical Security': ['physical', 'access control', 'badging', 'mantrap', 'fire suppression'],
        'Threat Modeling': ['threat modeling', 'threat analysis', 'attack vector'],

        # Domain 4: Communication & Network Security
        'Network Architecture': ['network', 'topology', 'architecture', 'infrastructure'],
        'Network Protocols': ['protocol', 'tcp', 'ip', 'osi', 'ethernet', 'arp'],
        'Network Security': ['network security', 'firewall', 'ids', 'ips'],
        'Email Security': ['email', 'smtp', 'pop', 'imap', 's/mime'],
        'VPN/Remote Access': ['vpn', 'remote access', 'ipsec', 'ssl'],
        'Wireless Security': ['wireless', 'wifi', '802.11', 'wep', 'wpa'],
        'Telecom Security': ['voip', 'sip', 'telecom'],

        # Domain 5: Identity & Access Management
        'Access Control': ['access control', 'acl', 'permission', 'privilege'],
        'Authentication': ['authentication', 'factor', 'mfa', '2fa', 'password'],
        'Authorization': ['authorization', 'role-based', 'attribute-based', 'rbac', 'abac'],
        'Identity Management': ['identity', 'identity management', 'iam', 'directory'],
        'Biometrics': ['biometric', 'fingerprint', 'iris', 'facial recognition'],
        'AAA': ['kerberos', 'ldap', 'radius', 'tacacs', 'diameter'],

        # Domain 6: Security Assessment & Testing
        'Vulnerability Assessment': ['vulnerability', 'assessment', 'scan', 'discovery'],
        'Penetration Testing': ['penetration', 'penetration testing', 'ethical hacking'],
        'Code Review': ['code review', 'code analysis', 'sast', 'dast'],
        'Security Testing': ['security testing', 'test', 'testing'],
        'Audit': ['audit', 'auditing', 'logging', 'review'],

        # Domain 7: Security Operations
        'Incident Management': ['incident', 'incident management', 'detection', 'response'],
        'Forensics': ['forensic', 'evidence', 'investigation', 'chain of custody'],
        'Logging & Monitoring': ['logging', 'monitoring', 'log', 'siem'],
        'Change Management': ['change management', 'change control', 'patch'],
        'Operations': ['operations', 'maintenance', 'administration'],

        # Domain 8: Software Development Security
        'SDLC': ['sdlc', 'development lifecycle', 'secure development'],
        'Secure Coding': ['secure coding', 'coding', 'code', 'programming'],
        'Software Testing': ['testing', 'unit test', 'integration test', 'qa'],
        'Software Architecture': ['architecture', 'design', 'pattern', 'design pattern'],
    }

    @staticmethod
    def extract_domain(question_text: str) -> int:
        """Extract CISSP domain (1-8) from question text"""
        text_lower = question_text.lower()

        domain_scores = {}
        for domain_num, keywords in QuestionAnalyzer.DOMAIN_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                domain_scores[domain_num] = score

        return max(domain_scores.items(), key=lambda x: x[1])[0] if domain_scores else 1

    @staticmethod
    def extract_topic(question_text: str) -> str:
        """Extract topic from question text"""
        text_lower = question_text.lower()

        topic_scores = {}
        for topic, keywords in QuestionAnalyzer.TOPIC_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                topic_scores[topic] = score

        if topic_scores:
            return max(topic_scores.items(), key=lambda x: x[1])[0]
        return "General"

    @staticmethod
    def extract_question_type(question_text: str) -> str:
        """Extract question type: Application, Exception, Scenario, Sequence"""
        text_lower = question_text.lower()

        # Exception type: has "NOT", "EXCEPT", etc.
        if re.search(r'\b(not|except|all are|all of the)\b.*\btrue\b', text_lower) or \
           re.search(r'\b(which|what).*\b(not|except)\b', text_lower):
            return "Exception"

        # Sequence type: has ordering keywords
        if re.search(r'\b(first|second|third|order|sequence|step|phase)\b', text_lower):
            return "Sequence"

        # Scenario type: longer, narrative style with names/context
        if len(question_text) > 200 or re.search(r'\b[A-Z][a-z]+\s+(is|has|was)\b', question_text):
            return "Scenario"

        # Default to Application
        return "Application"

    @staticmethod
    def extract_exam_trick(question_text: str) -> Optional[str]:
        """Extract exam trick type: NOT, BEST, MOST, FIRST, ONLY, etc."""
        text_upper = question_text.upper()

        tricks = [
            ('NOT', r'\b(NOT|EXCEPT|NONE OF)\b'),
            ('BEST', r'\b(BEST|MOST APPROPRIATE|MOST LIKELY)\b'),
            ('MOST', r'\b(MOST|GREATEST|HIGHEST)\b'),
            ('FIRST', r'\b(FIRST|PRIMARY|INITIAL)\b'),
            ('ONLY', r'\b(ONLY|SOLELY|EXCLUSIVELY)\b'),
        ]

        for trick_name, pattern in tricks:
            if re.search(pattern, text_upper):
                return trick_name

        return None

    @staticmethod
    def extract_difficulty(question_text: str, options: Dict[str, str]) -> str:
        """Extract difficulty: Easy, Medium, Hard"""
        # Simple heuristic: length and complexity
        text_len = len(question_text)
        option_len = sum(len(opt) for opt in options.values())
        total_len = text_len + option_len

        # Count technical terms
        tech_terms = len(re.findall(r'\b(algorithm|protocol|cipher|biometric|kerberos|pki)\b',
                                     question_text.lower()))

        if total_len < 150 and tech_terms == 0:
            return "Easy"
        elif total_len > 400 or tech_terms >= 3:
            return "Hard"
        else:
            return "Medium"

    @staticmethod
    def analyze(question_num: int, question_text: str, options: Dict[str, str]) -> Dict:
        """Analyze a complete question and return all attributes"""
        return {
            'number': question_num,
            'domain': QuestionAnalyzer.extract_domain(question_text),
            'topic': QuestionAnalyzer.extract_topic(question_text),
            'subtopic': QuestionAnalyzer.extract_topic(question_text),  # Can refine later
            'difficulty': QuestionAnalyzer.extract_difficulty(question_text, options),
            'question_type': QuestionAnalyzer.extract_question_type(question_text),
            'exam_trick': QuestionAnalyzer.extract_exam_trick(question_text),
        }
