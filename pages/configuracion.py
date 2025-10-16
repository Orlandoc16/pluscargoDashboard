"""
Configuracion page - Application settings and preferences.
"""
import streamlit as st
import json
import os
from datetime import datetime, timedelta
from services.supabase_client import test_connection, get_supabase_client
from config.settings import (
    SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY,
    DEBUG_MODE, CACHE_TTL, MAX_RETRIES, REQUEST_TIMEOUT,
    PAGE_TITLE, PAGE_ICON, LAYOUT, CHART_COLORS
)
from utils.i18n_helpers import t, init_i18n, bilingual_metric, bilingual_header, bilingual_subheader, bilingual_selectbox
import logging

logger = logging.getLogger(__name__)

def render():
    """Render the configuration page."""
    # Initialize i18n
    init_i18n()
    
    try:
        # Test connection and update status
        try:
            connection_result = test_connection()
            # Handle connection result properly - it returns a dict with 'status' key
            if isinstance(connection_result, dict) and 'status' in connection_result:
                st.session_state.connection_status = 'connected' if connection_result['status'] == 'success' else 'disconnected'
            else:
                # Fallback for unexpected result format
                st.session_state.connection_status = 'disconnected'
        except Exception as conn_error:
            logger.error(f"Connection test error: {conn_error}")
            st.session_state.connection_status = 'disconnected'
        
        # Show connection status
        if st.session_state.connection_status == 'connected':
            st.success(f"✅ {t('connected_to_supabase', 'settings')}")
        else:
            st.warning(f"⚠️ {t('no_connection_to_supabase', 'settings')}")
        
        # Configuration sections
        render_database_config()
        render_app_settings()
        render_ui_preferences()
        render_data_settings()
        render_export_settings()
        render_system_info()
        
    except Exception as e:
        st.error(f"{t('error_loading_settings_page', 'settings')}: {e}")
        logger.error(f"Configuration page rendering error: {e}", exc_info=True)

def render_database_config():
    """Render database configuration section."""
    bilingual_subheader("🗄️", "database_configuration", "settings")
    
    with st.expander(t('supabase_configuration', 'settings'), expanded=False):
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                st.text_input(
                    t('supabase_url', 'settings'),
                    value=SUPABASE_URL[:50] + "..." if len(SUPABASE_URL) > 50 else SUPABASE_URL,
                    disabled=True,
                    help=t('supabase_url_help', 'settings')
                )
                
                st.text_input(
                    t('anon_key', 'settings'),
                    value="sk-" + "*" * 20 + SUPABASE_ANON_KEY[-10:] if SUPABASE_ANON_KEY else "",
                    disabled=True,
                    type="password",
                    help=t('anon_key_help', 'settings')
                )
            
            with col2:
                st.text_input(
                    t('service_role_key', 'settings'),
                    value="sk-" + "*" * 20 + SUPABASE_SERVICE_ROLE_KEY[-10:] if SUPABASE_SERVICE_ROLE_KEY else "",
                    disabled=True,
                    type="password",
                    help=t('service_role_key_help', 'settings')
                )
            
                # Connection test
                if st.button(f"🔄 {t('test_connection', 'settings')}", key="test_connection"):
                    with st.spinner(t('testing_connection', 'settings')):
                        result = test_connection()
                        if isinstance(result, dict) and result.get('status') == 'success':
                            st.success(f"✅ {t('connection_successful', 'settings')}")
                            st.json({
                                "status": result.get('status'),
                                "message": result.get('message'),
                                "data_available": result.get('data_available', False)
                            })
                        else:
                            error_msg = result.get('message', t('unknown_error', 'settings')) if isinstance(result, dict) else str(result)
                            st.error(f"❌ {t('connection_error', 'settings')}: {error_msg}")
            
            # Database tables info
            st.markdown(f"#### 📋 {t('database_tables', 'settings')}")
            
            tables_info = {
                "leads_pluscargo_simple": t('leads_table_description', 'settings'),
            "call_results_pluscargo_simple": t('calls_table_description', 'settings'),
                "agents": t('agents_table_description', 'settings')
            }
            
            for table, description in tables_info.items():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.code(table)
                with col2:
                    st.write(description)
                    
        except Exception as e:
            st.error(f"{t('error_database_config', 'settings')}: {e}")
            logger.error(f"Database config error: {e}")

