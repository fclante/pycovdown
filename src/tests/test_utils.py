import pytest
from pycovdown.utils import extract_code_sections

def test_extract_code_sections_empty():
    """Test extraction with empty input."""
    lines = ["line 1", "line 2", "line 3"]
    missing = []
    assert extract_code_sections(lines, missing) == []

def test_extract_code_sections_single_line():
    """Test extraction with a single missing line."""
    lines = ["line 1", "line 2", "line 3", "line 4", "line 5"]
    missing = [3]  # Line 3 is missing
    sections = extract_code_sections(lines, missing)
    assert sections == [(0, 4)]  # Should include 2 lines before and after

def test_extract_code_sections_range_boundary():
    """Test extraction at file boundaries."""
    lines = ["line 1", "line 2", "line 3", "line 4", "line 5"]
    missing = [1, 5]  # First and last lines are missing
    sections = extract_code_sections(lines, missing)
    # Should include context but respect file boundaries
    assert sections == [(0, 2), (2, 4)]

def test_extract_code_sections_merged():
    """Test merging of nearby sections."""
    lines = ["line 1", "line 2", "line 3", "line 4", "line 5", 
             "line 6", "line 7", "line 8", "line 9", "line 10"]
    missing = [2, 6]  # Lines 2 and 6 are missing (within 4 lines of each other)
    sections = extract_code_sections(lines, missing)
    # Should merge sections because they're close
    assert sections == [(0, 8)]

def test_extract_code_sections_separate():
    """Test separation of distant sections."""
    lines = ["line 1", "line 2", "line 3", "line 4", "line 5", 
             "line 6", "line 7", "line 8", "line 9", "line 10"]
    missing = [2, 9]  # Lines 2 and 9 are missing (more than 4 lines apart)
    sections = extract_code_sections(lines, missing)
    # Should be two separate sections
    assert sections == [(0, 4), (6, 9)]

def test_extract_code_sections_multiple_adjacent():
    """Test extraction with multiple adjacent missing lines."""
    lines = ["line 1", "line 2", "line 3", "line 4", "line 5", 
             "line 6", "line 7", "line 8", "line 9", "line 10"]
    missing = [3, 4, 5]  # Three consecutive lines missing
    sections = extract_code_sections(lines, missing)
    # Should be one section with proper context
    assert sections == [(0, 7)]