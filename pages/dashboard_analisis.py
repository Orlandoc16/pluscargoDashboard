"""Dashboard & Análisis - Vista ejecutiva completa con KPIs, tendencias y análisis avanzado
Fusión de Dashboard y Análisis para eliminar duplicación de información
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from services.data_service import DataService
from services.supabase_client import test_connection
from utils.formatters import format_number, format_percentage
from utils.i18n_helpers import t, init_i18n, bilingual_metric, bilingual_header, bilingual_subheader
import logging

logger = logging.getLogger(__name__)

def render():
    """Render the unified dashboard and analysis page."""
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
            st.success(t("connected_supabase", "reports"))
        else:
            st.warning(t("disconnected_supabase", "reports"))
        
        # Main title
        bilingual_header(t("dashboard_executive_analysis", "reports"))
        st.markdown(f"**{t('period', 'reports')}** {start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}")
        st.markdown("---")
        
        # Section 1: KPIs Principales
        render_main_kpis(date_range)
        
        # Section 2: Embudo de Conversión y Métricas Avanzadas
        st.markdown(f"""
        <div style="background: #e3f2fd; padding: 1.5rem; border-radius: 0.75rem; margin: 2rem 0 1rem 0;">
            <h3 style="margin: 0; color: #1565c0;">🎯 {t("conversion_analysis", "dashboard")}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #1976d2;">{t("conversion_funnel_description", "dashboard")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            render_conversion_funnel_chart(date_range)
        with col2:
            render_conversion_metrics(date_range)
        
        # Section 3: Análisis Temporal
        st.markdown(f"""
        <div style="background: #f3e5f5; padding: 1.5rem; border-radius: 0.75rem; margin: 2rem 0 1rem 0;">
            <h3 style="margin: 0; color: #7b1fa2;">📈 {t("temporal_analysis", "dashboard")}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #8e24aa;">{t("trends_evolution_time", "dashboard")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            render_leads_evolution_chart(date_range)
        with col2:
            render_daily_calls_chart(date_range)
        
        # Section 4: Distribución y Resultados
        st.markdown(f"""
        <div style="background: #fff3e0; padding: 1.5rem; border-radius: 0.75rem; margin: 2rem 0 1rem 0;">
            <h3 style="margin: 0; color: #ef6c00;">🎯 {t("distribution_results", "dashboard")}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #f57c00;">{t("results_performance_analysis", "dashboard")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            render_calls_by_result_chart(date_range)
        with col2:
            render_leads_by_status_chart(date_range)
        
        # Section 5: Correlaciones y Insights
        st.markdown(f"""
        <div style="background: #e8f5e8; padding: 1.5rem; border-radius: 0.75rem; margin: 2rem 0 1rem 0;">
            <h3 style="margin: 0; color: #2e7d32;">🔍 {t("correlations_insights", "dashboard")}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #388e3c;">{t("advanced_analysis", "dashboard")}</p>
        </div>
        """, unsafe_allow_html=True)
        
        render_correlation_analysis(date_range)
        render_executive_summary(date_range)
        
    except Exception as e:
        st.error(f"{t('common.loading_error')}: {e}")
        logger.error(f"Dashboard error: {e}")

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

def render_main_kpis(date_range):
    """Render main KPIs with enhanced metrics."""
    
    # Get data with loading indicator
    with st.spinner(t("common.loading")):
        leads_data = DataService.get_leads_summary()
        calls_data = DataService.get_calls_summary(date_range)
    
    # First row of KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_leads = leads_data.get("total_active_leads", 0)
        bilingual_metric(
            label_es="👥 Leads Activos",
            label_en="👥 Active Leads",
            value=format_number(total_leads),
            help_es="Total de leads en el sistema",
            help_en="Total leads in the system"
        )
    
    with col2:
        total_calls = calls_data.get("total_calls", 0)
        bilingual_metric(
            label_es="📞 Llamadas Realizadas",
            label_en="📞 Calls Made",
            value=format_number(total_calls),
            help_es="Total de llamadas en el período",
            help_en="Total calls in the period"
        )
    
    with col3:
        calls_per_lead = calls_data.get("calls_per_lead", 0)
        bilingual_metric(
            label_es="📊 Llamadas por Lead",
            label_en="📊 Calls per Lead",
            value=f"{calls_per_lead:.1f}",
            help_es="Promedio de llamadas por lead",
            help_en="Average calls per lead"
        )
    
    with col4:
        contact_rate = calls_data.get("contact_rate", 0)
        bilingual_metric(
            label_es="📈 Tasa de Contacto",
            label_en="📈 Contact Rate",
            value=f"{contact_rate:.1f}%",
            help_es="Porcentaje de leads contactados exitosamente",
            help_en="Percentage of successfully contacted leads"
        )
    
    # Second row of KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        conversion_rate = calls_data.get("conversion_rate", 0)
        bilingual_metric(
            label_es="🎯 Tasa de Conversión",
            label_en="🎯 Conversion Rate",
            value=f"{conversion_rate:.1f}%",
            help_es="Porcentaje de leads convertidos",
            help_en="Percentage of converted leads"
        )
    
    with col2:
        success_rate = calls_data.get("success_rate", 0)
        bilingual_metric(
            label_es="✅ Éxito en Llamadas",
            label_en="✅ Call Success",
            value=f"{success_rate:.1f}%",
            help_es="Porcentaje de llamadas exitosas",
            help_en="Percentage of successful calls"
        )
    
    with col3:
        converted_leads = leads_data.get("converted_leads", 0)
        bilingual_metric(
            label_es="🏆 Leads Convertidos",
            label_en="🏆 Converted Leads",
            value=format_number(converted_leads),
            help_es="Total de leads convertidos",
            help_en="Total converted leads"
        )
    
    with col4:
        contacted_leads = calls_data.get("contacted_leads", 0)
        bilingual_metric(
            label_es="📋 Leads Contactados",
            label_en="📋 Contacted Leads",
            value=format_number(contacted_leads),
            help_es="Total de leads contactados",
            help_en="Total contacted leads"
        )

def render_conversion_metrics(date_range):
    """Render detailed conversion metrics."""
    bilingual_subheader(t("detailed_metrics", "reports"))
    
    # Load data for analysis
    leads_df = DataService.get_leads_data(date_range, limit=5000)
    calls_df = DataService.get_calls_data(date_range, limit=5000)
    
    # Ensure we have DataFrames
    if isinstance(leads_df, dict):
        leads_df = pd.DataFrame()
    if isinstance(calls_df, dict):
        calls_df = pd.DataFrame()
    
    # Calculate metrics
    total_leads = len(leads_df) if not leads_df.empty else 0
    total_calls = len(calls_df) if not calls_df.empty else 0
    
    contacted_leads = 0
    converted_leads = 0
    successful_calls = 0
    
    if not leads_df.empty and "estado_lead" in leads_df.columns:
        contacted_leads = len(leads_df[leads_df["estado_lead"] != "no_contactado"])
        converted_leads = len(leads_df[leads_df["estado_lead"].isin(["calificado", "cotizacion_gratis"])])
    
    if not calls_df.empty and "resultado_llamada" in calls_df.columns:
        successful_calls = len(calls_df[calls_df["resultado_llamada"] == "exitosa"])
    
    # Display metrics
    contact_rate = (contacted_leads / total_leads * 100) if total_leads > 0 else 0
    conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
    call_success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
    calls_per_lead = total_calls / total_leads if total_leads > 0 else 0
    
    bilingual_metric(t("contact_rate", "reports"), f"{contact_rate:.1f}%", delta=f"{contacted_leads}/{total_leads}")
    bilingual_metric(t("conversion_rate", "reports"), f"{conversion_rate:.1f}%", delta=f"{converted_leads}/{total_leads}")
    bilingual_metric(t("call_success", "reports"), f"{call_success_rate:.1f}%", delta=f"{successful_calls}/{total_calls}")
    bilingual_metric(t("calls_per_lead", "reports"), f"{calls_per_lead:.1f}", delta=f"{total_calls} {t('calls', 'dashboard')}")

def render_conversion_funnel_chart(date_range):
    """Render conversion funnel chart."""
    bilingual_subheader(t("conversion_funnel", "reports"))
    
    funnel_data = DataService.get_conversion_funnel(date_range)
    
    if funnel_data:
        # Create funnel chart
        fig_funnel = go.Figure(go.Funnel(
            y=list(funnel_data.keys()),
            x=list(funnel_data.values()),
            textinfo="value+percent initial",
            marker=dict(
                color=["#3498db", "#f39c12", "#2ecc71", "#e74c3c"],
                line=dict(width=2, color="white")
            )
        ))
        
        fig_funnel.update_layout(
            title=t("lead_conversion_funnel"),
            height=400,
            font=dict(size=12)
        )
        
        st.plotly_chart(fig_funnel, use_container_width=True)
    else:
        st.info(t("no_funnel_data", "dashboard"))

def render_leads_evolution_chart(date_range):
    """Render leads evolution over time."""
    bilingual_subheader(t("leads_evolution", "reports"))
    
    leads_evolution = DataService.get_leads_evolution(date_range)
    
    if not leads_evolution.empty:
        fig_evolution = px.line(
            leads_evolution,
            x='fecha',
            y='total_leads',
            title=t("daily_leads_evolution", "dashboard"),
            markers=True
        )
        fig_evolution.update_traces(line_color='#2ecc71', marker_color='#2ecc71')
        fig_evolution.update_layout(
            height=400,
            xaxis_title=t("date", "dashboard"),
            yaxis_title=t("number_of_leads", "dashboard")
        )
        st.plotly_chart(fig_evolution, use_container_width=True)
    else:
        st.info(t("no_leads_evolution_data", "dashboard"))

def render_daily_calls_chart(date_range):
    """Render daily calls volume."""
    bilingual_subheader(t("call_volume", "reports"))
    
    calls_volume = DataService.get_daily_calls_volume(date_range)
    
    if not calls_volume.empty:
        fig_calls = px.line(
            calls_volume,
            x='fecha',
            y='total_llamadas',
            title=t("daily_calls_volume", "dashboard"),
            markers=True
        )
        fig_calls.update_traces(line_color='#3498db', marker_color='#3498db')
        fig_calls.update_layout(
            height=400,
            xaxis_title=t("date", "dashboard"),
            yaxis_title=t("number_of_calls", "dashboard")
        )
        st.plotly_chart(fig_calls, use_container_width=True)
    else:
        st.info(t("no_call_volume_data", "dashboard"))

def render_calls_by_result_chart(date_range):
    """Render calls distribution by result."""
    bilingual_subheader(t("results_distribution", "reports"))
    
    results_data = DataService.get_calls_by_result(date_range)
    
    if not results_data.empty:
        # Color mapping for call results
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
            title=t("call_results_distribution", "dashboard"),
            color_discrete_sequence=colors
        )
        fig_results.update_traces(textposition='inside', textinfo='percent+label')
        fig_results.update_layout(height=400)
        st.plotly_chart(fig_results, use_container_width=True)
    else:
        st.info(t("no_results_data", "dashboard"))

