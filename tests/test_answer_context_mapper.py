import pytest
from cissp_analyzer.answer_context_mapper import AnswerContextMapper


class TestAnswerContextMapper:
    """Tests for using answer text to enhance domain/topic classification."""

    def test_extract_keywords_from_answer_text(self):
        """Test keyword extraction from answer explanations."""
        mapper = AnswerContextMapper()
        answer_text = "AES is a symmetric encryption algorithm used for data protection"

        keywords = mapper.extract_keywords(answer_text)

        assert "aes" in keywords
        assert "symmetric" in keywords
        assert "encryption" in keywords

    def test_map_question_with_context(self):
        """Test domain mapping using both Q and A context."""
        mapper = AnswerContextMapper()

        question_text = "Which cryptographic method uses a shared secret key?"
        answer_text = "AES (Advanced Encryption Standard) is the symmetric encryption standard"

        # Should map to Cryptography domain based on both texts
        domain = mapper.map_with_context(question_text, answer_text)

        assert domain == "Cryptography" or "Crypt" in domain

    def test_map_access_control_question(self):
        """Test that answer context helps classify access control questions."""
        mapper = AnswerContextMapper()

        question = "Which component manages user privileges?"
        answer = "Role-Based Access Control (RBAC) manages permissions and access levels"

        domain = mapper.map_with_context(question, answer)

        assert "Access" in domain or "Control" in domain

    def test_map_with_question_only_fallback(self):
        """Test that empty answer text falls back to question-only mapping."""
        mapper = AnswerContextMapper()

        question = "What is the primary goal of asset management?"
        answer = ""

        domain = mapper.map_with_context(question, answer)

        assert domain is not None  # Should still produce a result

    def test_improve_classification_with_answer_keywords(self):
        """Test that answer keywords improve classification accuracy."""
        mapper = AnswerContextMapper()

        # Question is vague, but answer keywords clarify domain
        question = "This framework addresses multiple security areas"
        answer_keywords = ["authentication", "authorization", "access control", "identity management"]

        improved_domain = mapper.map_with_keywords(question, answer_keywords)

        # Should classify as Access Control/Identity Management domain
        assert improved_domain is not None

    def test_handle_conflicting_contexts(self):
        """Test behavior when question and answer suggest different domains."""
        mapper = AnswerContextMapper()

        # Question might suggest one domain, answer text suggests another
        question = "What principle guides security design?"
        answer = "Defense in Depth uses multiple layers of cryptographic controls"

        # Should integrate both for most accurate classification
        result = mapper.map_with_context(question, answer)

        assert result is not None

    def test_extract_domain_keywords_from_answer(self):
        """Test that domain-specific keywords are extracted from answers."""
        mapper = AnswerContextMapper()

        domain_keywords = {
            "Cryptography": ["AES", "RSA", "encryption", "cipher", "hash"],
            "Access Control": ["RBAC", "authorization", "permissions", "roles"],
            "Governance": ["policy", "compliance", "standards", "risk"],
        }

        answer_text = "RBAC provides role-based authorization and permission management"

        detected_domains = mapper.detect_domains_from_text(answer_text, domain_keywords)

        assert "Access Control" in detected_domains
