"""
Data formatting utilities for the Call Analytics application.
"""
from typing import Any, Optional, Union, Dict, List
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import logging

logger = logging.getLogger(__name__)

def get_locale() -> str:
    """Get current locale from session state."""
    return st.session_state.get('language', 'es')

def format_number(value: Union[int, float, str], 
                 decimal_places: int = 0, 
                 use_thousands_separator: bool = True,
                 locale: Optional[str] = None) -> str:
    """
    Format number for display with locale support.
    
    Args:
        value: Number to format
        decimal_places (int): Number of decimal places
        use_thousands_separator (bool): Whether to use thousands separator
        locale (str): Locale for formatting ('es' or 'en')
        
    Returns:
        str: Formatted number string
    """
    try:
        if pd.isna(value) or value is None:
            return "0"
        
        if locale is None:
            locale = get_locale()
        
        # Convert to float
        if isinstance(value, str):
            try:
                value = float(value)
            except ValueError:
                return str(value)
        
        # Format number based on locale
        if locale == 'es':
            # Spanish format: 1.234.567,89
            if use_thousands_separator:
                if decimal_places == 0:
                    return f"{value:,.0f}".replace(",", ".")
                else:
                    return f"{value:,.{decimal_places}f}".replace(",", "X").replace(".", ",").replace("X", ".")
            else:
                if decimal_places == 0:
                    return f"{value:.0f}"
                else:
                    return f"{value:.{decimal_places}f}".replace(".", ",")
        else:
            # English format: 1,234,567.89
            if use_thousands_separator:
                return f"{value:,.{decimal_places}f}"
            else:
                return f"{value:.{decimal_places}f}"
        
    except Exception as e:
        logger.error(f"Error formatting number: {e}")
        return str(value)

def format_percentage(value: Union[int, float, str], 
                     decimal_places: int = 1,
                     locale: Optional[str] = None) -> str:
    """
    Format percentage for display with locale support.
    
    Args:
        value: Percentage value (0-100 or 0-1)
        decimal_places (int): Number of decimal places
        locale (str): Locale for formatting ('es' or 'en')
        
    Returns:
        str: Formatted percentage string
    """
    try:
        if pd.isna(value) or value is None:
            return "0,0%" if (locale or get_locale()) == 'es' else "0.0%"
        
        if locale is None:
            locale = get_locale()
        
        # Convert to float
        if isinstance(value, str):
            try:
                value = float(value.replace("%", "").replace(",", "."))
            except ValueError:
                return str(value)
        
        # Assume values > 1 are already percentages, values <= 1 need to be multiplied by 100
        if value <= 1:
            value = value * 100
        
        if locale == 'es':
            return f"{value:.{decimal_places}f}%".replace(".", ",")
        else:
            return f"{value:.{decimal_places}f}%"
        
    except Exception as e:
        logger.error(f"Error formatting percentage: {e}")
        return str(value)

def format_currency(value: Union[int, float, str], 
                   currency: str = "COP", 
                   decimal_places: int = 0,
                   locale: Optional[str] = None) -> str:
    """
    Format currency for display with locale support.
    
    Args:
        value: Currency value
        currency (str): Currency code
        decimal_places (int): Number of decimal places
        locale (str): Locale for formatting ('es' or 'en')
        
    Returns:
        str: Formatted currency string
    """
    try:
        if pd.isna(value) or value is None:
            return f"${format_number(0, decimal_places, locale=locale)} {currency}"
        
        if locale is None:
            locale = get_locale()
        
        # Convert to float
        if isinstance(value, str):
            try:
                value = float(value.replace("$", "").replace(",", "").replace(".", ""))
            except ValueError:
                return str(value)
        
        formatted_value = format_number(value, decimal_places, locale=locale)
        
        if locale == 'es':
            return f"${formatted_value} {currency}"
        else:
            return f"{currency} ${formatted_value}"
        
    except Exception as e:
        logger.error(f"Error formatting currency: {e}")
        return str(value)

