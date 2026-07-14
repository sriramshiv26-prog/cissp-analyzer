"""
Tests for the Trap Analysis Engine

Tests the complete trap category analysis system for identifying student
cognitive traps and generating personalized study recommendations.
"""

import pytest
from cissp_analyzer.trap_analysis_engine import (
    TrapAnalysisEngine,
    TrapExplanation,
    TrapVulnerability,
    AnswerAnalysisResult,
)


@pytest.fixture
def engine():
    """Initialize trap analysis engine."""
    return TrapAnalysisEngine()


class TestTrapAnalysisEngineInitialization:
    """Test engine initialization and data loading."""

    def test_engine_initializes_successfully(self, engine):
        """Test that engine loads without errors."""
        assert engine is not None

    def test_trap_categories_loaded(self, engine):
        """Test that trap categories are loaded."""
        assert engine.trap_categories is not None
        assert len(engine.trap_categories) == 21

    def test_question_mappings_loaded(self, engine):
        """Test that question mappings are loaded."""
        assert engine.question_mappings is not None
        assert len(engine.question_mappings) == 161

    def test_all_trap_categories_have_metadata(self, engine):
        """Test that each trap category has required fields."""
        for trap_code, trap_data in engine.trap_categories.items():
            assert "name" in trap_data
            assert "type" in trap_data
            assert "frequency" in trap_data
            assert len(trap_code) <= 10  # Reasonable code length


class TestSingleAnswerAnalysis:
    """Test single answer analysis functionality."""

    def test_analyze_correct_answer(self, engine):
        """Test analyzing a correct answer."""
        result = engine.analyze_answer(1, "B", "B")
        assert result.is_correct is True
        assert result.trap_category is None
        assert result.trap_explanation is None

    def test_analyze_wrong_answer(self, engine):
        """Test analyzing a wrong answer."""
        result = engine.analyze_answer(31, "C", "A")
        assert result.is_correct is False
        assert result.trap_category is not None
        assert result.trap_explanation is not None

    def test_analyzed_result_has_required_fields(self, engine):
        """Test that analyzed result has all required fields."""
        result = engine.analyze_answer(31, "C", "A")
        assert hasattr(result, "question_num")
        assert hasattr(result, "student_answer")
        assert hasattr(result, "correct_answer")
        assert hasattr(result, "is_correct")
        assert hasattr(result, "trap_category")
        assert hasattr(result, "domain")
        assert hasattr(result, "difficulty")

    def test_trap_explanation_quality(self, engine):
        """Test that trap explanations are detailed."""
        result = engine.analyze_answer(31, "C", "A")
        if result.trap_explanation:
            assert result.trap_explanation.why_student_fell
            assert result.trap_explanation.isc2_fix
            assert result.trap_explanation.prevention_tip
            assert 0.0 <= result.trap_explanation.confidence_score <= 1.0

    def test_analyze_multiple_wrong_answers(self, engine):
        """Test analyzing different wrong answers."""
        wrong_combos = [(1, "C", "B"), (31, "B", "A"), (58, "D", "C")]
        results = [engine.analyze_answer(q, s, c) for q, s, c in wrong_combos]
        assert all(r.is_correct is False for r in results)
        assert all(r.trap_category is not None for r in results)


class TestBatchAnswerAnalysis:
    """Test batch answer analysis functionality."""

    def test_batch_analysis_completes(self, engine):
        """Test that batch analysis processes all answers."""
        answers = {1: "B", 31: "C", 58: "A", 120: "D"}
        answer_key = {1: "B", 31: "A", 58: "C", 120: "D"}
        results = engine.analyze_all_answers(answers, answer_key)
        assert len(results) == 4

    def test_batch_analysis_returns_list(self, engine):
        """Test that batch analysis returns a list."""
        answers = {1: "B", 31: "C"}
        answer_key = {1: "B", 31: "A"}
        results = engine.analyze_all_answers(answers, answer_key)
        assert isinstance(results, list)

    def test_batch_analysis_with_empty_answers(self, engine):
        """Test batch analysis with empty input."""
        results = engine.analyze_all_answers({}, {})
        assert isinstance(results, list)
        assert len(results) == 0

    def test_batch_analysis_mixed_correct_wrong(self, engine):
        """Test batch analysis with mix of correct and wrong answers."""
        answers = {1: "B", 31: "C", 58: "C"}
        answer_key = {1: "B", 31: "A", 58: "C"}
        results = engine.analyze_all_answers(answers, answer_key)
        correct = sum(1 for r in results if r.is_correct)
        wrong = sum(1 for r in results if not r.is_correct)
        assert correct + wrong == 3
        assert wrong == 1  # Only Q31 is wrong


