#!/usr/bin/env python3
"""
Test utilities and helper functions for SMART_STUDENT
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


def test_simple_math():
    """Test basic mathematical operations"""
    assert 1 + 1 == 2
    assert 2 * 3 == 6
    assert 10 / 2 == 5
    assert 3 ** 2 == 9


def test_string_operations():
    """Test basic string operations"""
    test_string = "SMART_STUDENT"
    assert len(test_string) == 13
    assert test_string.lower() == "smart_student"
    assert "SMART" in test_string
    assert test_string.replace("_", "-") == "SMART-STUDENT"


def test_list_operations():
    """Test basic list operations"""
    test_list = [1, 2, 3, 4, 5]
    assert len(test_list) == 5
    assert max(test_list) == 5
    assert min(test_list) == 1
    assert sum(test_list) == 15


def test_dict_operations():
    """Test basic dictionary operations"""
    test_dict = {"name": "SMART_STUDENT", "version": "1.0", "type": "educational"}
    assert len(test_dict) == 3
    assert test_dict["name"] == "SMART_STUDENT"
    assert "version" in test_dict
    assert list(test_dict.keys()) == ["name", "version", "type"]


def test_file_operations():
    """Test basic file operations"""
    test_content = "This is a test file for SMART_STUDENT"
    test_file_path = "/tmp/test_smart_student.txt"
    
    # Write test file
    with open(test_file_path, 'w') as f:
        f.write(test_content)
    
    # Read and verify
    assert os.path.exists(test_file_path)
    with open(test_file_path, 'r') as f:
        content = f.read()
        assert content == test_content
    
    # Cleanup
    os.remove(test_file_path)
    assert not os.path.exists(test_file_path)


def test_exception_handling():
    """Test exception handling"""
    with pytest.raises(ZeroDivisionError):
        result = 1 / 0
    
    with pytest.raises(KeyError):
        test_dict = {"a": 1}
        value = test_dict["b"]
    
    with pytest.raises(IndexError):
        test_list = [1, 2, 3]
        value = test_list[10]


if __name__ == "__main__":
    pytest.main([__file__])