def render_leads_by_status_chart(date_range):
    """Render leads distribution by status."""
    bilingual_subheader(t("lead_status", "reports"))
    
    leads_df = DataService.get_leads_data(date_range, limit=5000)
    
    if isinstance(leads_df, dict):
        leads_df = pd.DataFrame()
    
    if not leads_df.empty and "estado_lead" in leads_df.columns:
        estado_counts = leads_df["estado_lead"].value_counts()
        
        # Color mapping for estados
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
            title=t("lead_status", "dashboard"),
            color_discrete_sequence=colors
        )
        fig_estado.update_traces(textposition='inside', textinfo='percent+label')
        fig_estado.update_layout(height=400)
        st.plotly_chart(fig_estado, use_container_width=True)
    else:
        st.info(t("no_leads_distribution_data", "dashboard"))

def render_correlation_analysis(date_range):
    """Render correlation analysis between leads and calls."""
    bilingual_subheader(t("correlation_analysis", "reports"))
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### 📊 {t('leads_calls_correlation', 'dashboard')}")
        
        # Load data
        leads_df = DataService.get_leads_data(date_range, limit=5000)
        calls_df = DataService.get_calls_data(date_range, limit=5000)
        
        if isinstance(leads_df, dict):
            leads_df = pd.DataFrame()
        if isinstance(calls_df, dict):
            calls_df = pd.DataFrame()
        
        if not leads_df.empty and not calls_df.empty:
            # Calculate daily metrics
            if "fecha_creacion" in leads_df.columns:
                daily_leads = leads_df.groupby(pd.to_datetime(leads_df['fecha_creacion']).dt.date).size()
            else:
                daily_leads = pd.Series()
            
            if "fecha_llamada" in calls_df.columns:
                daily_calls = calls_df.groupby(pd.to_datetime(calls_df['fecha_llamada']).dt.date).size()
            else:
                daily_calls = pd.Series()
            
            if not daily_leads.empty and not daily_calls.empty:
                # Merge data
                correlation_df = pd.DataFrame({
                    'leads': daily_leads,
                    'calls': daily_calls
                }).fillna(0)
                
                if len(correlation_df) > 1:
                    correlation = correlation_df['leads'].corr(correlation_df['calls'])
                    st.metric("Correlación", f"{correlation:.3f}")
                    
                    # Scatter plot
                    fig_corr = px.scatter(
                        correlation_df,
                        x='leads',
                        y='calls',
                        title="Correlación Leads vs Llamadas",
                        trendline="ols"
                    )
                    fig_corr.update_layout(height=300)
                    st.plotly_chart(fig_corr, use_container_width=True)
                else:
                    st.info(t("insufficient_correlation_data", "common"))
            else:
                st.info(t("no_temporal_data_available", "common"))
        else:
            st.info(t("no_data_available_analysis", "common"))
        
        # Análisis de eficiencia por período
        st.markdown(f"#### 🎯 {t('efficiency_by_period', 'common')}")
        
        # Weekly efficiency analysis
        if not calls_df.empty and "fecha_llamada" in calls_df.columns and "resultado_llamada" in calls_df.columns:
            calls_df['week'] = pd.to_datetime(calls_df['fecha_llamada']).dt.isocalendar().week
            weekly_efficiency = calls_df.groupby('week').agg({
                'resultado_llamada': ['count', lambda x: (x == 'exitosa').sum()]
            })
            weekly_efficiency.columns = ['total_calls', 'successful_calls']
            weekly_efficiency['efficiency'] = (weekly_efficiency['successful_calls'] / weekly_efficiency['total_calls'] * 100).round(1)
            
            if not weekly_efficiency.empty:
                fig_efficiency = px.bar(
                    weekly_efficiency.reset_index(),
                    x='week',
                    y='efficiency',
                    title="Eficiencia Semanal (%)",
                    color='efficiency',
                    color_continuous_scale="viridis"
                )
                fig_efficiency.update_layout(height=300)
                st.plotly_chart(fig_efficiency, use_container_width=True)
            else:
                st.info(t('no_efficiency_data', 'reports'))
        else:
            st.info(t('no_call_data', 'reports'))

