"""
Date and time utilities for the Call Analytics application.
"""
from datetime import datetime, timedelta, date
from typing import Tuple, Optional, List, Union
import pandas as pd
import logging

logger = logging.getLogger(__name__)

def get_date_range_options() -> List[Tuple[str, int]]:
    """
    Get predefined date range options.
    
    Returns:
        list: List of (label, days) tuples
    """
    return [
        ("Últimos 7 días", 7),
        ("Últimos 15 días", 15),
        ("Últimos 30 días", 30),
        ("Últimos 60 días", 60),
        ("Últimos 90 días", 90),
        ("Últimos 6 meses", 180),
        ("Último año", 365)
    ]

def get_quick_date_range(days: int) -> Tuple[date, date]:
    """
    Get date range for the last N days.
    
    Args:
        days (int): Number of days to go back
        
    Returns:
        tuple: (start_date, end_date)
    """
    try:
        end_date = date.today()
        start_date = end_date - timedelta(days=days - 1)  # -1 to include today
        
        return start_date, end_date
        
    except Exception as e:
        logger.error(f"Error getting quick date range: {e}")
        return date.today() - timedelta(days=30), date.today()

def get_current_month_range() -> Tuple[date, date]:
    """
    Get date range for the current month.
    
    Returns:
        tuple: (start_date, end_date)
    """
    try:
        today = date.today()
        start_date = today.replace(day=1)
        
        # Get last day of current month
        if today.month == 12:
            next_month = today.replace(year=today.year + 1, month=1, day=1)
        else:
            next_month = today.replace(month=today.month + 1, day=1)
        
        end_date = next_month - timedelta(days=1)
        
        return start_date, end_date
        
    except Exception as e:
        logger.error(f"Error getting current month range: {e}")
        return date.today().replace(day=1), date.today()

def get_previous_month_range() -> Tuple[date, date]:
    """
    Get date range for the previous month.
    
    Returns:
        tuple: (start_date, end_date)
    """
    try:
        today = date.today()
        
        # Get first day of previous month
        if today.month == 1:
            start_date = today.replace(year=today.year - 1, month=12, day=1)
        else:
            start_date = today.replace(month=today.month - 1, day=1)
        
        # Get last day of previous month
        end_date = today.replace(day=1) - timedelta(days=1)
        
        return start_date, end_date
        
    except Exception as e:
        logger.error(f"Error getting previous month range: {e}")
        return date.today() - timedelta(days=30), date.today()

def get_current_week_range() -> Tuple[date, date]:
    """
    Get date range for the current week (Monday to Sunday).
    
    Returns:
        tuple: (start_date, end_date)
    """
    try:
        today = date.today()
        
        # Get Monday of current week
        days_since_monday = today.weekday()
        start_date = today - timedelta(days=days_since_monday)
        
        # Get Sunday of current week
        end_date = start_date + timedelta(days=6)
        
        return start_date, end_date
        
    except Exception as e:
        logger.error(f"Error getting current week range: {e}")
        return date.today() - timedelta(days=7), date.today()

def get_previous_week_range() -> Tuple[date, date]:
    """
    Get date range for the previous week (Monday to Sunday).
    
    Returns:
        tuple: (start_date, end_date)
    """
    try:
        current_week_start, _ = get_current_week_range()
        
        # Previous week ends on Sunday before current week
        end_date = current_week_start - timedelta(days=1)
        
        # Previous week starts on Monday
        start_date = end_date - timedelta(days=6)
        
        return start_date, end_date
        
    except Exception as e:
        logger.error(f"Error getting previous week range: {e}")
        return date.today() - timedelta(days=14), date.today() - timedelta(days=7)

def format_date_for_display(date_obj: Union[date, datetime, str], format_type: str = 'short') -> str:
    """
    Format date for display in the UI.
    
    Args:
        date_obj: Date object to format
        format_type (str): Format type ('short', 'long', 'datetime')
        
    Returns:
        str: Formatted date string
    """
    try:
        # Convert to datetime if needed
        if isinstance(date_obj, str):
            if 'T' in date_obj:
                date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
            else:
                date_obj = datetime.strptime(date_obj, '%Y-%m-%d').date()
        elif isinstance(date_obj, date) and not isinstance(date_obj, datetime):
            date_obj = datetime.combine(date_obj, datetime.min.time())
        
        # Format based on type
        if format_type == 'short':
            return date_obj.strftime('%d/%m/%Y')
        elif format_type == 'long':
            return date_obj.strftime('%d de %B de %Y')
        elif format_type == 'datetime':
            return date_obj.strftime('%d/%m/%Y %H:%M')
        elif format_type == 'time':
            return date_obj.strftime('%H:%M:%S')
        else:
            return date_obj.strftime('%d/%m/%Y')
        
    except Exception as e:
        logger.error(f"Error formatting date: {e}")
        return str(date_obj)