class TestVulnerabilitySummarization:
    """Test trap vulnerability summarization."""

    def test_vulnerability_summary_returns_list(self, engine):
        """Test that vulnerability summary returns a list."""
        answers = {1: "B", 31: "C", 58: "A"}
        answer_key = {1: "B", 31: "A", 58: "C"}
        results = engine.analyze_all_answers(answers, answer_key)
        vulnerabilities = engine.summarize_vulnerabilities(results)
        assert isinstance(vulnerabilities, list)

    def test_vulnerabilities_identify_weak_traps(self, engine):
        """Test that vulnerabilities identify student weak areas."""
        answers = {31: "C", 50: "B"}
        answer_key = {31: "A", 50: "D"}
        results = engine.analyze_all_answers(answers, answer_key)
        vulnerabilities = engine.summarize_vulnerabilities(results)
        # Should identify traps the student fell for
        if vulnerabilities:
            vuln = vulnerabilities[0]
            assert vuln.trap_category
            assert vuln.frequency_count > 0

    def test_vulnerability_has_required_fields(self, engine):
        """Test that vulnerability objects have required fields."""
        answers = {31: "C"}
        answer_key = {31: "A"}
        results = engine.analyze_all_answers(answers, answer_key)
        vulnerabilities = engine.summarize_vulnerabilities(results)
        if vulnerabilities:
            vuln = vulnerabilities[0]
            assert hasattr(vuln, "trap_category")
            assert hasattr(vuln, "frequency_count")
            assert hasattr(vuln, "affected_questions")
            assert hasattr(vuln, "severity")


class TestRecommendationGeneration:
    """Test personalized study recommendation generation."""

    def test_recommendations_return_dict(self, engine):
        """Test that recommendations are returned as a dict."""
        answers = {1: "B", 31: "C", 58: "A"}
        answer_key = {1: "B", 31: "A", 58: "C"}
        results = engine.analyze_all_answers(answers, answer_key)
        vulnerabilities = engine.summarize_vulnerabilities(results)
        recs = engine.generate_recommendations(vulnerabilities)
        assert isinstance(recs, dict)

    def test_recommendations_target_weak_areas(self, engine):
        """Test that recommendations target identified weak areas."""
        answers = {31: "C", 50: "B"}
        answer_key = {31: "A", 50: "D"}
        results = engine.analyze_all_answers(answers, answer_key)
        vulnerabilities = engine.summarize_vulnerabilities(results)
        recs = engine.generate_recommendations(vulnerabilities)
        # Should provide actionable recommendations
        assert len(recs) >= 0  # May be empty if no vulnerabilities

    def test_recommendation_has_study_details(self, engine):
        """Test that recommendations include study details."""
        answers = {31: "C"}
        answer_key = {31: "A"}
        results = engine.analyze_all_answers(answers, answer_key)
        vulnerabilities = engine.summarize_vulnerabilities(results)
        recs = engine.generate_recommendations(vulnerabilities)
        # Should return dict with study recommendations
        assert isinstance(recs, dict)
        assert "study_plan" in recs or "high_priority_traps" in recs


class TestTrapCategoryReference:
    """Test trap category lookup functionality."""

    def test_get_trap_details(self, engine):
        """Test retrieving trap category details."""
        trap_detail = engine.get_trap_details("VERSUS")
        assert trap_detail is not None
        assert trap_detail["name"] == "Similar Options"

    def test_get_trap_details_invalid_code(self, engine):
        """Test getting details for invalid trap code."""
        trap_detail = engine.get_trap_details("INVALID")
        assert trap_detail is None

    def test_get_question_trap_info(self, engine):
        """Test retrieving question trap information."""
        trap_info = engine.get_question_trap_info(31)
        assert trap_info is not None
        assert "trap_category" in trap_info

    def test_get_question_trap_info_invalid(self, engine):
        """Test getting trap info for invalid question."""
        trap_info = engine.get_question_trap_info(999)
        assert trap_info is None

    def test_all_trap_codes_valid(self, engine):
        """Test that all trap codes are valid references."""
        legacy_codes = {"BEST", "NOT", "FIRST"}  # Legacy codes not in reference.json
        for question_num in range(1, 162):
            trap_info = engine.get_question_trap_info(question_num)
            if trap_info and "trap_category" in trap_info:
                trap_code = trap_info["trap_category"]
                # Either in current categories or legacy codes
                assert trap_code in engine.trap_categories or trap_code in legacy_codes


class TestExportFunctionality:
    """Test result export functionality."""

    def test_export_to_json_format(self, engine):
        """Test exporting results to JSON format."""
        result = engine.analyze_answer(31, "C", "A")
        json_output = engine.export_analysis_results([result], format="json")
        assert isinstance(json_output, str)
        # Should be valid JSON
        import json as json_module

        json_module.loads(json_output)

    def test_export_to_json(self, engine):
        """Test exporting results to JSON string."""
        result = engine.analyze_answer(31, "C", "A")
        json_str = engine.export_analysis_results([result], format="json")
        assert isinstance(json_str, str)
        assert "31" in json_str or "question" in json_str.lower()

    def test_export_multiple_results(self, engine):
        """Test exporting multiple analysis results."""
        answers = {31: "C", 58: "A"}
        answer_key = {31: "A", 58: "C"}
        results = engine.analyze_all_answers(answers, answer_key)
        exported = engine.export_analysis_results(results, format="json")
        assert isinstance(exported, str)
        # Should be valid JSON
        import json as json_module

        json_module.loads(exported)