def render_executive_summary(date_range):
    """Render executive summary with insights and recommendations."""
    st.subheader(f"💡 {t('executive_summary', 'reports')}")
    
    # Load summary data
    leads_data = DataService.get_leads_summary()
    calls_data = DataService.get_calls_summary(date_range)
    
    # Generate insights
    insights = []
    
    contact_rate = calls_data.get("contact_rate", 0)
    conversion_rate = calls_data.get("conversion_rate", 0)
    success_rate = calls_data.get("success_rate", 0)
    
    if contact_rate > 70:
        insights.append(f"✅ **{t('excellent_contact_rate', 'reports')}**: {t('team_contacting_effectively', 'reports')}")
    elif contact_rate > 50:
        insights.append(f"⚠️ **{t('moderate_contact_rate', 'reports')}**: {t('contact_strategy_improvement_opportunity', 'reports')}")
    else:
        insights.append(f"🔴 **{t('low_contact_rate', 'reports')}**: {t('urgent_contact_strategy_review', 'reports')}")
    
    if conversion_rate > 15:
        insights.append(f"🎯 **{t('high_conversion', 'reports')}**: {t('leads_responding_well_value_proposition', 'reports')}")
    elif conversion_rate > 8:
        insights.append(f"📈 **{t('average_conversion', 'reports')}**: {t('conversion_optimization_potential', 'reports')}")
    else:
        insights.append(f"📉 **{t('low_conversion', 'reports')}**: {t('lead_quality_sales_process_review', 'reports')}")
    
    if success_rate > 60:
        insights.append(f"📞 **{t('excellent_call_performance', 'reports')}**: {t('agents_handling_calls_effectively', 'reports')}")
    else:
        insights.append(f"📞 **{t('call_opportunity', 'reports')}**: {t('consider_additional_training', 'reports')}")
    
    # Display insights
    for insight in insights:
        st.markdown(insight)
    
    # Recommendations
    st.markdown(f"#### 🎯 {t('recommendations', 'reports')}")
    recommendations = [
        f"📊 **{t('continuous_monitoring', 'reports')}**: {t('review_metrics_weekly', 'reports')}",
        f"🎯 **{t('schedule_optimization', 'reports')}**: {t('analyze_best_contact_hours', 'reports')}",
        f"📈 **{t('team_training', 'reports')}**: {t('implement_data_based_training', 'reports')}",
        f"🔍 **{t('lead_segmentation', 'reports')}**: {t('prioritize_high_conversion_leads', 'reports')}",
        f"📞 **{t('script_improvement', 'reports')}**: {t('optimize_call_scripts', 'reports')}"
    ]
    
    for rec in recommendations:
        st.markdown(rec)