def format_date(date_value: Union[datetime, str, pd.Timestamp], 
               format_type: str = 'short',
               locale: Optional[str] = None) -> str:
    """
    Format date for display with locale support.
    
    Args:
        date_value: Date to format
        format_type (str): Format type ('short', 'medium', 'long', 'full')
        locale (str): Locale for formatting ('es' or 'en')
        
    Returns:
        str: Formatted date string
    """
    try:
        if pd.isna(date_value) or date_value is None:
            return ""
        
        if locale is None:
            locale = get_locale()
        
        # Convert to datetime
        if isinstance(date_value, str):
            try:
                date_value = pd.to_datetime(date_value)
            except ValueError:
                return str(date_value)
        elif isinstance(date_value, pd.Timestamp):
            date_value = date_value.to_pydatetime()
        
        # Format based on locale and type
        if locale == 'es':
            if format_type == 'short':
                return date_value.strftime("%d/%m/%Y")
            elif format_type == 'medium':
                return date_value.strftime("%d %b %Y")
            elif format_type == 'long':
                months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                         'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
                return f"{date_value.day} de {months[date_value.month-1]} de {date_value.year}"
            elif format_type == 'full':
                days = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
                months = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                         'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
                weekday = days[date_value.weekday()]
                return f"{weekday}, {date_value.day} de {months[date_value.month-1]} de {date_value.year}"
        else:
            if format_type == 'short':
                return date_value.strftime("%m/%d/%Y")
            elif format_type == 'medium':
                return date_value.strftime("%b %d, %Y")
            elif format_type == 'long':
                return date_value.strftime("%B %d, %Y")
            elif format_type == 'full':
                return date_value.strftime("%A, %B %d, %Y")
        
        return date_value.strftime("%Y-%m-%d")
        
    except Exception as e:
        logger.error(f"Error formatting date: {e}")
        return str(date_value)

def format_datetime(datetime_value: Union[datetime, str, pd.Timestamp],
                   format_type: str = 'short',
                   locale: Optional[str] = None) -> str:
    """
    Format datetime for display with locale support.
    
    Args:
        datetime_value: Datetime to format
        format_type (str): Format type ('short', 'medium', 'long')
        locale (str): Locale for formatting ('es' or 'en')
        
    Returns:
        str: Formatted datetime string
    """
    try:
        if pd.isna(datetime_value) or datetime_value is None:
            return ""
        
        if locale is None:
            locale = get_locale()
        
        # Convert to datetime
        if isinstance(datetime_value, str):
            try:
                datetime_value = pd.to_datetime(datetime_value)
            except ValueError:
                return str(datetime_value)
        elif isinstance(datetime_value, pd.Timestamp):
            datetime_value = datetime_value.to_pydatetime()
        
        # Format based on locale and type
        if locale == 'es':
            if format_type == 'short':
                return datetime_value.strftime("%d/%m/%Y %H:%M")
            elif format_type == 'medium':
                return datetime_value.strftime("%d %b %Y %H:%M:%S")
            elif format_type == 'long':
                return datetime_value.strftime("%d de %B de %Y a las %H:%M:%S")
        else:
            if format_type == 'short':
                return datetime_value.strftime("%m/%d/%Y %H:%M")
            elif format_type == 'medium':
                return datetime_value.strftime("%b %d, %Y %H:%M:%S")
            elif format_type == 'long':
                return datetime_value.strftime("%B %d, %Y at %H:%M:%S")
        
        return datetime_value.strftime("%Y-%m-%d %H:%M:%S")
        
    except Exception as e:
        logger.error(f"Error formatting datetime: {e}")
        return str(datetime_value)

def format_duration(seconds: Union[int, float, str], 
                   format_type: str = 'hms') -> str:
    """
    Format duration for display.
    
    Args:
        seconds: Duration in seconds
        format_type (str): Format type ('hms', 'ms', 'compact')
        
    Returns:
        str: Formatted duration string
    """
    try:
        if pd.isna(seconds) or seconds is None:
            return "00:00:00" if format_type == 'hms' else "0s"
        
        # Convert to int
        if isinstance(seconds, str):
            try:
                seconds = float(seconds)
            except ValueError:
                return str(seconds)
        
        seconds = int(seconds)
        
        if format_type == 'hms':
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            secs = seconds % 60
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        
        elif format_type == 'ms':
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes:02d}:{secs:02d}"
        
        elif format_type == 'compact':
            if seconds < 60:
                return f"{seconds}s"
            elif seconds < 3600:
                minutes = seconds // 60
                return f"{minutes}m"
            else:
                hours = seconds // 3600
                minutes = (seconds % 3600) // 60
                if minutes > 0:
                    return f"{hours}h {minutes}m"
                else:
                    return f"{hours}h"
        
        else:
            return str(seconds)
        
    except Exception as e:
        logger.error(f"Error formatting duration: {e}")
        return str(seconds)

