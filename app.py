"""
Call Analytics Dashboard - Streamlit Application
Interfaz rediseñada enfocada en leads_pluscargo_simple y call_results_pluscargo_simple
"""
import streamlit as st
import logging
from datetime import datetime, timedelta
from config.settings import (
    APP_TITLE, APP_ICON, PAGE_LAYOUT, DEBUG_MODE,
    validate_config, CHART_COLORS
)
from utils.i18n_helpers import (
    init_language, language_selector, t, 
    create_bilingual_header, create_bilingual_selectbox,
    create_bilingual_button, show_error_message, show_info_message
)

# Configure logging
logging.basicConfig(
    level=logging.INFO if not DEBUG_MODE else logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize i18n system
init_language()

# Page configuration
st.set_page_config(
    page_title=t('app_title', 'common'),
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items=None
)

# Check configuration and show warning if not configured
from config.settings import is_config_valid
if not is_config_valid():
    st.warning("⚠️ " + t('config_warning', 'common', 'Configuration incomplete. Please set up your Supabase credentials in Streamlit Cloud secrets.'))
    st.info("ℹ️ " + t('config_info', 'common', 'Go to Manage app → Secrets and add your Supabase URL and keys.'))

# Add custom CSS for better styling and accessibility
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 1rem;
        color: white;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        margin: 0;
        color: white;
        font-weight: 600;
    }
    
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #e1e5e9;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }
    
    .status-success { background-color: #28a745; }
    .status-warning { background-color: #ffc107; }
    .status-error { background-color: #dc3545; }
    
    .sidebar-info {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }
    
    .chart-container {
        background: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        border: 1px solid #e1e5e9;
    }
    
    /* Hide Streamlit default elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Hide Streamlit sidebar navigation */
    .css-1d391kg {display: none;}
    .css-1rs6os {display: none;}
    .css-17eq0hr {display: none;}
    section[data-testid="stSidebar"] nav {display: none;}
    section[data-testid="stSidebar"] .css-1d391kg {display: none;}
    section[data-testid="stSidebar"] .css-1rs6os {display: none;}
    section[data-testid="stSidebar"] .css-17eq0hr {display: none;}
    [data-testid="stSidebarNav"] {display: none !important;}
    .st-emotion-cache-1cypcdb {display: none !important;}
    .st-emotion-cache-pkbazv {display: none !important;}
    
    /* Enhanced accessibility and visual feedback */
    .stButton > button {
        width: 100%;
        transition: all 0.3s ease;
        border-radius: 0.5rem;
        border: 1px solid #007bff;
        background-color: #007bff;
        color: white;
        font-weight: 500;
    }
    
    .stButton > button:hover {
        background-color: #0056b3;
        border-color: #0056b3;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
    }
    .stButton > button:focus {
        outline: 2px solid #667eea;
        outline-offset: 2px;
    }
    
    /* Improved contrast for better readability */
    .stSelectbox > div > div {
        background-color: white;
        border: 2px solid #e9ecef;
        border-radius: 0.5rem;
    }
    .stSelectbox > div > div:focus-within {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Loading spinner enhancement */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Success/Error message styling */
    .stSuccess {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
    .stError {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
    .stInfo {
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        border-radius: 0.5rem;
        padding: 0.75rem;
    }
    
    /* Chart container improvements */
    .js-plotly-plot {
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    /* Keyboard navigation improvements */
    *:focus {
        outline: 2px solid #667eea;
        outline-offset: 2px;
    }
    
    /* High contrast mode support */
    @media (prefers-contrast: high) {
        .main-header {
            background: #000;
            color: #fff;
            border: 2px solid #fff;
        }
        .stButton > button {
            border: 2px solid #000;
        }
    }
    
    /* Reduced motion support */
    @media (prefers-reduced-motion: reduce) {
        .stButton > button {
            transition: none;
        }
        .stButton > button:hover {
            transform: none;
        }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'Dashboard_Analisis'
    
    if 'date_range' not in st.session_state:
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)
        st.session_state.date_range = (start_date, end_date)
    
    if 'selected_agents' not in st.session_state:
        st.session_state.selected_agents = []
    
    if 'connection_status' not in st.session_state:
        st.session_state.connection_status = 'unknown'

def render_sidebar():
    """Render the sidebar with navigation and filters."""
    with st.sidebar:
        # Language selector at the top
        language_selector()
        
        # App header
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <h2>{APP_ICON} {t('app_title', 'common')}</h2>
            <p style="color: #666; font-size: 0.9rem;">{t('app_subtitle', 'common')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation - Main Pages
        st.markdown(f"### 🧭 {t('navigation', 'common')}")
        
        # Main visible pages
        main_pages = {
            f"🏠 App": "Dashboard_Analisis",
            f"👥 Leads": "_leads",
            f"📞 Llamadas": "_llamadas"
        }
        
        # Create main navigation buttons with active state styling
        for display_name, page_name in main_pages.items():
            is_active = st.session_state.current_page == page_name
            button_style = "primary" if is_active else "secondary"
            
            if st.button(
                display_name, 
                key=f"nav_{page_name}",
                type=button_style,
                use_container_width=True
            ):
                if not is_active:  # Only change if not already active
                    st.session_state.current_page = page_name
                    st.rerun()
        
        # Advanced options dropdown
        st.markdown("---")
        st.markdown(f"### ⚙️ Opciones avanzadas")
        
        advanced_pages = {
            f"🧑‍💼 Agentes": "_agentes",
            f"📊 Análisis": "Dashboard_Analisis", 
            f"⚙️ Configuración": "Configuración",
            f"📊 Dashboard": "Dashboard_Analisis",
            f"👥 Gestión Completa": "Gestion_Completa",
            f"📋 Reportes": "Reportes"
        }
        
        # Get current selection for dropdown
        current_advanced = None
        for display_name, page_name in advanced_pages.items():
            if st.session_state.current_page == page_name and page_name not in main_pages.values():
                current_advanced = display_name
                break
        
        selected_advanced = st.selectbox(
            "Seleccionar opción:",
            options=["-- Seleccionar --"] + list(advanced_pages.keys()),
            index=0 if current_advanced is None else list(advanced_pages.keys()).index(current_advanced) + 1,
            key="advanced_nav_select"
        )
        
        # Handle advanced page selection
        if selected_advanced != "-- Seleccionar --" and selected_advanced in advanced_pages:
            selected_page = advanced_pages[selected_advanced]
            if st.session_state.current_page != selected_page:
                st.session_state.current_page = selected_page
                st.rerun()
        
        st.markdown("---")
        
        # Global filters (only show on relevant pages)
        if st.session_state.current_page in ['Dashboard_Analisis', 'Gestion_Completa']:
            st.markdown(f"### 🔍 {t('global_filters', 'common')}")
            
            # Date range filter
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    t('from_date', 'common'),
                    value=st.session_state.date_range[0],
                    key="global_start_date"
                )
            with col2:
                end_date = st.date_input(
                    t('to_date', 'common'), 
                    value=st.session_state.date_range[1],
                    key="global_end_date"
                )
            
            # Update session state if dates changed
            if (start_date, end_date) != st.session_state.date_range:
                st.session_state.date_range = (start_date, end_date)
                st.rerun()
            
            # Quick date filters
            st.markdown(f"**{t('quick_filters', 'common')}:**")
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(t('last_7_days', 'common'), key="last_7_days"):
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=7)
                    st.session_state.date_range = (start_date, end_date)
                    st.rerun()
                
                if st.button(t('last_month', 'common'), key="last_month"):
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=30)
                    st.session_state.date_range = (start_date, end_date)
                    st.rerun()
            
            with col2:
                if st.button(t('last_15_days', 'common'), key="last_15_days"):
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=15)
                    st.session_state.date_range = (start_date, end_date)
                    st.rerun()
                
                if st.button(t('last_3_months', 'common'), key="last_3_months"):
                    end_date = datetime.now().date()
                    start_date = end_date - timedelta(days=90)
                    st.session_state.date_range = (start_date, end_date)
                    st.rerun()
            
            # Advanced filters section
            st.markdown("---")
            st.markdown(f"### 🎯 {t('advanced_filters', 'common')}")
            
            # Initialize advanced filters in session state if not exists
            if 'advanced_filters' not in st.session_state:
                st.session_state.advanced_filters = {
                    'agent': t('all', 'common'),
                    'lead_status': t('all', 'common'),
                    'industry': t('all', 'common'),
                    'call_result': t('all', 'common')
                }
            
            # Agent filter
            agent_options = [t('all', 'common'), 'Juan Pérez', 'María García', 'Carlos López', 'Ana Martínez']
            selected_agent = st.selectbox(
                f"👤 {t('agent', 'common')}",
                options=agent_options,
                index=agent_options.index(st.session_state.advanced_filters['agent']) if st.session_state.advanced_filters['agent'] in agent_options else 0,
                key="filter_agent"
            )
            
            # Lead status filter
            status_options = [t('all', 'common'), t('lead_status_new', 'management'), t('lead_status_contacted', 'management'), 
                            t('lead_status_interested', 'management'), t('lead_status_qualified', 'management'), t('lead_status_not_interested', 'management')]
            selected_status = st.selectbox(
                f"📋 {t('lead_status', 'common')}",
                options=status_options,
                index=status_options.index(st.session_state.advanced_filters['lead_status']) if st.session_state.advanced_filters['lead_status'] in status_options else 0,
                key="filter_status"
            )
            
            # Industry filter
            industry_options = [t('all', 'common'), t('industry_technology', 'management'), t('industry_manufacturing', 'management'), 
                              t('industry_services', 'management'), t('industry_retail', 'management'), t('industry_healthcare', 'management'), t('industry_education', 'management')]
            selected_industry = st.selectbox(
                f"🏢 {t('industry', 'common')}",
                options=industry_options,
                index=industry_options.index(st.session_state.advanced_filters['industry']) if st.session_state.advanced_filters['industry'] in industry_options else 0,
                key="filter_industry"
            )
            
            # Call result filter (only for relevant pages)
            if st.session_state.current_page in ['Dashboard', 'Llamadas']:
                result_options = [t('all', 'common'), t('call_result_successful', 'management'), t('call_result_no_answer', 'management'), 
                                t('call_result_busy', 'management'), t('call_result_not_interested', 'management'), t('call_result_reschedule', 'management')]
                selected_result = st.selectbox(
                    f"📞 {t('call_result', 'common')}",
                    options=result_options,
                    index=result_options.index(st.session_state.advanced_filters['call_result']) if st.session_state.advanced_filters['call_result'] in result_options else 0,
                    key="filter_call_result"
                )
                
                # Update session state for call result
                if selected_result != st.session_state.advanced_filters['call_result']:
                    st.session_state.advanced_filters['call_result'] = selected_result
                    st.rerun()
            
            # Update session state for other filters
            filters_changed = False
            if selected_agent != st.session_state.advanced_filters['agent']:
                st.session_state.advanced_filters['agent'] = selected_agent
                filters_changed = True
            if selected_status != st.session_state.advanced_filters['lead_status']:
                st.session_state.advanced_filters['lead_status'] = selected_status
                filters_changed = True
            if selected_industry != st.session_state.advanced_filters['industry']:
                st.session_state.advanced_filters['industry'] = selected_industry
                filters_changed = True
            
            if filters_changed:
                st.rerun()
            
            # Clear filters button
            if st.button(f"🔄 {t('clear_filters', 'common')}", key="clear_filters"):
                st.session_state.advanced_filters = {
                    'agent': t('all', 'common'),
                    'lead_status': t('all', 'common'),
                    'industry': t('all', 'common'),
                    'call_result': t('all', 'common')
                }
                st.rerun()
            
            # Show active filters summary
            active_filters = []
            for key, value in st.session_state.advanced_filters.items():
                if value != t('all', 'common'):
                    active_filters.append(f"{key}: {value}")
            
            if active_filters:
                st.markdown(f"**{t('active_filters', 'common')}:**")
                for filter_text in active_filters:
                    st.markdown(f"• {filter_text}")
            else:
                st.markdown(f"*{t('no_active_filters', 'common')}*")
        
        st.markdown("---")
        
        # Connection status
        status_color = {
            'connected': '#28a745',
            'disconnected': '#dc3545', 
            'unknown': '#ffc107'
        }.get(st.session_state.connection_status, '#ffc107')
        
        status_text = {
            'connected': t('connected', 'common'),
            'disconnected': t('disconnected', 'common'),
            'unknown': t('checking', 'common')
        }.get(st.session_state.connection_status, t('unknown', 'common'))
        
        st.markdown(f"""
        <div class="sidebar-info">
            <strong>{t('connection_status', 'common')}:</strong><br>
            <span class="status-indicator" style="background-color: {status_color};"></span>
            {status_text}
        </div>
        """, unsafe_allow_html=True)
        
        # App info
        st.markdown(f"""
        <div style="margin-top: 2rem; padding: 1rem; background: #f8f9fa; border-radius: 0.5rem; font-size: 0.8rem; color: #666;">
            <strong>{t('information', 'common')}:</strong><br>
            • {t('real_time_data', 'common')}<br>
            • {t('auto_update', 'common')}<br>
            • {t('export_available', 'common')}<br>
            <br>
            <strong>{t('version', 'common')}:</strong> 1.0.0<br>
            <strong>{t('last_update', 'common')}:</strong><br>
            {datetime.now().strftime("%d/%m/%Y %H:%M")}
        </div>
        """, unsafe_allow_html=True)

def render_main_content():
    """Render the main content area based on current page."""
    current_page = st.session_state.current_page
    
    # Page header
    st.markdown(f"""
    <div class="main-header">
        <h1>{get_page_icon(current_page)} {get_page_title(current_page)}</h1>
        <p style="color: #666; margin: 0;">
            {get_page_description(current_page)}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load and render the appropriate page
    try:
        if current_page == "Dashboard_Analisis":
            from pages import dashboard_analisis
            dashboard_analisis.render()
        elif current_page == "Gestion_Completa":
            from pages import gestion_completa
            gestion_completa.render()
        elif current_page == "Reportes":
            from pages import reportes
            reportes.render()
        elif current_page == "Configuración":
            from pages import configuracion
            configuracion.render()
        elif current_page == "_leads":
            from pages import _leads
            _leads.render()
        elif current_page == "_llamadas":
            from pages import _llamadas
            _llamadas.render()
        elif current_page == "_agentes":
            from pages import _agentes
            _agentes.render()
        else:
            show_error_message('page_not_found', 'common', page=current_page)
            
    except ImportError as e:
        show_error_message('page_load_error', 'common', page=current_page, error=str(e))
        show_info_message('page_in_development', 'common')
    except Exception as e:
        show_error_message('unexpected_error', 'common', page=current_page, error=str(e))
        if DEBUG_MODE:
            st.exception(e)

def get_page_icon(page_name: str) -> str:
    """Get icon for page name."""
    icons = {
        "Dashboard_Analisis": "📊",
        "Gestion_Completa": "👥",
        "Reportes": "📋",
        "Configuración": "⚙️",
        "_leads": "👥",
        "_llamadas": "📞",
        "_agentes": "🧑‍💼"
    }
    return icons.get(page_name, "📄")

def get_page_title(page_name: str) -> str:
    """Get translated title for page name."""
    titles = {
        "Dashboard_Analisis": t('dashboard_analysis', 'common'),
        "Gestion_Completa": t('complete_management', 'common'),
        "Reportes": t('reports', 'common'),
        "Configuración": t('configuration', 'common'),
        "_leads": "Gestión de Leads",
        "_llamadas": "Análisis de Llamadas",
        "_agentes": "Rendimiento de Agentes"
    }
    return titles.get(page_name, page_name)

def get_page_description(page_name: str) -> str:
    """Get translated description for page name."""
    descriptions = {
        "Dashboard_Analisis": t('dashboard_description', 'common'),
        "Gestion_Completa": t('management_description', 'common'),
        "Reportes": t('reports_description', 'common'),
        "Configuración": t('settings_description', 'common'),
        "_leads": "Gestión completa de leads y seguimiento",
        "_llamadas": "Análisis detallado de llamadas y resultados",
        "_agentes": "Evaluación del rendimiento de agentes"
    }
    return descriptions.get(page_name, t('app_page', 'common'))

def main():
    """Main application function."""
    try:
        # Initialize session state
        initialize_session_state()
        
        # Render sidebar
        render_sidebar()
        
        # Render main content
        render_main_content()
        
    except Exception as e:
        show_error_message('critical_error', 'common', error=str(e))
        if DEBUG_MODE:
            st.exception(e)
        logger.error(f"Critical application error: {e}", exc_info=True)

if __name__ == "__main__":
    main()