def format_date_range_for_display(start_date: Union[date, datetime, str], 
                                end_date: Union[date, datetime, str]) -> str:
    """
    Format date range for display.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        str: Formatted date range string
    """
    try:
        start_str = format_date_for_display(start_date, 'short')
        end_str = format_date_for_display(end_date, 'short')
        
        return f"{start_str} - {end_str}"
        
    except Exception as e:
        logger.error(f"Error formatting date range: {e}")
        return "Rango de fechas inválido"

def get_business_days_count(start_date: date, end_date: date, 
                          exclude_weekends: bool = True) -> int:
    """
    Count business days between two dates.
    
    Args:
        start_date (date): Start date
        end_date (date): End date
        exclude_weekends (bool): Whether to exclude weekends
        
    Returns:
        int: Number of business days
    """
    try:
        if start_date > end_date:
            return 0
        
        if not exclude_weekends:
            return (end_date - start_date).days + 1
        
        # Count business days (Monday = 0, Sunday = 6)
        business_days = 0
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() < 5:  # Monday to Friday
                business_days += 1
            current_date += timedelta(days=1)
        
        return business_days
        
    except Exception as e:
        logger.error(f"Error counting business days: {e}")
        return 0

def get_time_periods_for_analysis() -> List[Tuple[str, str]]:
    """
    Get predefined time periods for analysis.
    
    Returns:
        list: List of (label, period_code) tuples
    """
    return [
        ("Por Hora", "hourly"),
        ("Por Día", "daily"),
        ("Por Semana", "weekly"),
        ("Por Mes", "monthly"),
        ("Por Trimestre", "quarterly")
    ]

def get_hour_ranges() -> List[Tuple[str, Tuple[int, int]]]:
    """
    Get predefined hour ranges for analysis.
    
    Returns:
        list: List of (label, (start_hour, end_hour)) tuples
    """
    return [
        ("Madrugada (00:00-05:59)", (0, 5)),
        ("Mañana (06:00-11:59)", (6, 11)),
        ("Tarde (12:00-17:59)", (12, 17)),
        ("Noche (18:00-23:59)", (18, 23))
    ]

def categorize_time_of_day(hour: int) -> str:
    """
    Categorize hour into time of day.
    
    Args:
        hour (int): Hour (0-23)
        
    Returns:
        str: Time category
    """
    try:
        if 0 <= hour <= 5:
            return "Madrugada"
        elif 6 <= hour <= 11:
            return "Mañana"
        elif 12 <= hour <= 17:
            return "Tarde"
        elif 18 <= hour <= 23:
            return "Noche"
        else:
            return "Desconocido"
        
    except Exception as e:
        logger.error(f"Error categorizing time of day: {e}")
        return "Desconocido"

def get_weekday_name(weekday: int, lang: str = 'es') -> str:
    """
    Get weekday name in specified language.
    
    Args:
        weekday (int): Weekday number (0=Monday, 6=Sunday)
        lang (str): Language code ('es' or 'en')
        
    Returns:
        str: Weekday name
    """
    try:
        if lang == 'es':
            weekdays = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        else:
            weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        if 0 <= weekday <= 6:
            return weekdays[weekday]
        else:
            return "Desconocido" if lang == 'es' else "Unknown"
        
    except Exception as e:
        logger.error(f"Error getting weekday name: {e}")
        return "Desconocido" if lang == 'es' else "Unknown"

def get_month_name(month: int, lang: str = 'es') -> str:
    """
    Get month name in specified language.
    
    Args:
        month (int): Month number (1-12)
        lang (str): Language code ('es' or 'en')
        
    Returns:
        str: Month name
    """
    try:
        if lang == 'es':
            months = [
                'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
            ]
        else:
            months = [
                'January', 'February', 'March', 'April', 'May', 'June',
                'July', 'August', 'September', 'October', 'November', 'December'
            ]
        
        if 1 <= month <= 12:
            return months[month - 1]
        else:
            return "Desconocido" if lang == 'es' else "Unknown"
        
    except Exception as e:
        logger.error(f"Error getting month name: {e}")
        return "Desconocido" if lang == 'es' else "Unknown"