def render_app_settings():
    """Render application settings section."""
    bilingual_subheader("⚙️", "app_configuration", "settings")
    
    with st.expander(t('general_configuration', 'settings'), expanded=True):
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                # Debug mode
                debug_enabled = st.checkbox(
                    t('debug_mode', 'settings'),
                    value=DEBUG_MODE,
                    help=t('debug_mode_help', 'settings'),
                    key="debug_mode"
                )
                
                # Cache settings
                cache_ttl = st.number_input(
                    t('cache_ttl', 'settings'),
                    min_value=60,
                    max_value=3600,
                    value=CACHE_TTL,
                    step=60,
                    help=t('cache_ttl_help', 'settings'),
                    key="cache_ttl"
                )
                
                # Auto-refresh settings
                auto_refresh = st.checkbox(
                    t('auto_refresh', 'settings'),
                    value=st.session_state.get('auto_refresh', False),
                    help=t('auto_refresh_help', 'settings'),
                    key="auto_refresh"
                )
            
            with col2:
                # Request settings
                max_retries = st.number_input(
                    t('max_retries', 'settings'),
                    min_value=1,
                    max_value=10,
                    value=MAX_RETRIES,
                    help=t('max_retries_help', 'settings'),
                    key="max_retries"
                )
                
                request_timeout = st.number_input(
                    t('request_timeout', 'settings'),
                    min_value=5,
                    max_value=60,
                    value=REQUEST_TIMEOUT,
                    help=t('request_timeout_help', 'settings'),
                    key="request_timeout"
                )
                
                # Refresh interval (only if auto-refresh is enabled)
                if auto_refresh:
                    refresh_interval = st.selectbox(
                        t('refresh_interval', 'settings'),
                        options=[30, 60, 120, 300, 600],
                        index=2,  # Default to 120 seconds
                        format_func=lambda x: f"{x} {t('seconds', 'settings')}" if x < 60 else f"{x//60} {t('minute' if x//60 == 1 else 'minutes', 'settings')}",
                        key="refresh_interval"
                    )
            
            # Save settings button
            if st.button(f"💾 {t('save_configuration', 'settings')}", key="save_app_settings"):
                save_app_settings({
                    'debug_mode': debug_enabled,
                    'cache_ttl': cache_ttl,
                    'max_retries': max_retries,
                    'request_timeout': request_timeout,
                    'auto_refresh': auto_refresh,
                    'refresh_interval': st.session_state.get('refresh_interval', 120) if auto_refresh else None
                })
                st.success(f"✅ {t('configuration_saved', 'settings')}")
                
        except Exception as e:
            st.error(f"{t('error_app_config', 'settings')}: {e}")
            logger.error(f"App settings error: {e}")

