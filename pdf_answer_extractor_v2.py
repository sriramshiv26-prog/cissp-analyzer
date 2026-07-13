#!/usr/bin/env python3
"""
Advanced PDF Answer Extractor v2
Extracts answers by matching question blocks instead of regex alone
"""

import re
from typing import Dict, Tuple


class AdvancedAnswerExtractor:
    """Extract answers by identifying question blocks and matching answers within each block"""

    @staticmethod
    def extract_by_question_blocks(pdf_text: str) -> Tuple[Dict[int, str], Dict[str, any]]:
        """
        Extract answers by finding question blocks and their answers

        Args:
            pdf_text: Full text extracted from PDF

        Returns:
            (answer_key dict, metadata dict with confidence)
        """
        answer_key = {}
        metadata = {
            "total_extracted": 0,
            "pattern_matches": 0,
            "block_matches": 0,
            "issues": []
        }

        # Split into lines
        lines = pdf_text.split('\n')

        # Find all question numbers (pattern: "N. " where N is a number)
        question_pattern = r'^(\d+)\.\s'

        question_blocks = {}
        current_q_num = None
        current_block = []

        # Build question blocks
        for i, line in enumerate(lines):
            match = re.match(question_pattern, line.strip())
            if match:
                q_num = int(match.group(1))

                # If we have a previous block, save it
                if current_q_num is not None:
                    question_blocks[current_q_num] = '\n'.join(current_block)

                # Start new block
                current_q_num = q_num
                current_block = [line]
            else:
                if current_q_num is not None:
                    current_block.append(line)

        # Save last block
        if current_q_num is not None:
            question_blocks[current_q_num] = '\n'.join(current_block)

        # Extract answers from each block
        answer_pattern = r"(?:correct\s+answer\s+is|answer\s+is|The\s+correct\s+answer\s+(?:is|:))\s*([A-D])"

        for q_num in sorted(question_blocks.keys()):
            block = question_blocks[q_num]

            # Look for answer within this block
            match = re.search(answer_pattern, block, re.IGNORECASE)

            if match:
                answer = match.group(1).upper()
                answer_key[q_num] = answer
                metadata["pattern_matches"] += 1
                metadata["block_matches"] += 1
            else:
                # Fallback: look for single letter followed by period as answer
                # Pattern: ") A." or similar at end of choice
                if re.search(r'\)\s+([A-D])[.)]', block):
                    fallback_match = re.search(r'\)\s+([A-D])[.)]', block)
                    if fallback_match:
                        answer = fallback_match.group(1)
                        answer_key[q_num] = answer
                        metadata["issues"].append(f"Q{q_num}: Used fallback pattern")
                else:
                    metadata["issues"].append(f"Q{q_num}: No answer found")

        metadata["total_extracted"] = len(answer_key)
        return answer_key, metadata

    @staticmethod
    def extract_question_metadata(pdf_text: str) -> Dict[int, Dict[str, str]]:
        """
        Extract question metadata (domain, topic, difficulty) from PDF

        Args:
            pdf_text: Full text extracted from PDF

        Returns:
            Dict mapping question number to metadata
        """
        metadata = {}

        # Keywords mapping to domains
        domain_keywords = {
            1: ['security management', 'risk', 'governance', 'policies'],
            2: ['asset', 'inventory', 'classification', 'data'],
            3: ['architecture', 'design', 'cryptography', 'encryption'],
            4: ['network', 'communication', 'protocol', 'transmission'],
            5: ['identity', 'access', 'authentication', 'authorization'],
            6: ['assessment', 'testing', 'vulnerability', 'penetration'],
            7: ['operations', 'incident', 'response', 'monitoring'],
            8: ['software', 'development', 'code', 'application']
        }

        topic_keywords = {
            'privacy': 'Privacy',
            'confidentiality': 'Confidentiality',
            'integrity': 'Integrity',
            'availability': 'Availability',
            'cryptography': 'Cryptography',
            'authentication': 'Authentication',
            'access control': 'Access Control',
            'vulnerability': 'Vulnerability',
            'compliance': 'Compliance',
            'security': 'Security',
        }

        # This is a simplified approach - in production would need more sophisticated NLP
        # For now, return empty metadata for questions > 42 (which don't have data)

        return metadata


def improve_extraction(pdf_text: str) -> Dict[int, str]:
    """
    Extract answers using improved method
    """
    extractor = AdvancedAnswerExtractor()
    answer_key, metadata = extractor.extract_by_question_blocks(pdf_text)

    print(f"Extraction Results:")
    print(f"  Total extracted: {metadata['total_extracted']}")
    print(f"  Pattern matches: {metadata['pattern_matches']}")
    print(f"  Block matches: {metadata['block_matches']}")

    if metadata['issues']:
        print(f"  Issues: {len(metadata['issues'])}")
        for issue in metadata['issues'][:5]:
            print(f"    - {issue}")

    return answer_key