def parse_date_string(date_string: str, formats: Optional[List[str]] = None) -> Optional[datetime]:
    """
    Parse date string with multiple format attempts.
    
    Args:
        date_string (str): Date string to parse
        formats (list, optional): List of formats to try
        
    Returns:
        datetime or None: Parsed datetime or None if parsing fails
    """
    try:
        if not formats:
            formats = [
                '%Y-%m-%d',
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%d/%m/%Y',
                '%d/%m/%Y %H:%M:%S',
                '%d-%m-%Y',
                '%d-%m-%Y %H:%M:%S'
            ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_string, fmt)
            except ValueError:
                continue
        
        # Try pandas parsing as last resort
        try:
            return pd.to_datetime(date_string)
        except:
            pass
        
        logger.warning(f"Could not parse date string: {date_string}")
        return None
        
    except Exception as e:
        logger.error(f"Error parsing date string: {e}")
        return None

def get_relative_time_description(date_obj: Union[date, datetime], lang: str = 'es') -> str:
    """
    Get relative time description (e.g., "hace 2 días").
    
    Args:
        date_obj: Date object
        lang (str): Language code ('es' or 'en')
        
    Returns:
        str: Relative time description
    """
    try:
        if isinstance(date_obj, date) and not isinstance(date_obj, datetime):
            date_obj = datetime.combine(date_obj, datetime.min.time())
        
        now = datetime.now()
        diff = now - date_obj
        
        if lang == 'es':
            if diff.days == 0:
                if diff.seconds < 3600:
                    minutes = diff.seconds // 60
                    return f"hace {minutes} minuto{'s' if minutes != 1 else ''}"
                else:
                    hours = diff.seconds // 3600
                    return f"hace {hours} hora{'s' if hours != 1 else ''}"
            elif diff.days == 1:
                return "ayer"
            elif diff.days < 7:
                return f"hace {diff.days} días"
            elif diff.days < 30:
                weeks = diff.days // 7
                return f"hace {weeks} semana{'s' if weeks != 1 else ''}"
            elif diff.days < 365:
                months = diff.days // 30
                return f"hace {months} mes{'es' if months != 1 else ''}"
            else:
                years = diff.days // 365
                return f"hace {years} año{'s' if years != 1 else ''}"
        else:
            if diff.days == 0:
                if diff.seconds < 3600:
                    minutes = diff.seconds // 60
                    return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
                else:
                    hours = diff.seconds // 3600
                    return f"{hours} hour{'s' if hours != 1 else ''} ago"
            elif diff.days == 1:
                return "yesterday"
            elif diff.days < 7:
                return f"{diff.days} days ago"
            elif diff.days < 30:
                weeks = diff.days // 7
                return f"{weeks} week{'s' if weeks != 1 else ''} ago"
            elif diff.days < 365:
                months = diff.days // 30
                return f"{months} month{'s' if months != 1 else ''} ago"
            else:
                years = diff.days // 365
                return f"{years} year{'s' if years != 1 else ''} ago"
        
    except Exception as e:
        logger.error(f"Error getting relative time description: {e}")
        return "Desconocido" if lang == 'es' else "Unknown"

def validate_date_range(start_date: Union[date, datetime, str], 
                       end_date: Union[date, datetime, str]) -> Tuple[bool, str]:
    """
    Validate date range.
    
    Args:
        start_date: Start date
        end_date: End date
        
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        # Convert to date objects if needed
        if isinstance(start_date, str):
            start_date = parse_date_string(start_date)
            if start_date is None:
                return False, "Fecha de inicio inválida"
            start_date = start_date.date()
        elif isinstance(start_date, datetime):
            start_date = start_date.date()
        
        if isinstance(end_date, str):
            end_date = parse_date_string(end_date)
            if end_date is None:
                return False, "Fecha de fin inválida"
            end_date = end_date.date()
        elif isinstance(end_date, datetime):
            end_date = end_date.date()
        
        # Validate range
        if start_date > end_date:
            return False, "La fecha de inicio debe ser anterior a la fecha de fin"
        
        # Check if range is too large (more than 2 years)
        if (end_date - start_date).days > 730:
            return False, "El rango de fechas no puede ser mayor a 2 años"
        
        # Check if dates are in the future
        today = date.today()
        if start_date > today:
            return False, "La fecha de inicio no puede ser futura"
        
        if end_date > today:
            return False, "La fecha de fin no puede ser futura"
        
        return True, ""
        
    except Exception as e:
        logger.error(f"Error validating date range: {e}")
        return False, "Error validando rango de fechas"