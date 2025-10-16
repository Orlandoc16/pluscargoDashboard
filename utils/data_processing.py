"""
Data processing utilities for the Call Analytics application.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import logging

logger = logging.getLogger(__name__)

def clean_call_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize call data.
    
    Args:
        df (pd.DataFrame): Raw call data
        
    Returns:
        pd.DataFrame: Cleaned call data
    """
    try:
        if df.empty:
            return df
        
        # Make a copy to avoid modifying original
        cleaned_df = df.copy()
        
        # Convert date columns
        date_columns = ['call_date', 'created_at', 'updated_at']
        for col in date_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_datetime(cleaned_df[col], errors='coerce')
        
        # Clean duration data
        if 'duration' in cleaned_df.columns:
            cleaned_df['duration_minutes'] = pd.to_numeric(cleaned_df['duration'], errors='coerce') / 60
            cleaned_df['duration_minutes'] = cleaned_df['duration_minutes'].fillna(0)
        
        # Standardize call status
        if 'call_status' in cleaned_df.columns:
            status_mapping = {
                'success': 'completed',
                'successful': 'completed',
                'complete': 'completed',
                'fail': 'failed',
                'failure': 'failed',
                'error': 'failed',
                'timeout': 'failed',
                'busy': 'busy',
                'no-answer': 'no_answer',
                'no_answer': 'no_answer',
                'cancelled': 'cancelled',
                'cancel': 'cancelled'
            }
            cleaned_df['call_status'] = cleaned_df['call_status'].str.lower().replace(status_mapping)
        
        # Clean phone numbers
        if 'phone' in cleaned_df.columns:
            cleaned_df['phone'] = cleaned_df['phone'].astype(str).str.replace(r'[^\d+]', '', regex=True)
        
        # Remove duplicates based on key columns
        key_columns = ['phone', 'call_date', 'agent_id']
        existing_columns = [col for col in key_columns if col in cleaned_df.columns]
        if existing_columns:
            cleaned_df = cleaned_df.drop_duplicates(subset=existing_columns, keep='last')
        
        # Sort by date
        if 'call_date' in cleaned_df.columns:
            cleaned_df = cleaned_df.sort_values('call_date', ascending=False)
        
        logger.info(f"Cleaned call data: {len(df)} -> {len(cleaned_df)} records")
        return cleaned_df
        
    except Exception as e:
        logger.error(f"Error cleaning call data: {e}")
        return df

