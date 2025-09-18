from pycovdown.formatter import format_missing_lines
from pycovdown.util import extract_code_sections
import os, re, pytest
from coverage import Coverage

def pytest_addoption(parser):
  group = parser.getgroup('pycovdown')
  group.addoption(
    '--cov-pycovdown',
    action='store',
    dest='pycovdown_file',
    metavar='path',
    default=None,
    help='create markdown coverage report at given path'
  )
  
@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):  # Changed from existatus to exitstatus
  pycovdown_file = config.option.pycovdown_file
  if (pycovdown_file is None):
    return
  
  if (not hasattr(terminalreporter.config, 'pluginmanager')):
    terminalreporter.write('pycovdown: pytest-cov not found, cannot generate report\n')
    return
  
  cov_plugin = terminalreporter.config.pluginmanager.get_plugin('_cov')
  if (not cov_plugin):
    terminalreporter.write('pycovdown: pytest-cov plugin not found\n')
    return
  
  if (not hasattr(cov_plugin, 'cov_controller')):
    terminalreporter.write('pycovdown: no coverage data available\n')
    return
  
  cov_data = cov_plugin.cov_controller.cov
  
  try:
    create_markdown_report(cov_data, pycovdown_file)
    terminalreporter.write(f'pycovdown: Created markdown with missing code coverage at {pycovdown_file}\n')
  except Exception as e:
    terminalreporter.write(f'pycovdown: Error creating markdown from missing code coverage data: {str(e)}\n')
    

def create_markdown_report(cov_data: Coverage, output_path: str):
    """
    Reads data about missing coverage and generates nicely formatted code,
    embedded in a markdown file with references to the files that has missing coverage.
    
    Args:
        cov_data (Coverage): The coverage object from pytest-cov containing coverage data
        output_path (str): File path where the markdown report should be saved
    """
    try:
        with open(output_path, 'w') as report:
            # Write header
            report.write("# Coverage Report\n\n")
            
            # Get files with missing coverage
            files_with_missing = {}
            total_stmts = 0
            total_miss = 0
            
            # Process each measured file
            for file_path in cov_data.get_data().measured_files():
                analysis = cov_data.analysis2(file_path)
                
                # Fix the statements calculation
                # Check types and handle appropriately
                if isinstance(analysis[0], list) and isinstance(analysis[1], list):
                    statements = set(analysis[0] + analysis[1])  # executed + missing statements
                else:
                    # Handle the case where they might be strings or other types
                    try:
                        statements = set([int(x) for x in analysis[0].split(',') if x.strip()] + 
                                        [int(x) for x in analysis[1].split(',') if x.strip()])
                    except (AttributeError, ValueError):
                        # Fallback if we can't parse them
                        statements = set()
                        print(f"Warning: Unexpected analysis data for {file_path}: {analysis[0]}, {analysis[1]}")
                
                missing_lines = analysis[3] if isinstance(analysis[3], list) else []
                
                if missing_lines:
                    stmts_count = len(statements)
                    miss_count = len(missing_lines)
                    coverage_pct = 100 - (miss_count * 100 / stmts_count) if stmts_count > 0 else 100
                    
                    files_with_missing[file_path] = {
                        'stmts': stmts_count,
                        'miss': miss_count,
                        'cover': coverage_pct,
                        'missing': missing_lines  # Keep as list, don't convert to set
                    }
                    
                    total_stmts += stmts_count
                    total_miss += miss_count
            
            # Write summary table
            report.write("## Summary\n\n")
            report.write("| Name | Stmts | Miss | Cover | Missing |\n")
            report.write("|------|-------|------|-------|---------|\n")
            
            for file_path, data in sorted(files_with_missing.items()):
                # Format missing lines for display (group consecutive lines)
                missing_formatted = format_missing_lines(data['missing'])
                
                # Write file row - ensure all values are strings before concatenation
                report.write(f"| {os.path.relpath(file_path)} | {data['stmts']} | {data['miss']} | {data['cover']:.0f}% | {missing_formatted} |\n")
            
            # Write total row
            if total_stmts > 0:
                total_cover = 100 - (total_miss * 100 / total_stmts)
                report.write(f"| **TOTAL** | **{total_stmts}** | **{total_miss}** | **{total_cover:.0f}%** | |\n\n")
            else:
                report.write(f"| **TOTAL** | **0** | **0** | **100%** | |\n\n")
            
            # Write detailed code sections
            report.write("## Detailed Code Sections with Missing Coverage\n\n")
            
            for file_path, data in sorted(files_with_missing.items()):
                rel_path = os.path.relpath(file_path)
                report.write(f"### {rel_path}\n\n")
                
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as src_file:
                        lines = src_file.readlines()
                    
                    # Get code sections with context
                    code_sections = extract_code_sections(lines, data['missing'])
                    
                    # Write each code section
                    for start, end in code_sections:
                        report.write("```python\n")
                        for i in range(start, end + 1):
                            if i < len(lines):
                                line_num = i + 1
                                is_missing = line_num in data['missing']
                                marker = "❌" if is_missing else "  "
                                line_text = lines[i].rstrip('\n')
                                report.write(f"{line_num:4d}{marker} {line_text}\n")
                        report.write("```\n\n")
                except Exception as e:
                    report.write(f"*Error reading file: {str(e)}*\n\n")
        
        return True
    except Exception as e:
        import traceback
        print(f"Error in create_markdown_report: {str(e)}")
        print(traceback.format_exc())
        raise