def render_ui_preferences():
    """Render UI preferences section."""
    bilingual_subheader("🎨", "ui_preferences", "settings")
    
    with st.expander(t('visual_configuration', 'settings'), expanded=False):
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                # Theme selection
                theme = bilingual_selectbox(
                    "app_theme", "settings",
                    options=["auto", "light", "dark"],
                    index=0,
                    help=t('app_theme_help', 'settings'),
                    key="app_theme"
                )
                
                # Chart color scheme
                color_scheme = bilingual_selectbox(
                    "chart_color_scheme", "settings",
                    options=["default", "viridis", "plasma", "inferno", "magma", "cividis"],
                    index=0,
                    help=t('chart_color_scheme_help', 'settings'),
                    key="color_scheme"
                )
                
                # Default date range
                default_date_range = st.selectbox(
                    t('default_date_range', 'settings'),
                    options=[7, 15, 30, 60, 90],
                    index=2,  # Default to 30 days
                    format_func=lambda x: f"{t('last', 'settings')} {x} {t('days', 'settings')}",
                    help=t('default_date_range_help', 'settings'),
                    key="default_date_range"
                )
            
            with col2:
                # Page size settings
                page_size = st.number_input(
                    t('elements_per_page', 'settings'),
                    min_value=10,
                    max_value=100,
                    value=20,
                    step=10,
                    help=t('elements_per_page_help', 'settings'),
                    key="page_size"
                )
                
                # Chart height
                chart_height = st.number_input(
                    t('chart_height', 'settings'),
                    min_value=300,
                    max_value=800,
                    value=400,
                    step=50,
                    help=t('chart_height_help', 'settings'),
                    key="chart_height"
                )
                
                # Show advanced features
                show_advanced = st.checkbox(
                    t('show_advanced_features', 'settings'),
                    value=st.session_state.get('show_advanced', False),
                    help=t('show_advanced_features_help', 'settings'),
                    key="show_advanced"
                )
            
            # Preview of current settings
            st.markdown(f"#### 👀 {t('preview', 'settings')}")
            
            # Sample chart with current color scheme
            import plotly.express as px
            import pandas as pd
            
            sample_data = pd.DataFrame({
                t('category', 'settings'): ['A', 'B', 'C', 'D'],
                t('value', 'settings'): [23, 45, 56, 78]
            })
            
            color_discrete_map = None
            if color_scheme != "default":
                fig = px.bar(sample_data, x=t('category', 'settings'), y=t('value', 'settings'), 
                            color_discrete_sequence=getattr(px.colors.sequential, color_scheme.title(), px.colors.qualitative.Set1))
            else:
                fig = px.bar(sample_data, x=t('category', 'settings'), y=t('value', 'settings'))
            
            fig.update_layout(height=200, title=t('chart_example', 'settings'))
            st.plotly_chart(fig, use_container_width=True)
            
            # Save UI preferences
            if st.button(f"💾 {t('save_preferences', 'settings')}", key="save_ui_preferences"):
                save_ui_preferences({
                    'theme': theme,
                    'color_scheme': color_scheme,
                    'default_date_range': default_date_range,
                    'page_size': page_size,
                    'chart_height': chart_height,
                    'show_advanced': show_advanced
                })
                st.success(f"✅ {t('preferences_saved', 'settings')}")
                
        except Exception as e:
            st.error(f"{t('error_ui_preferences', 'settings')}: {e}")
            logger.error(f"UI preferences error: {e}")

def render_data_settings():
    """Render data processing settings section."""
    bilingual_subheader("📊", "data_configuration", "settings")
    
    with st.expander(t('data_processing', 'settings'), expanded=False):
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                # Data limits
                max_records = st.number_input(
                    t('max_records_per_query', 'settings'),
                    min_value=100,
                    max_value=10000,
                    value=5000,
                    step=500,
                    help=t('max_records_per_query_help', 'settings'),
                    key="max_records"
                )
                
                # Data freshness
                data_freshness = st.selectbox(
                    t('data_freshness', 'settings'),
                    options=[1, 5, 15, 30, 60],
                    index=2,  # Default to 15 minutes
                    format_func=lambda x: f"{x} {t('minute' if x == 1 else 'minutes', 'settings')}",
                    help=t('data_freshness_help', 'settings'),
                    key="data_freshness"
                )
            
            with col2:
                # Aggregation settings
                default_aggregation = bilingual_selectbox(
                    "default_aggregation", "settings",
                    options=["daily", "weekly", "monthly"],
                    index=0,
                    help=t('default_aggregation_help', 'settings'),
                    key="default_aggregation"
                )
                
                # Include weekends
                include_weekends = st.checkbox(
                    t('include_weekends', 'settings'),
                    value=True,
                    help=t('include_weekends_help', 'settings'),
                    key="include_weekends"
                )
            
            # Data quality settings
            st.markdown(f"#### 🔍 {t('data_quality', 'settings')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                exclude_test_data = st.checkbox(
                    t('exclude_test_data', 'settings'),
                    value=True,
                    help=t('exclude_test_data_help', 'settings'),
                    key="exclude_test_data"
                )
            
            with col2:
                min_call_duration = st.number_input(
                    t('min_call_duration', 'settings'),
                    min_value=0,
                    max_value=300,
                    value=5,
                    help=t('min_call_duration_help', 'settings'),
                    key="min_call_duration"
                )
            
            if st.button(f"💾 {t('save_data_configuration', 'settings')}", key="save_data_settings"):
                save_data_settings({
                    'max_records': max_records,
                    'data_freshness': data_freshness,
                    'default_aggregation': default_aggregation,
                    'include_weekends': include_weekends,
                    'exclude_test_data': exclude_test_data,
                    'min_call_duration': min_call_duration
                })
                st.success(f"✅ {t('data_configuration_saved', 'settings')}")
                
        except Exception as e:
            st.error(f"{t('error_data_config', 'settings')}: {e}")
            logger.error(f"Data settings error: {e}")

