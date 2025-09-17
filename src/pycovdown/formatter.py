def format_missing_lines(missing_lines):
    """Format missing line numbers into a compact representation."""
    if not missing_lines:
        return ""
    
    # Make sure we're working with a sorted list
    missing = sorted(list(missing_lines))
    
    ranges = []
    start = missing[0]
    end = start
    
    for line in missing[1:]:
        if line == end + 1:
            end = line
        else:
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{end}")
            start = end = line
    
    # Add the last range
    if start == end:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{end}")
    
    # Limit output length
    if len(ranges) > 10:
        result = ", ".join(ranges[:10]) + ", ..."
    else:
        result = ", ".join(ranges)
        
    return result
