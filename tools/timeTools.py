from datetime import datetime, timezone
try:
    from zoneinfo import ZoneInfo
except ImportError:
    # Fallback for older Python versions (Python < 3.9)
    # Users can install backports.zoneinfo if needed: pip install backports.zoneinfo
    ZoneInfo = None

def getUTCNow():
    '''
    Gets the current UTC time.
    '''
    return datetime.now(timezone.utc)

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


def convertUTCEpochToISO(epochSeconds: int) -> str:
    '''
    Converts UTC epoch seconds to standard ISO format time string (将UTC时间戳秒数转换为标准ISO时间格式).
    Returns the time in standard ISO 8601 format with UTC timezone indicator.
    
    The output format is: YYYY-MM-DDTHH:MM:SSZ (e.g., '2024-01-01T12:00:00Z')
    
    If the conversion fails, returns an error message.

    Args:
        epochSeconds (int): The UTC epoch seconds (timestamp in seconds since 1970-01-01 00:00:00 UTC).
                          This argument is required.
                          Examples: 1704110400, 1609459200

    Returns:
        str: The standard ISO format time string (e.g., '2024-01-01T12:00:00Z').
             Returns an error message string if conversion fails.
    '''
    try:
        # Convert epoch seconds to UTC datetime
        dt_utc = datetime.fromtimestamp(epochSeconds, tz=timezone.utc)
        
        # Format as ISO 8601 standard format with 'Z' suffix for UTC
        iso_string = dt_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        return iso_string
    
    except (ValueError, OSError) as e:
        return f'Error: Invalid epoch seconds value. {str(e)}'
    except Exception as e:
        return f'Error happens in converting UTC epoch seconds to ISO time: {str(e)}'


def convertUTCToLocal(utcISOTimeString: str, localTimeZone: str = None) -> str:
    '''
    Converts a UTC ISO time string to local timezone ISO format (将UTC时间转换为用户本地时区时间).
    If localTimeZone is not provided, uses the system's local timezone.
    
    The output format is: YYYY-MM-DDTHH:MM:SS±HH:MM (e.g., '2024-01-01T20:00:00+08:00' for UTC+8)
    
    If the conversion fails, returns an error message.

    Args:
        utcISOTimeString (str): The UTC ISO format time string to convert (e.g., '2024-01-01T12:00:00Z').
                              This argument is required.
        localTimeZone (str, optional): The local timezone name (e.g., 'Asia/Shanghai', 'America/New_York', 'Europe/London').
                                      If not provided, uses the system's local timezone.
                                      See IANA Time Zone Database for valid timezone names.

    Returns:
        str: The local timezone ISO format time string (e.g., '2024-01-01T20:00:00+08:00').
             Returns an error message string if conversion fails.
    '''
    try:
        # Parse the UTC ISO string
        iso_str = utcISOTimeString.strip().replace('Z', '+00:00')
        dt_utc = datetime.fromisoformat(iso_str)
        
        # Ensure the datetime is UTC timezone-aware
        if dt_utc.tzinfo is None:
            dt_utc = dt_utc.replace(tzinfo=timezone.utc)
        elif dt_utc.tzinfo != timezone.utc:
            # Convert to UTC if it's in a different timezone
            dt_utc = dt_utc.astimezone(timezone.utc)
        
        # Convert to local timezone
        if localTimeZone:
            # Use specified timezone
            if ZoneInfo is None:
                return 'Error: zoneinfo module not available. Please install backports.zoneinfo or use Python 3.9+.'
            
            try:
                local_tz = ZoneInfo(localTimeZone)
            except Exception as e:
                return f'Error: Invalid timezone name "{localTimeZone}". {str(e)}'
        else:
            # Use system's local timezone
            local_tz = datetime.now().astimezone().tzinfo
        
        # Convert UTC to local time
        dt_local = dt_utc.astimezone(local_tz)
        
        # Format as ISO 8601 with timezone offset
        iso_string = dt_local.isoformat()
        
        return iso_string
    
    except ValueError as e:
        return f'Error: Invalid UTC ISO time format. {str(e)}'
    except Exception as e:
        return f'Error happens in converting UTC to local time: {str(e)}'

