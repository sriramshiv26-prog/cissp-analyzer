import re
from typing import Optional


class FilenameParser:
    """Parser for extracting student name and exam info from standardized filenames.

    Expected filename pattern: Mock[N]_[Date]_[StudentName].xlsx
    Examples:
        - Mock1_Jun26_Sri.xlsx -> student: "Sri", exam: 1
        - Mock2_Jun28_Sam.xlsx -> student: "Sam", exam: 2
        - Mock10_Aug15_Bob.xlsx -> student: "Bob", exam: 10
    """

    # Regex pattern: Mock(digits)_date(alphanumeric)_name(alphanumeric+spaces).xlsx
    PATTERN = r"Mock(\d+)_([A-Za-z0-9]+)_([A-Za-z0-9\s]+)\.xlsx"

    def extract_student_name(self, filename: str) -> Optional[str]:
        """Extract student name from filename.

        Args:
            filename: The filename to parse

        Returns:
            Student name if pattern matches, None otherwise
        """
        match = re.match(self.PATTERN, filename)
        if match:
            return match.group(3).strip()
        return None

    def extract_exam_number(self, filename: str) -> Optional[int]:
        """Extract exam number from filename.

        Args:
            filename: The filename to parse

        Returns:
            Exam number as int if pattern matches, None otherwise
        """
        match = re.match(self.PATTERN, filename)
        if match:
            return int(match.group(1))
        return None

    def extract_date(self, filename: str) -> Optional[str]:
        """Extract date from filename.

        Args:
            filename: The filename to parse

        Returns:
            Date string if pattern matches, None otherwise
        """
        match = re.match(self.PATTERN, filename)
        if match:
            return match.group(2)
        return None

    def matches_pattern(self, filename: str) -> bool:
        """Check if filename matches the expected pattern.

        Args:
            filename: The filename to validate

        Returns:
            True if filename matches pattern, False otherwise
        """
        return bool(re.match(self.PATTERN, filename))

    @staticmethod
    def normalize_student_name(name: str) -> str:
        """Normalize student name by converting to lowercase and stripping whitespace.

        Args:
            name: The student name to normalize

        Returns:
            Normalized name (lowercase, whitespace trimmed)
        """
        return name.strip().lower()
