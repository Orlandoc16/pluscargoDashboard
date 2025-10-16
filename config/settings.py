"""
Configuration settings for Call Analytics Streamlit application.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Try to import streamlit for secrets (only available when running in Streamlit)
try:
    import streamlit as st
    _streamlit_available = True
except ImportError:
    _streamlit_available = False

def get_config_value(key, default=None):
    """Get configuration value from Streamlit secrets or environment variables."""
    if _streamlit_available:
        try:
            # Try to get from Streamlit secrets first
            if hasattr(st, 'secrets') and 'supabase' in st.secrets:
                supabase_secrets = st.secrets['supabase']
                if key.lower().replace('supabase_', '') in supabase_secrets:
                    return supabase_secrets[key.lower().replace('supabase_', '')]
        except Exception:
            pass
    
    # Fallback to environment variables
    return os.getenv(key, default)

# Supabase Configuration
SUPABASE_URL = get_config_value("SUPABASE_URL")
SUPABASE_ANON_KEY = get_config_value("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = get_config_value("SUPABASE_SERVICE_ROLE_KEY")

# Database Tables
LEADS_TABLE = os.getenv("LEADS_TABLE", "leads_pluscargo_simple")
CALL_RESULTS_TABLE = os.getenv("CALL_RESULTS_TABLE", "call_results_pluscargo_simple")
AGENTS_TABLE = os.getenv("AGENTS_TABLE", "agents")

# Application Settings
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # 5 minutes
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
TIMEOUT = int(os.getenv("TIMEOUT", "30"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

# UI Configuration
APP_TITLE = "Call Analytics Dashboard"
APP_ICON = "📊"
PAGE_LAYOUT = "wide"
DEBUG_MODE = DEBUG
# Legacy names for backward compatibility
PAGE_TITLE = APP_TITLE
PAGE_ICON = APP_ICON
LAYOUT = PAGE_LAYOUT

# Chart Colors
CHART_COLORS = [
    "#FF4B4B",  # primary
    "#00D4AA",  # success
    "#F97316",  # warning
    "#DC2626",  # error
    "#1E3A8A",  # info
    "#64748B"   # neutral
]

# Date Format
DATE_FORMAT = "%Y-%m-%d"
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

# Export Settings
EXPORT_FORMATS = ["CSV", "Excel", "PDF"]
MAX_EXPORT_ROWS = 10000

# Validation
def validate_config():
    """Validate required configuration variables."""
    required_vars = [
        ("SUPABASE_URL", SUPABASE_URL),
        ("SUPABASE_ANON_KEY", SUPABASE_ANON_KEY)
    ]
    
    missing_vars = []
    for var_name, var_value in required_vars:
        if not var_value:
            missing_vars.append(var_name)
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    return True

def is_config_valid():
    """Check if configuration is valid without raising exceptions."""
    try:
        validate_config()
        return True
    except ValueError:
        return False

# Note: Validation is not run automatically on import to prevent deployment failures
# Call validate_config() or is_config_valid() explicitly when needed