def format_phone_number(phone: str) -> str:
    """
    Format phone number for display.
    
    Args:
        phone (str): Phone number
        
    Returns:
        str: Formatted phone number
    """
    try:
        if not phone or pd.isna(phone):
            return ""
        
        # Remove all non-digit characters
        digits = ''.join(filter(str.isdigit, str(phone)))
        
        if len(digits) == 10:
            # Colombian mobile format: 3XX XXX XXXX
            return f"{digits[:3]} {digits[3:6]} {digits[6:]}"
        elif len(digits) == 7:
            # Local format: XXX XXXX
            return f"{digits[:3]} {digits[3:]}"
        elif len(digits) == 12 and digits.startswith('57'):
            # International format: +57 3XX XXX XXXX
            return f"+57 {digits[2:5]} {digits[5:8]} {digits[8:]}"
        else:
            return phone
        
    except Exception as e:
        logger.error(f"Error formatting phone number: {e}")
        return str(phone)

def format_call_result(result: str, locale: Optional[str] = None) -> str:
    """
    Format call result for display with locale support.
    
    Args:
        result (str): Call result code
        locale (str): Locale for formatting ('es' or 'en')
        
    Returns:
        str: Formatted call result
    """
    try:
        if not result or pd.isna(result):
            if locale is None:
                locale = get_locale()
            return "Sin resultado" if locale == 'es' else "No result"
        
        if locale is None:
            locale = get_locale()
        
        if locale == 'es':
            result_mapping = {
                'answered': 'Contestada',
                'no_answer': 'No contestó',
                'busy': 'Ocupado',
                'failed': 'Falló',
                'voicemail': 'Buzón de voz',
                'rejected': 'Rechazada',
                'cancelled': 'Cancelada',
                'interested': 'Interesado',
                'not_interested': 'No interesado',
                'callback': 'Llamar después',
                'wrong_number': 'Número equivocado',
                'converted': 'Convertido',
                'qualified': 'Calificado',
                'unqualified': 'No calificado'
            }
        else:
            result_mapping = {
                'answered': 'Answered',
                'no_answer': 'No Answer',
                'busy': 'Busy',
                'failed': 'Failed',
                'voicemail': 'Voicemail',
                'rejected': 'Rejected',
                'cancelled': 'Cancelled',
                'interested': 'Interested',
                'not_interested': 'Not Interested',
                'callback': 'Callback',
                'wrong_number': 'Wrong Number',
                'converted': 'Converted',
                'qualified': 'Qualified',
                'unqualified': 'Unqualified'
            }
        
        return result_mapping.get(str(result).lower(), str(result).title())
        
    except Exception as e:
        logger.error(f"Error formatting call result: {e}")
        return str(result)

def format_agent_name(name: str, locale: Optional[str] = None) -> str:
    """
    Format agent name for display with locale support.
    
    Args:
        name (str): Agent name
        locale (str): Locale for formatting ('es' or 'en')
        
    Returns:
        str: Formatted agent name
    """
    try:
        if not name or pd.isna(name):
            if locale is None:
                locale = get_locale()
            return "Agente Desconocido" if locale == 'es' else "Unknown Agent"
        
        # Capitalize each word
        return str(name).title()
        
    except Exception as e:
        logger.error(f"Error formatting agent name: {e}")
        return str(name)