def render_export_settings():
    """Render export settings section."""
    bilingual_subheader("📤", "export_configuration", "settings")
    
    with st.expander(t('export_options', 'settings'), expanded=False):
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                # Default export format
                default_export_format = bilingual_selectbox(
                    "default_export_format", "settings",
                    options=["excel", "csv", "pdf"],
                    index=0,
                    help=t('default_export_format_help', 'settings'),
                    key="default_export_format"
                )
                
                # Include charts in exports
                include_charts_export = st.checkbox(
                    t('include_charts_in_exports', 'settings'),
                    value=True,
                    help=t('include_charts_in_exports_help', 'settings'),
                    key="include_charts_export"
                )
            
            with col2:
                # Max export records
                max_export_records = st.number_input(
                    t('max_records_per_export', 'settings'),
                    min_value=1000,
                    max_value=50000,
                    value=10000,
                    step=1000,
                    help=t('max_records_per_export_help', 'settings'),
                    key="max_export_records"
                )
                
                # Export filename format
                filename_format = bilingual_selectbox(
                    "filename_format", "settings",
                    options=["timestamp", "date_range", "custom"],
                    index=0,
                    help=t('filename_format_help', 'settings'),
                    key="filename_format"
                )
            
            # Export quality settings
            st.markdown(f"#### 📋 {t('export_quality', 'settings')}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                include_metadata = st.checkbox(
                    t('include_metadata', 'settings'),
                    value=True,
                    help=t('include_metadata_help', 'settings'),
                    key="include_metadata"
                )
            
            with col2:
                compress_exports = st.checkbox(
                    t('compress_exports', 'settings'),
                    value=False,
                    help=t('compress_exports_help', 'settings'),
                    key="compress_exports"
                )
            
            if st.button(f"💾 {t('save_export_configuration', 'settings')}", key="save_export_settings"):
                save_export_settings({
                    'default_export_format': default_export_format,
                    'include_charts_export': include_charts_export,
                    'max_export_records': max_export_records,
                    'filename_format': filename_format,
                    'include_metadata': include_metadata,
                    'compress_exports': compress_exports
                })
                st.success(f"✅ {t('export_configuration_saved', 'settings')}")
                
        except Exception as e:
            st.error(f"{t('error_export_config', 'settings')}: {e}")
            logger.error(f"Export settings error: {e}")

def render_system_info():
    """Render system information section."""
    bilingual_subheader("🖥️", "system_information", "settings")
    
    with st.expander(t('technical_information', 'settings'), expanded=False):
        try:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"#### 📦 {t('application', 'settings')}")
                st.write(f"**{t('title', 'settings')}:** {PAGE_TITLE}")
                st.write(f"**{t('icon', 'settings')}:** {PAGE_ICON}")
                st.write(f"**{t('layout', 'settings')}:** {LAYOUT}")
                st.write(f"**{t('debug_mode', 'settings')}:** {t('enabled' if DEBUG_MODE else 'disabled', 'settings')}")
                
                st.markdown(f"#### 🔧 {t('configuration', 'settings')}")
                st.write(f"**{t('cache_ttl', 'settings')}:** {CACHE_TTL} {t('seconds', 'settings')}")
                st.write(f"**{t('max_retries', 'settings')}:** {MAX_RETRIES}")
                st.write(f"**{t('timeout', 'settings')}:** {REQUEST_TIMEOUT} {t('seconds', 'settings')}")
            
            with col2:
                st.markdown(f"#### 🎨 {t('theme', 'settings')}")
                st.write(f"**{t('chart_colors', 'settings')}:**")
                for i, color in enumerate(CHART_COLORS[:5]):
                    st.markdown(f'<div style="display: inline-block; width: 20px; height: 20px; background-color: {color}; margin-right: 5px; border: 1px solid #ccc;"></div> {color}', unsafe_allow_html=True)
                
                st.markdown(f"#### 📊 {t('connection_status', 'settings')}")
                connection_status = st.session_state.get('connection_status', 'unknown')
                status_color = {'connected': '🟢', 'disconnected': '🔴', 'unknown': '🟡'}
                st.write(f"**{t('status', 'settings')}:** {status_color.get(connection_status, '🟡')} {t(connection_status, 'settings')}")
                
                if connection_status == 'connected':
                    st.write(f"**{t('last_verification', 'settings')}:** {t('now', 'settings')}")
                else:
                    st.write(f"**{t('last_verification', 'settings')}:** {t('error', 'settings')}")
            
            # Cache information
            st.markdown(f"#### 💾 {t('cache_information', 'settings')}")
            
            cache_info = get_cache_info()
            if cache_info:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric(t('cache_entries', 'settings'), cache_info.get('entries', 0))
                with col2:
                    st.metric(t('cache_hits', 'settings'), cache_info.get('hits', 0))
                with col3:
                    st.metric(t('cache_misses', 'settings'), cache_info.get('misses', 0))
            
            # Clear cache button
            if st.button(f"🗑️ {t('clear_cache', 'settings')}", key="clear_cache"):
                clear_app_cache()
                st.success(f"✅ {t('cache_cleared', 'settings')}")
                st.rerun()
                
        except Exception as e:
            st.error(f"{t('error_system_info', 'settings')}: {e}")
            logger.error(f"System info error: {e}")

