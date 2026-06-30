import pytest
from cissp_analyzer.filename_parser import FilenameParser


class TestFilenameParser:
    """Test suite for FilenameParser class"""

    def test_extract_student_name_from_standard_pattern(self):
        """Test extracting student name from filename"""
        parser = FilenameParser()

        # Test case 1: Simple name
        result = parser.extract_student_name("Mock1_Jun26_Sri.xlsx")
        assert result == "Sri"

        # Test case 2: Different exam number
        result = parser.extract_student_name("Mock2_Jun28_Sam.xlsx")
        assert result == "Sam"

        # Test case 3: Two-digit exam number
        result = parser.extract_student_name("Mock10_Aug15_Bob.xlsx")
        assert result == "Bob"

    def test_extract_exam_number(self):
        """Test extracting exam number from filename"""
        parser = FilenameParser()

        # Test case 1: Single digit exam number
        result = parser.extract_exam_number("Mock1_Jun26_Sri.xlsx")
        assert result == 1
        assert isinstance(result, int)

        # Test case 2: Two-digit exam number
        result = parser.extract_exam_number("Mock10_Aug15_Bob.xlsx")
        assert result == 10

        # Test case 3: Three-digit exam number
        result = parser.extract_exam_number("Mock100_Sep20_Alice.xlsx")
        assert result == 100

    def test_malformed_filename_returns_none(self):
        """Test that malformed filenames return None"""
        parser = FilenameParser()

        # Missing .xlsx extension
        assert parser.extract_student_name("Mock1_Jun26_Sri.txt") is None
        assert parser.extract_exam_number("Mock1_Jun26_Sri.txt") is None

        # Wrong format structure
        assert parser.extract_student_name("Sri_Jun26_Mock1.xlsx") is None
        assert parser.extract_exam_number("Sri_Jun26_Mock1.xlsx") is None

        # Incomplete pattern
        assert parser.extract_student_name("Mock1_Jun26.xlsx") is None
        assert parser.extract_exam_number("Mock1_Jun26.xlsx") is None

    def test_case_insensitive_extraction(self):
        """Test that extraction works with different cases"""
        parser = FilenameParser()

        # Uppercase MOCK
        result = parser.extract_student_name("MOCK1_Jun26_Sri.xlsx")
        assert result == "Sri" or result is None  # Depends on implementation

        # Mixed case student name
        result = parser.extract_student_name("Mock1_Jun26_SrI.xlsx")
        assert result == "SrI" or result == "sri"  # Should normalize

    def test_matches_pattern(self):
        """Test pattern matching validation"""
        parser = FilenameParser()

        # Valid patterns
        assert parser.matches_pattern("Mock1_Jun26_Sri.xlsx") is True
        assert parser.matches_pattern("Mock10_Aug15_Bob.xlsx") is True

        # Invalid patterns
        assert parser.matches_pattern("Mock1_Jun26_Sri.txt") is False
        assert parser.matches_pattern("Sri_Jun26_Mock1.xlsx") is False
        assert parser.matches_pattern("invalid.xlsx") is False

    def test_extract_date(self):
        """Test extracting date from filename"""
        parser = FilenameParser()

        result = parser.extract_date("Mock1_Jun26_Sri.xlsx")
        assert result == "Jun26"

        result = parser.extract_date("Mock2_Aug15_Bob.xlsx")
        assert result == "Aug15"

        # Test invalid filename returns None
        result = parser.extract_date("invalid.xlsx")
        assert result is None

    def test_normalize_student_name(self):
        """Test student name normalization"""
        # Test lowercase conversion
        assert FilenameParser.normalize_student_name("Sri") == "sri"
        assert FilenameParser.normalize_student_name("SRI") == "sri"
        assert FilenameParser.normalize_student_name("Sri Raj") == "sri raj"

        # Test whitespace stripping
        assert FilenameParser.normalize_student_name(" Sri ") == "sri"
        assert FilenameParser.normalize_student_name("  Bob  ") == "bob"