def format_lead_source(source: str, locale: Optional[str] = None) -> str:
    """
    Format lead source for display with locale support.
    
    Args:
        source (str): Lead source
        locale (str): Locale for formatting ('es' or 'en')
        
    Returns:
        str: Formatted lead source
    """
    try:
        if not source or pd.isna(source):
            if locale is None:
                locale = get_locale()
            return "Fuente Desconocida" if locale == 'es' else "Unknown Source"
        
        if locale is None:
            locale = get_locale()
        
        if locale == 'es':
            source_mapping = {
                'web': 'Sitio Web',
                'facebook': 'Facebook',
                'google': 'Google Ads',
                'referral': 'Referido',
                'direct': 'Directo',
                'email': 'Email Marketing',
                'sms': 'SMS Marketing',
                'cold_call': 'Llamada en Frío',
                'organic': 'Búsqueda Orgánica',
                'social': 'Redes Sociales',
                'other': 'Otro'
            }
        else:
            source_mapping = {
                'web': 'Website',
                'facebook': 'Facebook',
                'google': 'Google Ads',
                'referral': 'Referral',
                'direct': 'Direct',
                'email': 'Email Marketing',
                'sms': 'SMS Marketing',
                'cold_call': 'Cold Call',
                'organic': 'Organic Search',
                'social': 'Social Media',
                'other': 'Other'
            }
        
        return source_mapping.get(str(source).lower(), str(source).title())
        
    except Exception as e:
        logger.error(f"Error formatting lead source: {e}")
        return str(source)

def format_table_data(df: pd.DataFrame, 
                     column_formats: Optional[Dict[str, str]] = None) -> pd.DataFrame:
    """
    Format DataFrame for table display.
    
    Args:
        df (pd.DataFrame): DataFrame to format
        column_formats (dict, optional): Column format specifications
        
    Returns:
        pd.DataFrame: Formatted DataFrame
    """
    try:
        if df.empty:
            return df
        
        formatted_df = df.copy()
        
        # Default column formats
        default_formats = {
            'duration': 'duration',
            'phone': 'phone',
            'result': 'call_result',
            'agent': 'agent_name',
            'source': 'lead_source',
            'created_at': 'datetime',
            'updated_at': 'datetime',
            'call_date': 'date'
        }
        
        # Merge with provided formats
        if column_formats:
            default_formats.update(column_formats)
        
        # Apply formatting to each column
        for col in formatted_df.columns:
            col_lower = col.lower()
            format_type = None
            
            # Find format type
            for key, fmt in default_formats.items():
                if key in col_lower:
                    format_type = fmt
                    break
            
            if format_type and col in formatted_df.columns:
                if format_type == 'duration':
                    formatted_df[col] = formatted_df[col].apply(
                        lambda x: format_duration(x, 'ms') if pd.notna(x) else ""
                    )
                elif format_type == 'phone':
                    formatted_df[col] = formatted_df[col].apply(format_phone_number)
                elif format_type == 'call_result':
                    formatted_df[col] = formatted_df[col].apply(format_call_result)
                elif format_type == 'agent_name':
                    formatted_df[col] = formatted_df[col].apply(format_agent_name)
                elif format_type == 'lead_source':
                    formatted_df[col] = formatted_df[col].apply(format_lead_source)
                elif format_type == 'datetime':
                    formatted_df[col] = pd.to_datetime(formatted_df[col], errors='coerce').dt.strftime('%d/%m/%Y %H:%M')
                elif format_type == 'date':
                    formatted_df[col] = pd.to_datetime(formatted_df[col], errors='coerce').dt.strftime('%d/%m/%Y')
                elif format_type == 'percentage':
                    formatted_df[col] = formatted_df[col].apply(lambda x: format_percentage(x) if pd.notna(x) else "")
                elif format_type == 'currency':
                    formatted_df[col] = formatted_df[col].apply(lambda x: format_currency(x) if pd.notna(x) else "")
                elif format_type == 'number':
                    formatted_df[col] = formatted_df[col].apply(lambda x: format_number(x) if pd.notna(x) else "")
        
        return formatted_df
        
    except Exception as e:
        logger.error(f"Error formatting table data: {e}")
        return df

def format_metric_value(value: Any, metric_type: str) -> str:
    """
    Format metric value based on type.
    
    Args:
        value: Metric value
        metric_type (str): Type of metric
        
    Returns:
        str: Formatted metric value
    """
    try:
        if pd.isna(value) or value is None:
            return "0"
        
        if metric_type == 'count':
            return format_number(value, 0)
        elif metric_type == 'percentage':
            return format_percentage(value)
        elif metric_type == 'duration':
            return format_duration(value, 'compact')
        elif metric_type == 'currency':
            return format_currency(value)
        elif metric_type == 'rate':
            return format_percentage(value)
        elif metric_type == 'average':
            return format_number(value, 1)
        else:
            return format_number(value, 0)
        
    except Exception as e:
        logger.error(f"Error formatting metric value: {e}")
        return str(value)

