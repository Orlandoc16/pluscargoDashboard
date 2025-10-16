"""
Export utilities for the Call Analytics application.
"""
import pandas as pd
import io
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

def auto_adjust_columns(worksheet):
    """Auto-adjust column widths in Excel worksheet."""
    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
        
        adjusted_width = min(max_length + 2, 50)
        worksheet.column_dimensions[column_letter].width = adjusted_width

def export_to_excel(data, sheet_name: str = "Data", filename: Optional[str] = None) -> bytes:
    """
    Export DataFrame to Excel format.
    
    Args:
        data: DataFrame or dict with DataFrames to export
        sheet_name (str): Name for the Excel sheet
        filename (str, optional): Filename for the export
        
    Returns:
        bytes: Excel file content
    """
    try:
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if isinstance(data, dict):
                # Multiple sheets
                for name, df in data.items():
                    if not df.empty:
                        clean_name = clean_sheet_name_for_excel(name)
                        df.to_excel(writer, sheet_name=clean_name, index=False)
                        auto_adjust_columns(writer.sheets[clean_name])
            else:
                # Single DataFrame
                if not data.empty:
                    clean_name = clean_sheet_name_for_excel(sheet_name)
                    data.to_excel(writer, sheet_name=clean_name, index=False)
                    auto_adjust_columns(writer.sheets[clean_name])
        
        output.seek(0)
        logger.info(f"Exported data to Excel")
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Error exporting to Excel: {e}")
        raise

def export_to_csv(df: pd.DataFrame, filename: Optional[str] = None) -> str:
    """
    Export DataFrame to CSV format.
    
    Args:
        df (pd.DataFrame): Data to export
        filename (str, optional): Filename for the export
        
    Returns:
        str: CSV content
    """
    try:
        if df.empty:
            return "No data available for export"
        
        # Clean data for CSV export
        export_df = df.copy()
        
        # Convert datetime columns to string
        for col in export_df.columns:
            if export_df[col].dtype == 'datetime64[ns]':
                export_df[col] = export_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        csv_content = export_df.to_csv(index=False, encoding='utf-8')
        
        logger.info(f"Exported {len(df)} rows to CSV")
        return csv_content
        
    except Exception as e:
        logger.error(f"Error exporting to CSV: {e}")
        raise

def export_to_json(data: Any, filename: Optional[str] = None, pretty: bool = True) -> str:
    """
    Export data to JSON format.
    
    Args:
        data: Data to export
        filename (str, optional): Filename for the export
        pretty (bool): Whether to format JSON prettily
        
    Returns:
        str: JSON content
    """
    try:
        if pretty:
            json_content = json.dumps(data, indent=2, ensure_ascii=False, default=str)
        else:
            json_content = json.dumps(data, ensure_ascii=False, default=str)
        
        logger.info("Exported data to JSON")
        return json_content
        
    except Exception as e:
        logger.error(f"Error exporting to JSON: {e}")
        raise

def clean_sheet_name_for_excel(name: str) -> str:
    """
    Clean sheet name for Excel compatibility.
    
    Args:
        name (str): Original sheet name
        
    Returns:
        str: Cleaned sheet name
    """
    # Excel sheet name restrictions
    invalid_chars = ['\\', '/', '*', '[', ']', ':', '?']
    clean_name = name
    
    for char in invalid_chars:
        clean_name = clean_name.replace(char, '_')
    
    # Limit length to 31 characters
    if len(clean_name) > 31:
        clean_name = clean_name[:31]
    
    return clean_name

def prepare_data_for_export(data: List[Dict], export_format: str = 'csv') -> pd.DataFrame:
    """
    Prepare data for export by converting to DataFrame and cleaning.
    
    Args:
        data (list): List of dictionaries with data
        export_format (str): Export format ('csv', 'excel', 'json')
        
    Returns:
        pd.DataFrame: Cleaned DataFrame ready for export
    """
    try:
        if not data:
            return pd.DataFrame()
        
        df = pd.DataFrame(data)
        
        # Clean data based on export format
        if export_format.lower() in ['csv', 'excel']:
            # Convert datetime columns
            for col in df.columns:
                if df[col].dtype == 'object':
                    # Try to convert datetime strings
                    try:
                        df[col] = pd.to_datetime(df[col], errors='ignore')
                    except:
                        pass
                
                # Handle None/NaN values
                df[col] = df[col].fillna('')
        
        logger.info(f"Prepared {len(df)} rows for {export_format} export")
        return df
        
    except Exception as e:
        logger.error(f"Error preparing data for export: {e}")
        return pd.DataFrame()

def get_export_summary(data: pd.DataFrame, export_type: str) -> Dict[str, Any]:
    """
    Generate export summary information.
    
    Args:
        data (pd.DataFrame): Exported data
        export_type (str): Type of export
        
    Returns:
        dict: Export summary
    """
    try:
        summary = {
            'export_type': export_type,
            'total_rows': len(data),
            'total_columns': len(data.columns) if not data.empty else 0,
            'columns': list(data.columns) if not data.empty else [],
            'export_timestamp': datetime.now().isoformat(),
            'file_size_estimate': f"{len(str(data)) / 1024:.2f} KB" if not data.empty else "0 KB"
        }
        
        return summary
        
    except Exception as e:
        logger.error(f"Error generating export summary: {e}")
        return {
            'export_type': export_type,
            'error': str(e),
            'export_timestamp': datetime.now().isoformat()
        }

def validate_export_data(data: Any) -> bool:
    """
    Validate data before export.
    
    Args:
        data: Data to validate
        
    Returns:
        bool: True if data is valid for export
    """
    try:
        if data is None:
            return False
        
        if isinstance(data, pd.DataFrame):
            return not data.empty
        
        if isinstance(data, (list, dict)):
            return len(data) > 0
        
        return True
        
    except Exception as e:
        logger.error(f"Error validating export data: {e}")
        return False

def generate_export_filename(base_name: str, export_format: str, date_range: Optional[tuple] = None) -> str:
    """
    Generate a standardized filename for exports.
    
    Args:
        base_name (str): Base name for the file
        export_format (str): File format extension
        date_range (tuple, optional): Date range for the export
        
    Returns:
        str: Generated filename
    """
    try:
        # Clean base name
        clean_base = base_name.lower().replace(' ', '_').replace('-', '_')
        
        # Add date range if provided
        if date_range:
            start_date = date_range[0] if isinstance(date_range[0], str) else date_range[0].strftime('%Y%m%d')
            end_date = date_range[1] if isinstance(date_range[1], str) else date_range[1].strftime('%Y%m%d')
            clean_base += f"_{start_date}_to_{end_date}"
        else:
            # Add current date
            clean_base += f"_{datetime.now().strftime('%Y%m%d')}"
        
        # Add timestamp
        timestamp = datetime.now().strftime('%H%M%S')
        
        # Construct filename
        filename = f"{clean_base}_{timestamp}.{export_format.lower()}"
        
        return filename
        
    except Exception as e:
        logger.error(f"Error generating filename: {e}")
        return f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format.lower()}"