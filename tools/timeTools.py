from datetime import datetime, timezone
from langchain_core.tools import tool


@tool
def convertISOToUTCEpoch(isoTimeString: str) -> int:
    '''
    Converts an ISO format time string to UTC epoch seconds (UTC时间戳秒数).
    Supports various ISO formats including:
    - 2024-01-01T12:00:00Z
    - 2024-01-01T12:00:00+08:00
    - 2024-01-01T12:00:00-05:00
    - 2024-01-01T12:00:00.123456Z
    - 2024-01-01 12:00:00 (without timezone, assumed as UTC)
    
    If the conversion fails, returns an error message.

    Args:
        isoTimeString (str): The ISO format time string to convert.
                          This argument is required.
                          Examples: '2024-01-01T12:00:00Z', '2024-01-01T12:00:00+08:00'

    Returns:
        int: The UTC epoch seconds (timestamp in seconds since 1970-01-01 00:00:00 UTC).
             Returns an error message string if conversion fails.
    '''
    try:
        # Try to parse the ISO format string
        # datetime.fromisoformat() handles most ISO formats, but not 'Z' suffix
        # So we replace 'Z' with '+00:00' first
        iso_str = isoTimeString.strip().replace('Z', '+00:00')
        
        # Parse the ISO string
        dt = datetime.fromisoformat(iso_str)
        
        # Convert to UTC timestamp (epoch seconds)
        # If the datetime is timezone-aware, timestamp() automatically converts to UTC
        if dt.tzinfo is not None:
            epoch_seconds = int(dt.timestamp())
        else:
            # If no timezone info, assume it's already in UTC
            # Create a UTC timezone-aware datetime
            dt_utc = dt.replace(tzinfo=timezone.utc)
            epoch_seconds = int(dt_utc.timestamp())
        
        return epoch_seconds
    
    except ValueError as e:
        return f'Error: Invalid ISO time format. {str(e)}'
    except Exception as e:
        return f'Error happens in converting ISO time to UTC epoch seconds: {str(e)}'
