"""
Gestión Completa - Vista unificada de Leads y Llamadas
Fusión de Leads y Llamadas para eliminar duplicación de información
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from services.data_service import DataService
from services.supabase_client import test_connection
from utils.formatters import format_number, format_percentage
from utils.i18n_helpers import t, init_i18n, bilingual_metric, bilingual_header, bilingual_subheader, bilingual_selectbox
import logging

logger = logging.getLogger(__name__)

def render():
    """Render the unified leads and calls management page."""
    try:
        # Initialize i18n
        init_i18n()
        
        # Test connection
        connection_status = test_connection_status()
        
        # Use global date range from session state
        if 'date_range' in st.session_state:
            start_date, end_date = st.session_state.date_range
        else:
            start_date = datetime.now().date() - timedelta(days=30)
            end_date = datetime.now().date()
        
        date_range = (start_date, end_date)
        
        # Show connection status
        if connection_status == 'connected':
            st.success(t("connected_supabase"))
        else:
            st.warning(t("disconnected_supabase"))
        
        # Main title
        bilingual_header("👥 Gestión Completa de Leads y Llamadas", "👥 Complete Lead and Call Management")
        st.markdown(f"**{t('period')}** {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
        st.markdown("---")
        
        # Section 1: Resumen de Gestión
        render_management_summary(date_range)
        
        # Section 2: Análisis de Leads
        st.markdown(f"""
        <div style="background: #e8f5e8; padding: 1.5rem; border-radius: 0.75rem; margin: 2rem 0 1rem 0;">
            <h3 style="margin: 0; color: #2e7d32;">👥 {t("management.leads_analysis")}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #388e3c;">{t("management.leads_management_tracking")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            render_leads_table(date_range)
        with col2:
            render_leads_status_distribution(date_range)
        
        # Section 3: Análisis de Llamadas
        st.markdown(f"""
        <div style="background: #e3f2fd; padding: 1.5rem; border-radius: 0.75rem; margin: 2rem 0 1rem 0;">
            <h3 style="margin: 0; color: #1565c0;">📞 {t("management.calls_analysis")}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #1976d2;">{t("management.calls_tracking_results")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            render_calls_table(date_range)
        with col2:
            render_calls_results_distribution(date_range)
        
        # Section 4: Relación Leads-Llamadas
        st.markdown(f"""
        <div style="background: #fff3e0; padding: 1.5rem; border-radius: 0.75rem; margin: 2rem 0 1rem 0;">
            <h3 style="margin: 0; color: #ef6c00;">🔗 {t("management.leads_calls_relationship")}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #f57c00;">{t("management.integrated_management_analysis")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            render_leads_calls_relationship(date_range)
        with col2:
            render_performance_metrics(date_range)
        
        # Section 5: Acciones y Filtros Avanzados
        render_advanced_filters_and_actions(date_range)
        
    except Exception as e:
        st.error(f"{t('common.loading_error')}: {e}")
        logger.error(f"Management error: {e}")

def test_connection_status():
    """Test and update connection status."""
    try:
        result = test_connection()
        if isinstance(result, dict) and result.get('status') == 'success':
            st.session_state.connection_status = 'connected'
            return 'connected'
        else:
            st.session_state.connection_status = 'disconnected'
            return 'disconnected'
    except Exception:
        st.session_state.connection_status = 'disconnected'
        return 'disconnected'

def render_management_summary(date_range):
    """Render management summary with key metrics."""
    
    # Get data with loading indicator
    with st.spinner(t("management.loading_management_summary")):
        leads_data = DataService.get_leads_summary()
        calls_data = DataService.get_calls_summary(date_range)
    
    # KPIs row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_leads = leads_data.get("total_active_leads", 0)
        bilingual_metric(
            label_es="👥 Total Leads",
            label_en="👥 Total Leads",
            value=format_number(total_leads),
            help_es="Total de leads activos en el sistema",
            help_en="Total active leads in the system"
        )
    
    with col2:
        contacted_leads = calls_data.get("contacted_leads", 0)
        bilingual_metric(
            label_es="📞 Leads Contactados",
            label_en="📞 Contacted Leads",
            value=format_number(contacted_leads),
            help_es="Leads que han sido contactados",
            help_en="Leads that have been contacted"
        )
    
    with col3:
        total_calls = calls_data.get("total_calls", 0)
        bilingual_metric(
            label_es="📊 Total Llamadas",
            label_en="📊 Total Calls",
            value=format_number(total_calls),
            help_es="Total de llamadas realizadas",
            help_en="Total calls made"
        )
    
    with col4:
        conversion_rate = calls_data.get("conversion_rate", 0)
        bilingual_metric(
            label_es="🎯 Tasa Conversión",
            label_en="🎯 Conversion Rate",
            value=f"{conversion_rate:.1f}%",
            help_es="Porcentaje de leads convertidos",
            help_en="Percentage of converted leads"
        )

def render_leads_table(date_range):
    """Render leads data table with filters."""
    bilingual_subheader("📋 Gestión de Leads", "📋 Lead Management")
    
    # Load leads data
    leads_df = DataService.get_leads_data(date_range, limit=1000)
    
    if isinstance(leads_df, dict):
        leads_df = pd.DataFrame()
    
    if not leads_df.empty:
        # Add filters
        if "estado_lead" in leads_df.columns:
            estados_disponibles = leads_df["estado_lead"].unique().tolist()
            estado_filter = bilingual_selectbox(
                label_es="Filtrar por estado:",
                label_en="Filter by status:",
                options=[t("common.all")] + estados_disponibles,
                key="leads_estado_filter"
            )
            
            if estado_filter != t("common.all"):
                leads_df = leads_df[leads_df["estado_lead"] == estado_filter]
        
        # Display metrics
        bilingual_metric(
            label_es="Leads mostrados",
            label_en="Leads shown",
            value=str(len(leads_df))
        )
        
        # Display table
        if not leads_df.empty:
            # Select relevant columns
            display_columns = []
            if "nombre" in leads_df.columns:
                display_columns.append("nombre")
            if "telefono" in leads_df.columns:
                display_columns.append("telefono")
            if "email" in leads_df.columns:
                display_columns.append("email")
            if "estado_lead" in leads_df.columns:
                display_columns.append("estado_lead")
            if "fecha_creacion" in leads_df.columns:
                display_columns.append("fecha_creacion")
            
            if display_columns:
                st.dataframe(
                    leads_df[display_columns].head(50),
                    use_container_width=True,
                    height=300
                )
            else:
                st.dataframe(leads_df.head(50), use_container_width=True, height=300)
        else:
            st.info(t("management.no_matching_leads"))
    else:
        st.info(t("management.no_leads_data"))

def render_leads_status_distribution(date_range):
    """Render leads status distribution chart."""
    bilingual_subheader("📊 Distribución de Estados", "📊 Status Distribution")
    
    leads_df = DataService.get_leads_data(date_range, limit=5000)
    
    if isinstance(leads_df, dict):
        leads_df = pd.DataFrame()
    
    if not leads_df.empty and "estado_lead" in leads_df.columns:
        estado_counts = leads_df["estado_lead"].value_counts()
        
        # Color mapping
        color_map = {
            "no_contactado": "#ff6b6b",
            "contactado": "#4ecdc4", 
            "interesado": "#45b7d1",
            "no_interesado": "#96ceb4",
            "calificado": "#feca57",
            "cotizacion_gratis": "#48dbfb"
        }
        
        colors = [color_map.get(estado, "#95a5a6") for estado in estado_counts.index]
        
        fig_estado = px.pie(
            values=estado_counts.values,
            names=estado_counts.index,
            title=t("management.lead_status_chart"),
            color_discrete_sequence=colors
        )
        fig_estado.update_traces(textposition='inside', textinfo='percent+label')
        fig_estado.update_layout(height=350)
        st.plotly_chart(fig_estado, use_container_width=True)
    else:
        st.info(t("management.no_status_data"))

def render_calls_table(date_range):
    """Render calls data table with filters."""
    bilingual_subheader("📞 Registro de Llamadas", "📞 Call Records")
    
    # Load calls data
    calls_df = DataService.get_calls_data(date_range, limit=1000)
    
    if isinstance(calls_df, dict):
        calls_df = pd.DataFrame()
    
    if not calls_df.empty:
        # Add filters
        if "resultado_llamada" in calls_df.columns:
            resultados_disponibles = calls_df["resultado_llamada"].unique().tolist()
            resultado_filter = bilingual_selectbox(
                label_es="Filtrar por resultado:",
                label_en="Filter by result:",
                options=[t("common.all")] + resultados_disponibles,
                key="calls_resultado_filter"
            )
            
            if resultado_filter != t("common.all"):
                calls_df = calls_df[calls_df["resultado_llamada"] == resultado_filter]
        
        # Display metrics
        bilingual_metric(
            label_es="Llamadas mostradas",
            label_en="Calls shown",
            value=str(len(calls_df))
        )
        
        # Display table
        if not calls_df.empty:
            # Select relevant columns
            display_columns = []
            if "lead_id" in calls_df.columns:
                display_columns.append("lead_id")
            if "fecha_llamada" in calls_df.columns:
                display_columns.append("fecha_llamada")
            if "resultado_llamada" in calls_df.columns:
                display_columns.append("resultado_llamada")
            if "duracion_minutos" in calls_df.columns:
                display_columns.append("duracion_minutos")
            if "notas" in calls_df.columns:
                display_columns.append("notas")
            
            if display_columns:
                st.dataframe(
                    calls_df[display_columns].head(50),
                    use_container_width=True,
                    height=300
                )
            else:
                st.dataframe(calls_df.head(50), use_container_width=True, height=300)
        else:
            st.info(t("management.no_matching_calls"))
    else:
        st.info(t("management.no_calls_data"))

def render_calls_results_distribution(date_range):
    """Render calls results distribution chart."""
    bilingual_subheader("🎯 Resultados de Llamadas", "🎯 Call Results")
    
    results_data = DataService.get_calls_by_result(date_range)
    
    if not results_data.empty:
        # Color mapping
        color_map = {
            "exitosa": "#2ecc71",
            "no_contesta": "#e74c3c",
            "ocupado": "#f39c12",
            "buzón": "#9b59b6",
            "número_incorrecto": "#e67e22",
            "rechazada": "#95a5a6"
        }
        
        colors = [color_map.get(result, "#34495e") for result in results_data['resultado_llamada']]
        
        fig_results = px.pie(
            results_data,
            values='cantidad',
            names='resultado_llamada',
            title=t("management.results_distribution_chart"),
            color_discrete_sequence=colors
        )
        fig_results.update_traces(textposition='inside', textinfo='percent+label')
        fig_results.update_layout(height=350)
        st.plotly_chart(fig_results, use_container_width=True)
    else:
        st.info(t("management.no_results_data"))

def render_leads_calls_relationship(date_range):
    """Render relationship analysis between leads and calls."""
    bilingual_subheader("🔗 Relación Leads-Llamadas", "🔗 Lead-Call Relationship")
    
    # Load data
    leads_df = DataService.get_leads_data(date_range, limit=5000)
    calls_df = DataService.get_calls_data(date_range, limit=5000)
    
    if isinstance(leads_df, dict):
        leads_df = pd.DataFrame()
    if isinstance(calls_df, dict):
        calls_df = pd.DataFrame()
    
    if not leads_df.empty and not calls_df.empty:
        # Calculate calls per lead
        if "lead_id" in calls_df.columns:
            calls_per_lead = calls_df.groupby("lead_id").size().reset_index(name='num_calls')
            
            # Create histogram
            fig_hist = px.histogram(
                calls_per_lead,
                x='num_calls',
                title=t("management.calls_per_lead_distribution"),
                nbins=20,
                color_discrete_sequence=['#3498db']
            )
            fig_hist.update_layout(
                xaxis_title=t("management.number_of_calls"),
                yaxis_title=t("management.number_of_leads"),
                height=300
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
            # Show statistics
            avg_calls = calls_per_lead['num_calls'].mean()
            max_calls = calls_per_lead['num_calls'].max()
            bilingual_metric(
                label_es="Promedio llamadas/lead",
                label_en="Average calls/lead",
                value=f"{avg_calls:.1f}"
            )
            bilingual_metric(
                label_es="Máximo llamadas a un lead",
                label_en="Maximum calls to a lead",
                value=str(max_calls)
            )
        else:
            st.info(t("management.no_lead_id_analysis"))
    else:
        st.info(t("management.insufficient_data_analysis"))

def render_performance_metrics(date_range):
    """Render performance metrics."""
    bilingual_subheader("📈 Métricas de Performance", "📈 Performance Metrics")
    
    # Load summary data
    calls_data = DataService.get_calls_summary(date_range)
    
    # Display key metrics
    col1, col2 = st.columns(2)
    
    with col1:
        bilingual_metric(
            label_es="📞 Tasa de Contacto",
            label_en="📞 Contact Rate",
            value=f"{calls_data.get('contact_rate', 0):.1f}%"
        )
        bilingual_metric(
            label_es="✅ Éxito en Llamadas",
            label_en="✅ Call Success Rate",
            value=f"{calls_data.get('success_rate', 0):.1f}%"
        )
    
    with col2:
        bilingual_metric(
            label_es="🎯 Tasa de Conversión",
            label_en="🎯 Conversion Rate",
            value=f"{calls_data.get('conversion_rate', 0):.1f}%"
        )
        bilingual_metric(
            label_es="📊 Llamadas por Lead",
            label_en="📊 Calls per Lead",
            value=f"{calls_data.get('calls_per_lead', 0):.1f}"
        )
    
    # Performance trend
    calls_volume = DataService.get_daily_calls_volume(date_range)
    
    if not calls_volume.empty:
        fig_trend = px.line(
            calls_volume,
            x='fecha',
            y='total_llamadas',
            title=t("management.daily_calls_trend"),
            markers=True
        )
        fig_trend.update_traces(line_color='#2ecc71', marker_color='#2ecc71')
        fig_trend.update_layout(height=250)
        st.plotly_chart(fig_trend, use_container_width=True)

def render_advanced_filters_and_actions(date_range):
    """Render advanced filters and action buttons."""
    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 0.75rem; margin: 2rem 0 1rem 0;">
        <h3 style="margin: 0; color: #495057;">⚙️ {t("management.advanced_actions_filters")}</h3>
        <p style="margin: 0.5rem 0 0 0; color: #6c757d;">{t("management.additional_management_tools")}</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        bilingual_subheader(f"📊 {t('management.export_data')}", f"📊 {t('management.export_data')}")
        if st.button(f"📥 {t('management.export_leads')}", key="export_leads"):
            st.info(t("management.export_functionality_development"))
        if st.button(f"📥 {t('management.export_calls')}", key="export_calls"):
            st.info(t("management.export_functionality_development"))
    
    with col2:
        bilingual_subheader(f"🔍 {t('management.advanced_search')}", f"🔍 {t('management.advanced_search')}")
        search_term = st.text_input(t("management.search_name_phone"), key="advanced_search")
        if search_term:
            st.info(f"{t('management.searching')}: {search_term}")
    
    with col3:
        bilingual_subheader(f"📈 {t('management.reports')}", f"📈 {t('management.reports')}")
        if st.button(f"📋 {t('management.generate_report')}", key="generate_report"):
            st.info(t("management.report_generation_development"))
        if st.button(f"📧 {t('management.send_report')}", key="send_report"):
            st.info(t("management.report_sending_development"))