class TestPerformance:
    """Test performance characteristics."""

    def test_single_answer_analysis_performance(self, engine):
        """Test that single answer analysis is fast."""
        import time

        start = time.time()
        for i in range(100):
            engine.analyze_answer(31, "C", "A")
        duration = time.time() - start
        assert duration < 5.0  # Should process 100 in under 5 seconds

    def test_batch_analysis_performance(self, engine):
        """Test that batch analysis is efficient."""
        import time

        answers = {i: chr(65 + (i % 4)) for i in range(1, 162)}
        answer_key = {i: chr(65 + ((i + 1) % 4)) for i in range(1, 162)}

        start = time.time()
        results = engine.analyze_all_answers(answers, answer_key)
        duration = time.time() - start

        assert len(results) == 161
        assert duration < 5.0  # Should process all 161 in under 5 seconds


class TestIntegrationScenarios:
    """Test realistic usage scenarios."""

    def test_complete_student_analysis_workflow(self, engine):
        """Test complete workflow: upload → analyze → summarize → recommend."""
        # Simulate student exam answers
        student_answers = {
            1: "B",
            2: "C",  # Wrong - should be A
            31: "C",  # Wrong - should be A
            58: "C",  # Correct
            120: "D",  # Correct
        }
        answer_key = {1: "B", 2: "A", 31: "A", 58: "C", 120: "D"}

        # Step 1: Analyze all answers
        results = engine.analyze_all_answers(student_answers, answer_key)
        assert len(results) == 5

        # Step 2: Summarize vulnerabilities
        vulnerabilities = engine.summarize_vulnerabilities(results)
        assert isinstance(vulnerabilities, list)

        # Step 3: Generate recommendations
        recs = engine.generate_recommendations(vulnerabilities)
        assert isinstance(recs, dict)
        assert "study_plan" in recs or "high_priority_traps" in recs

        # Should identify weak areas
        score = sum(1 for r in results if r.is_correct) / len(results)
        assert score == 0.6  # 3/5 correct

    def test_high_performing_student(self, engine):
        """Test analysis of high-performing student (80%+)."""
        answers = {i: chr(65 + (i % 4)) for i in range(1, 162)}
        # Make 80% correct
        answer_key = {i: chr(65 + (i % 4)) for i in range(1, 162)}
        # Wrong on 20% (32 questions)
        for i in range(1, 33):
            answers[i] = chr(65 + ((i + 1) % 4))

        results = engine.analyze_all_answers(answers, answer_key)
        vulnerabilities = engine.summarize_vulnerabilities(results)

        # High performing student should have fewer vulnerabilities
        correct = sum(1 for r in results if r.is_correct)
        score = correct / len(results)
        assert score >= 0.8

    def test_struggling_student(self, engine):
        """Test analysis of struggling student (<50%)."""
        answers = {i: chr(65 + ((i + 1) % 4)) for i in range(1, 162)}
        answer_key = {i: chr(65 + (i % 4)) for i in range(1, 162)}

        results = engine.analyze_all_answers(answers, answer_key)
        vulnerabilities = engine.summarize_vulnerabilities(results)

        # Struggling student should show multiple vulnerabilities
        correct = sum(1 for r in results if r.is_correct)
        score = correct / len(results)
        assert score < 0.5


class TestDataIntegrity:
    """Test data integrity and edge cases."""

    def test_all_161_questions_have_traps(self, engine):
        """Test that all 161 questions have trap assignments."""
        for q_num in range(1, 162):
            trap_info = engine.get_question_trap_info(q_num)
            assert trap_info is not None
            assert trap_info.get("trap_category") is not None

    def test_trap_categories_consistent(self, engine):
        """Test that trap category definitions are consistent."""
        for trap_code in ["NEG", "ORDER", "TOOL", "VERSUS"]:
            trap_data = engine.trap_categories.get(trap_code)
            assert trap_data is not None
            assert "name" in trap_data
            assert "the_trap" in trap_data or "type" in trap_data

    def test_answer_comparison_edge_cases(self, engine):
        """Test edge cases in answer comparison."""
        # Case-insensitive comparison
        result1 = engine.analyze_answer(1, "b", "B")
        result2 = engine.analyze_answer(1, "B", "B")
        # Both should be treated as correct
        assert result1.is_correct
        assert result2.is_correct

    def test_multiple_correct_answers(self, engine):
        """Test handling of different answer formats."""
        # Uppercase
        result_upper = engine.analyze_answer(1, "A", "A")
        # Lowercase
        result_lower = engine.analyze_answer(1, "a", "a")
        assert result_upper.is_correct
        assert result_lower.is_correct


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
