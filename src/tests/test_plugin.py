import pytest
import os
import tempfile
from unittest.mock import MagicMock, patch
from pycovdown.plugin import pytest_addoption, pytest_terminal_summary, create_markdown_report
from coverage import Coverage

def test_pytest_addoption():
    """Test that the plugin adds the correct command line option."""
    parser = MagicMock()
    group = MagicMock()
    parser.getgroup.return_value = group
    
    pytest_addoption(parser)
    
    # Verify parser.getgroup was called with 'pycovdown'
    parser.getgroup.assert_called_once_with('pycovdown')
    
    # Verify addoption was called with the correct parameters
    group.addoption.assert_called_once()
    args, kwargs = group.addoption.call_args
    assert args[0] == '--cov-pycovdown'
    assert kwargs['dest'] == 'pycovdown_file'

def test_pytest_terminal_summary_no_file():
    """Test terminal summary when no output file is specified."""
    config = MagicMock()
    config.option.pycovdown_file = None
    terminalreporter = MagicMock()
    
    pytest_terminal_summary(terminalreporter, 0, config)
    
    # Verify that no write operations were performed
    terminalreporter.write.assert_not_called()

@patch('pycovdown.plugin.create_markdown_report')
def test_pytest_terminal_summary_with_file(mock_create_report):
    """Test terminal summary with an output file specified."""
    config = MagicMock()
    config.option.pycovdown_file = 'coverage.md'
    
    terminalreporter = MagicMock()
    terminalreporter.config.pluginmanager.get_plugin.return_value = MagicMock()
    terminalreporter.config.pluginmanager.get_plugin.return_value.cov_controller.cov = "coverage_data"
    
    pytest_terminal_summary(terminalreporter, 0, config)
    
    # Verify that create_markdown_report was called with right parameters
    mock_create_report.assert_called_once_with("coverage_data", 'coverage.md')
    
    # Verify terminal report was written
    terminalreporter.write.assert_called_once()
    assert "Created markdown with missing code coverage" in terminalreporter.write.call_args[0][0]

@patch('builtins.open', new_callable=MagicMock)
@patch('os.path.relpath', return_value='test_file.py')
def test_create_markdown_report_empty(mock_relpath, mock_open):
    """Test report creation with no files having missing coverage."""
    # Set up mocks
    cov_data = MagicMock(spec=Coverage)
    cov_data.get_data().measured_files.return_value = []
    
    # Call function
    create_markdown_report(cov_data, 'output.md')
    
    # Check writes
    write_calls = [call[0][0] for call in mock_open.return_value.__enter__.return_value.write.call_args_list]
    assert '# Coverage Report' in write_calls[0]
    assert '## Summary' in write_calls[1]

@patch('builtins.open')
def test_create_markdown_report_with_files(mock_open):
    """Test report creation with files having missing coverage."""
    # Set up file mocks more carefully
    report_mock = MagicMock()
    source_mock = MagicMock()
    source_mock.__enter__.return_value.readlines.return_value = ["line1\n", "line2\n", "line3\n", "line4\n", "line5\n"]
    
    # Important: define the side_effect to return different mocks for each call
    mock_open.side_effect = lambda file, mode='r', encoding=None: report_mock if file == 'output.md' else source_mock
    
    # Set up coverage data mock
    cov_data = MagicMock(spec=Coverage)
    cov_data.get_data().measured_files.return_value = ['test_file.py']
    cov_data.analysis2.return_value = (
        [1, 2],  # Executed statements
        [3, 5],  # Missing statements
        [],      # Excluded statements
        [3, 5]   # Missing lines
    )
    
    # Call function directly without additional patches
    create_markdown_report(cov_data, 'output.md')

    # Verify writes were made
    report_mock.__enter__.return_value.write.assert_any_call("# Coverage Report\n\n")
    assert report_mock.__enter__.return_value.write.call_count > 5  # Ensure multiple writes happened