def format_chart_label(label: str, max_length: int = 20) -> str:
    """
    Format chart label with truncation if needed.
    
    Args:
        label (str): Label to format
        max_length (int): Maximum length
        
    Returns:
        str: Formatted label
    """
    try:
        if not label or pd.isna(label):
            return ""
        
        label = str(label)
        
        if len(label) <= max_length:
            return label
        else:
            return label[:max_length-3] + "..."
        
    except Exception as e:
        logger.error(f"Error formatting chart label: {e}")
        return str(label)

def format_tooltip_text(data: Dict[str, Any]) -> str:
    """
    Format tooltip text for charts.
    
    Args:
        data (dict): Data for tooltip
        
    Returns:
        str: Formatted tooltip text
    """
    try:
        lines = []
        
        for key, value in data.items():
            if pd.isna(value) or value is None:
                continue
            
            # Format key
            formatted_key = key.replace('_', ' ').title()
            
            # Format value based on key
            if 'percentage' in key.lower() or 'rate' in key.lower():
                formatted_value = format_percentage(value)
            elif 'duration' in key.lower() or 'time' in key.lower():
                formatted_value = format_duration(value, 'compact')
            elif 'count' in key.lower() or 'total' in key.lower():
                formatted_value = format_number(value, 0)
            elif 'currency' in key.lower() or 'amount' in key.lower():
                formatted_value = format_currency(value)
            else:
                formatted_value = str(value)
            
            lines.append(f"{formatted_key}: {formatted_value}")
        
        return "<br>".join(lines)
        
    except Exception as e:
        logger.error(f"Error formatting tooltip text: {e}")
        return str(data)

def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean column names for better display.
    
    Args:
        df (pd.DataFrame): DataFrame with columns to clean
        
    Returns:
        pd.DataFrame: DataFrame with cleaned column names
    """
    try:
        cleaned_df = df.copy()
        
        # Column name mapping
        column_mapping = {
            'id': 'ID',
            'created_at': 'Fecha Creación',
            'updated_at': 'Fecha Actualización',
            'call_date': 'Fecha Llamada',
            'phone': 'Teléfono',
            'duration': 'Duración',
            'result': 'Resultado',
            'agent_id': 'ID Agente',
            'agent_name': 'Agente',
            'lead_id': 'ID Lead',
            'lead_name': 'Nombre Lead',
            'lead_source': 'Fuente Lead',
            'conversion_rate': 'Tasa Conversión',
            'total_calls': 'Total Llamadas',
            'successful_calls': 'Llamadas Exitosas',
            'average_duration': 'Duración Promedio',
            'total_duration': 'Duración Total',
            'first_call': 'Primera Llamada',
            'last_call': 'Última Llamada',
            'status': 'Estado',
            'notes': 'Notas',
            'email': 'Email',
            'company': 'Empresa',
            'position': 'Cargo'
        }
        
        # Rename columns
        new_columns = {}
        for col in cleaned_df.columns:
            col_lower = col.lower()
            if col_lower in column_mapping:
                new_columns[col] = column_mapping[col_lower]
            else:
                # Clean column name
                clean_name = col.replace('_', ' ').title()
                new_columns[col] = clean_name
        
        cleaned_df.rename(columns=new_columns, inplace=True)
        
        return cleaned_df
        
    except Exception as e:
        logger.error(f"Error cleaning column names: {e}")
        return df

def format_export_filename(base_name: str, 
                          date_range: Optional[tuple] = None,
                          extension: str = 'xlsx') -> str:
    """
    Format filename for exports.
    
    Args:
        base_name (str): Base filename
        date_range (tuple, optional): Date range tuple
        extension (str): File extension
        
    Returns:
        str: Formatted filename
    """
    try:
        # Clean base name
        clean_base = base_name.lower().replace(' ', '_').replace('-', '_')
        
        # Add timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Add date range if provided
        if date_range:
            start_date, end_date = date_range
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            date_str = f"{start_date.strftime('%Y%m%d')}_{end_date.strftime('%Y%m%d')}"
            filename = f"{clean_base}_{date_str}_{timestamp}.{extension}"
        else:
            filename = f"{clean_base}_{timestamp}.{extension}"
        
        return filename
        
    except Exception as e:
        logger.error(f"Error formatting export filename: {e}")
        return f"{base_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{extension}"