def save_app_settings(settings):
    """Save application settings to session state and local storage."""
    try:
        for key, value in settings.items():
            st.session_state[f"app_{key}"] = value
        
        # Save to local file if needed
        settings_file = os.path.join(os.path.dirname(__file__), '..', 'config', 'user_settings.json')
        os.makedirs(os.path.dirname(settings_file), exist_ok=True)
        
        existing_settings = {}
        if os.path.exists(settings_file):
            with open(settings_file, 'r') as f:
                existing_settings = json.load(f)
        
        existing_settings.update(settings)
        
        with open(settings_file, 'w') as f:
            json.dump(existing_settings, f, indent=2)
        
        logger.info(f"App settings saved: {settings}")
        
    except Exception as e:
        logger.error(f"Error saving app settings: {e}")
        st.error(f"{t('error_saving_configuration', 'settings')}: {e}")

def save_ui_preferences(preferences):
    """Save UI preferences."""
    try:
        for key, value in preferences.items():
            st.session_state[f"ui_{key}"] = value
        
        logger.info(f"UI preferences saved: {preferences}")
        
    except Exception as e:
        logger.error(f"Error saving UI preferences: {e}")
        st.error(f"{t('error_saving_preferences', 'settings')}: {e}")

def save_data_settings(settings):
    """Save data processing settings."""
    try:
        for key, value in settings.items():
            st.session_state[f"data_{key}"] = value
        
        logger.info(f"Data settings saved: {settings}")
        
    except Exception as e:
        logger.error(f"Error saving data settings: {e}")
        st.error(f"{t('error_saving_data_configuration', 'settings')}: {e}")

def save_export_settings(settings):
    """Save export settings."""
    try:
        for key, value in settings.items():
            st.session_state[f"export_{key}"] = value
        
        logger.info(f"Export settings saved: {settings}")
        
    except Exception as e:
        logger.error(f"Error saving export settings: {e}")
        st.error(f"{t('error_saving_export_configuration', 'settings')}: {e}")

def get_cache_info():
    """Get cache information."""
    try:
        # This would typically interface with Streamlit's cache
        # For now, return mock data
        return {
            'entries': len(st.session_state),
            'hits': st.session_state.get('cache_hits', 0),
            'misses': st.session_state.get('cache_misses', 0)
        }
    except Exception as e:
        logger.error(f"Error getting cache info: {e}")
        return {}

def clear_app_cache():
    """Clear application cache."""
    try:
        # Clear Streamlit cache
        st.cache_data.clear()
        
        # Clear session state cache-related items
        cache_keys = [key for key in st.session_state.keys() if 'cache' in key.lower()]
        for key in cache_keys:
            del st.session_state[key]
        
        logger.info("App cache cleared")
        
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        st.error(f"{t('error_clearing_cache', 'settings')}: {e}")