import pytest
from pycovdown.formatter import format_missing_lines

def test_format_missing_lines_empty_list():
    """Test formatting with empty list."""
    assert format_missing_lines([]) == ""

def test_format_missing_lines_single_value():
    """Test formatting with a single line."""
    assert format_missing_lines([42]) == "42"

def test_format_missing_lines_consecutive():
    """Test formatting with consecutive lines."""
    assert format_missing_lines([1, 2, 3, 4, 5]) == "1-5"

def test_format_missing_lines_non_consecutive():
    """Test formatting with non-consecutive lines."""
    assert format_missing_lines([1, 3, 5, 7, 9]) == "1, 3, 5, 7, 9"

def test_format_missing_lines_mixed():
    """Test formatting with mixed consecutive and non-consecutive lines."""
    assert format_missing_lines([1, 2, 3, 5, 6, 9]) == "1-3, 5-6, 9"

def test_format_missing_lines_complex():
    """Test formatting with complex pattern of lines."""
    assert format_missing_lines([1, 3, 4, 5, 10, 11, 15]) == "1, 3-5, 10-11, 15"

def test_format_missing_lines_truncated():
    """Test truncation of long lists of ranges."""
    long_list = list(range(1, 100, 2))  # [1, 3, 5, ..., 99]
    result = format_missing_lines(long_list)
    assert result.endswith(", ...")
    assert len(result.split(",")) == 11  # 10 ranges + "..."