def clean_agent_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean and standardize agent data.
    
    Args:
        df (pd.DataFrame): Raw agent data
        
    Returns:
        pd.DataFrame: Cleaned agent data
    """
    try:
        if df.empty:
            return df
        
        cleaned_df = df.copy()
        
        # Clean agent names
        if 'name' in cleaned_df.columns:
            cleaned_df['name'] = cleaned_df['name'].str.strip().str.title()
        
        # Ensure numeric columns
        numeric_columns = ['total_calls', 'successful_calls', 'conversion_rate', 'avg_duration']
        for col in numeric_columns:
            if col in cleaned_df.columns:
                cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce').fillna(0)
        
        # Calculate missing metrics
        if 'total_calls' in cleaned_df.columns and 'successful_calls' in cleaned_df.columns:
            if 'conversion_rate' not in cleaned_df.columns:
                cleaned_df['conversion_rate'] = (
                    cleaned_df['successful_calls'] / cleaned_df['total_calls'] * 100
                ).fillna(0).round(2)
        
        # Remove inactive agents (no calls)
        if 'total_calls' in cleaned_df.columns:
            cleaned_df = cleaned_df[cleaned_df['total_calls'] > 0]
        
        logger.info(f"Cleaned agent data: {len(df)} -> {len(cleaned_df)} records")
        return cleaned_df
        
    except Exception as e:
        logger.error(f"Error cleaning agent data: {e}")
        return df

def calculate_metrics(df: pd.DataFrame, date_range: Optional[Tuple[str, str]] = None) -> Dict[str, Any]:
    """
    Calculate key metrics from call data.
    
    Args:
        df (pd.DataFrame): Call data
        date_range (tuple, optional): Date range filter
        
    Returns:
        dict: Calculated metrics
    """
    try:
        if df.empty:
            return get_empty_metrics()
        
        # Filter by date range if provided
        if date_range and 'call_date' in df.columns:
            start_date, end_date = date_range
            df = df[
                (df['call_date'] >= start_date) & 
                (df['call_date'] <= end_date)
            ]
        
        total_calls = len(df)
        
        if total_calls == 0:
            return get_empty_metrics()
        
        # Basic metrics
        successful_calls = len(df[df['call_status'] == 'completed']) if 'call_status' in df.columns else 0
        conversion_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
        
        # Duration metrics
        avg_duration = df['duration_minutes'].mean() if 'duration_minutes' in df.columns else 0
        total_duration = df['duration_minutes'].sum() if 'duration_minutes' in df.columns else 0
        
        # Agent metrics
        unique_agents = df['agent_id'].nunique() if 'agent_id' in df.columns else 0
        
        # Status distribution
        status_distribution = {}
        if 'call_status' in df.columns:
            status_distribution = df['call_status'].value_counts().to_dict()
        
        # Time-based metrics
        daily_calls = {}
        if 'call_date' in df.columns:
            daily_calls = df.groupby(df['call_date'].dt.date).size().to_dict()
        
        metrics = {
            'total_calls': total_calls,
            'successful_calls': successful_calls,
            'conversion_rate': round(conversion_rate, 2),
            'avg_duration': round(avg_duration, 2),
            'total_duration': round(total_duration, 2),
            'unique_agents': unique_agents,
            'status_distribution': status_distribution,
            'daily_calls': daily_calls,
            'period_start': date_range[0] if date_range else None,
            'period_end': date_range[1] if date_range else None
        }
        
        logger.info(f"Calculated metrics for {total_calls} calls")
        return metrics
        
    except Exception as e:
        logger.error(f"Error calculating metrics: {e}")
        return get_empty_metrics()

def get_empty_metrics() -> Dict[str, Any]:
    """
    Get empty metrics structure.
    
    Returns:
        dict: Empty metrics
    """
    return {
        'total_calls': 0,
        'successful_calls': 0,
        'conversion_rate': 0.0,
        'avg_duration': 0.0,
        'total_duration': 0.0,
        'unique_agents': 0,
        'status_distribution': {},
        'daily_calls': {},
        'period_start': None,
        'period_end': None
    }

def aggregate_data_by_period(df: pd.DataFrame, period: str = 'daily', date_column: str = 'call_date') -> pd.DataFrame:
    """
    Aggregate data by time period.
    
    Args:
        df (pd.DataFrame): Data to aggregate
        period (str): Aggregation period ('daily', 'weekly', 'monthly')
        date_column (str): Date column name
        
    Returns:
        pd.DataFrame: Aggregated data
    """
    try:
        if df.empty or date_column not in df.columns:
            return pd.DataFrame()
        
        # Ensure date column is datetime
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Define grouping frequency
        freq_map = {
            'daily': 'D',
            'weekly': 'W',
            'monthly': 'M'
        }
        
        freq = freq_map.get(period, 'D')
        
        # Group by period
        grouped = df.groupby(pd.Grouper(key=date_column, freq=freq))
        
        # Calculate aggregations
        agg_data = grouped.agg({
            'id': 'count',  # Total calls
            'call_status': lambda x: (x == 'completed').sum() if 'call_status' in df.columns else 0,  # Successful calls
            'duration_minutes': 'mean' if 'duration_minutes' in df.columns else lambda x: 0,  # Avg duration
            'agent_id': 'nunique' if 'agent_id' in df.columns else lambda x: 0  # Unique agents
        }).reset_index()
        
        # Rename columns
        agg_data.columns = [date_column, 'total_calls', 'successful_calls', 'avg_duration', 'unique_agents']
        
        # Calculate conversion rate
        agg_data['conversion_rate'] = (
            agg_data['successful_calls'] / agg_data['total_calls'] * 100
        ).fillna(0).round(2)
        
        # Fill missing periods
        if not agg_data.empty:
            date_range = pd.date_range(
                start=agg_data[date_column].min(),
                end=agg_data[date_column].max(),
                freq=freq
            )
            
            full_range = pd.DataFrame({date_column: date_range})
            agg_data = full_range.merge(agg_data, on=date_column, how='left').fillna(0)
        
        logger.info(f"Aggregated data by {period}: {len(agg_data)} periods")
        return agg_data
        
    except Exception as e:
        logger.error(f"Error aggregating data by period: {e}")
        return pd.DataFrame()

def calculate_agent_performance(calls_df: pd.DataFrame, agents_df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """
    Calculate detailed agent performance metrics.
    
    Args:
        calls_df (pd.DataFrame): Call data
        agents_df (pd.DataFrame, optional): Agent master data
        
    Returns:
        pd.DataFrame: Agent performance metrics
    """
    try:
        if calls_df.empty or 'agent_id' not in calls_df.columns:
            return pd.DataFrame()
        
        # Group by agent
        agent_metrics = calls_df.groupby('agent_id').agg({
            'id': 'count',  # Total calls
            'call_status': lambda x: (x == 'completed').sum() if 'call_status' in calls_df.columns else 0,  # Successful calls
            'duration_minutes': ['mean', 'sum'] if 'duration_minutes' in calls_df.columns else lambda x: [0, 0],  # Duration stats
            'call_date': ['min', 'max'] if 'call_date' in calls_df.columns else lambda x: [None, None]  # Date range
        }).reset_index()
        
        # Flatten column names
        agent_metrics.columns = [
            'agent_id', 'total_calls', 'successful_calls', 
            'avg_duration', 'total_duration', 'first_call', 'last_call'
        ]
        
        # Calculate conversion rate
        agent_metrics['conversion_rate'] = (
            agent_metrics['successful_calls'] / agent_metrics['total_calls'] * 100
        ).round(2)
        
        # Calculate calls per day
        if 'first_call' in agent_metrics.columns and 'last_call' in agent_metrics.columns:
            agent_metrics['days_active'] = (
                (agent_metrics['last_call'] - agent_metrics['first_call']).dt.days + 1
            ).fillna(1)
            agent_metrics['calls_per_day'] = (
                agent_metrics['total_calls'] / agent_metrics['days_active']
            ).round(2)
        
        # Merge with agent master data if provided
        if agents_df is not None and not agents_df.empty:
            agent_metrics = agent_metrics.merge(
                agents_df[['id', 'name']].rename(columns={'id': 'agent_id'}),
                on='agent_id',
                how='left'
            )
        else:
            agent_metrics['name'] = 'Agent ' + agent_metrics['agent_id'].astype(str)
        
        # Sort by conversion rate
        agent_metrics = agent_metrics.sort_values('conversion_rate', ascending=False)
        
        logger.info(f"Calculated performance for {len(agent_metrics)} agents")
        return agent_metrics
        
    except Exception as e:
        logger.error(f"Error calculating agent performance: {e}")
        return pd.DataFrame()

def detect_outliers(df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.Series:
    """
    Detect outliers in a numeric column.
    
    Args:
        df (pd.DataFrame): Data
        column (str): Column to analyze
        method (str): Detection method ('iqr', 'zscore')
        
    Returns:
        pd.Series: Boolean series indicating outliers
    """
    try:
        if df.empty or column not in df.columns:
            return pd.Series(dtype=bool)
        
        data = pd.to_numeric(df[column], errors='coerce').dropna()
        
        if len(data) == 0:
            return pd.Series([False] * len(df), index=df.index)
        
        if method == 'iqr':
            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = (data < lower_bound) | (data > upper_bound)
            
        elif method == 'zscore':
            z_scores = np.abs((data - data.mean()) / data.std())
            outliers = z_scores > 3
            
        else:
            return pd.Series([False] * len(df), index=df.index)
        
        # Map back to original dataframe
        result = pd.Series([False] * len(df), index=df.index)
        result.loc[outliers.index] = outliers
        
        logger.info(f"Detected {outliers.sum()} outliers in {column} using {method} method")
        return result
        
    except Exception as e:
        logger.error(f"Error detecting outliers: {e}")
        return pd.Series([False] * len(df), index=df.index)

def create_time_series(df: pd.DataFrame, date_column: str = 'call_date', 
                      value_column: str = 'id', freq: str = 'D') -> pd.DataFrame:
    """
    Create time series data for visualization.
    
    Args:
        df (pd.DataFrame): Source data
        date_column (str): Date column name
        value_column (str): Value column name
        freq (str): Frequency for time series
        
    Returns:
        pd.DataFrame: Time series data
    """
    try:
        if df.empty or date_column not in df.columns:
            return pd.DataFrame()
        
        # Ensure date column is datetime
        df[date_column] = pd.to_datetime(df[date_column])
        
        # Create time series
        if value_column == 'id':
            # Count records
            ts_data = df.groupby(pd.Grouper(key=date_column, freq=freq)).size().reset_index()
            ts_data.columns = [date_column, 'count']
        else:
            # Aggregate specified column
            ts_data = df.groupby(pd.Grouper(key=date_column, freq=freq))[value_column].sum().reset_index()
        
        # Fill missing dates
        if not ts_data.empty:
            date_range = pd.date_range(
                start=ts_data[date_column].min(),
                end=ts_data[date_column].max(),
                freq=freq
            )
            
            full_range = pd.DataFrame({date_column: date_range})
            ts_data = full_range.merge(ts_data, on=date_column, how='left').fillna(0)
        
        logger.info(f"Created time series with {len(ts_data)} data points")
        return ts_data
        
    except Exception as e:
        logger.error(f"Error creating time series: {e}")
        return pd.DataFrame()

def calculate_growth_rates(df: pd.DataFrame, value_column: str, periods: int = 1) -> pd.DataFrame:
    """
    Calculate growth rates for time series data.
    
    Args:
        df (pd.DataFrame): Time series data
        value_column (str): Column to calculate growth for
        periods (int): Number of periods for growth calculation
        
    Returns:
        pd.DataFrame: Data with growth rates
    """
    try:
        if df.empty or value_column not in df.columns:
            return df
        
        result_df = df.copy()
        
        # Calculate growth rate
        result_df[f'{value_column}_growth'] = (
            result_df[value_column].pct_change(periods=periods) * 100
        ).round(2)
        
        # Calculate moving average
        result_df[f'{value_column}_ma'] = (
            result_df[value_column].rolling(window=min(7, len(result_df))).mean()
        ).round(2)
        
        logger.info(f"Calculated growth rates for {value_column}")
        return result_df
        
    except Exception as e:
        logger.error(f"Error calculating growth rates: {e}")
        return df