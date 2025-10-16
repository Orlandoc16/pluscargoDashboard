"""
Dashboard Principal - Vista ejecutiva con KPIs y tendencias
Enfocado en leads_pluscargo_basic y call_results_pluscargo_basic
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta
from services.data_service import DataService
from services.supabase_client import test_connection
from utils.i18n_helpers import t
import logging

logger = logging.getLogger(__name__)

def render():
    """Render the simplified dashboard page."""
    try:
        # Test connection
        connection_status = test_connection_status()
        
        # Get date range from session state
        date_range = st.session_state.get('date_range', (
            datetime.now().date() - timedelta(days=30),
            datetime.now().date()
        ))
        
        # Show connection status
        if connection_status == 'connected':
            st.success(f"✅ {t('connected_supabase_realtime', 'dashboard')}")
        else:
            st.warning(f"⚠️ {t('no_connection_supabase', 'dashboard')}")
        
        # Section 1: Hero KPIs
        render_main_kpis(date_range)
        
        # Section 2: Análisis Temporal
        st.markdown(f"""
        <div style="background: #e3f2fd; padding: 1.5rem; border-radius: 0.75rem; margin: 2rem 0 1rem 0;">
            <h3 style="margin: 0; color: #1565c0;">📊 {t('temporal_analysis', 'dashboard')}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #1976d2;">{t('trends_evolution_time', 'dashboard')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([2, 1])
        with col1:
            render_leads_evolution_chart(date_range)
        with col2:
            render_daily_calls_chart(date_range)
        
        # Section 3: Distribución y Detalles
        st.markdown(f"""
        <div style="background: #f3e5f5; padding: 1.5rem; border-radius: 0.75rem; margin: 2rem 0 1rem 0;">
            <h3 style="margin: 0; color: #7b1fa2;">🎯 {t('distribution_results', 'dashboard')}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #8e24aa;">{t('results_performance_analysis', 'dashboard')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        col3, col4 = st.columns(2)
        with col3:
            render_calls_by_result_chart(date_range)
        with col4:
            render_conversion_funnel_chart(date_range)
        
        # Section 4: Insights y Acciones
        st.markdown(f"""
        <div style="background: #e8f5e8; padding: 1.5rem; border-radius: 0.75rem; margin: 2rem 0 1rem 0;">
            <h3 style="margin: 0; color: #2e7d32;">💡 {t('insights_recommendations', 'dashboard')}</h3>
            <p style="margin: 0.5rem 0 0 0; color: #388e3c;">{t('executive_summary_actions', 'dashboard')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        render_executive_summary(date_range)
        
    except Exception as e:
        st.error(f"{t('error_loading_dashboard', 'dashboard')}: {e}")
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
    """Render KPIs with improved hierarchy and visual organization."""
    
    # Get data with loading indicator
    with st.spinner(t('loading_metrics', 'dashboard')):
        leads_data = DataService.get_leads_summary()
        calls_data = DataService.get_calls_summary(date_range)
    
    # Hero Section - Primary KPIs
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); 
                padding: 2rem; border-radius: 1rem; margin-bottom: 2rem; color: white;">
        <h2 style="margin: 0; color: white;">🎯 {t('main_metrics', 'dashboard')}</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{t('executive_performance_view', 'dashboard')}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Primary KPIs - 3 main metrics in larger cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        conversion_rate = calls_data.get('conversion_rate', 0)
        converted_leads = calls_data.get('converted_leads', 0)
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 0.75rem; 
                    border-left: 5px solid #28a745; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)
        st.metric(
            label=f"✅ {t('conversion_rate', 'dashboard')}",
            value=f"{conversion_rate:.1f}%",
            delta=f"{converted_leads} {t('leads_converted', 'dashboard')}",
            help=t('conversion_rate_help', 'dashboard')
        )
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        contact_rate = calls_data.get('contact_rate', 0)
        contacted_leads = calls_data.get('contacted_leads', 0)
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 0.75rem; 
                    border-left: 5px solid #007bff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)
        st.metric(
            label=f"📈 {t('contact_rate', 'dashboard')}",
            value=f"{contact_rate:.1f}%",
            delta=f"{contacted_leads} {t('leads_contacted', 'dashboard')}",
            help=t('contact_rate_help', 'dashboard')
        )
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col3:
        success_rate = calls_data.get('success_rate', 0)
        successful_calls = int(calls_data.get('total_calls', 0) * success_rate / 100)
        total_calls = calls_data.get('total_calls', 0)
        st.markdown("""
        <div style="background: white; padding: 1.5rem; border-radius: 0.75rem; 
                    border-left: 5px solid #ffc107; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        """, unsafe_allow_html=True)
        st.metric(
            label=f"🎯 {t('call_success', 'dashboard')}",
            value=f"{success_rate:.1f}%",
            delta=f"{successful_calls}/{total_calls} {t('successful', 'dashboard')}",
            help=t('call_success_help', 'dashboard')
        )
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Secondary KPIs - Supporting metrics in smaller cards
    st.markdown(f"""
    <div style="background: #f8f9fa; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
        <h4 style="margin: 0; color: #495057;">📊 {t('support_metrics', 'dashboard')}</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col4, col5, col6, col7 = st.columns(4)
    
    with col4:
        total_leads = leads_data.get('total_active_leads', 0)
        st.metric(
            label=f"👥 {t('active_leads', 'dashboard')}",
            value=f"{total_leads:,}",
            help=t('active_leads_help', 'dashboard')
        )
    
    with col5:
        calls_per_lead = calls_data.get('calls_per_lead', 0)
        st.metric(
            label=f"📞 {t('calls_per_lead', 'dashboard')}",
            value=f"{calls_per_lead:.1f}",
            help=t('calls_per_lead_help', 'dashboard')
        )
    
    with col6:
        total_calls = calls_data.get('total_calls', 0)
        st.metric(
            label=f"📱 {t('total_calls', 'dashboard')}",
            value=f"{total_calls:,}",
            help=t('total_calls_help', 'dashboard')
        )
    
    with col7:
        # Calculate efficiency metric
        efficiency = (conversion_rate * contact_rate) / 100 if contact_rate > 0 else 0
        st.metric(
            label=f"⚡ {t('efficiency', 'dashboard')}",
            value=f"{efficiency:.1f}%",
            help=t('efficiency_help', 'dashboard')
        )

def render_leads_evolution_chart(date_range):
    """Render leads evolution by status chart with enhanced visual feedback."""
    st.markdown(f"#### 📈 {t('leads_evolution_status', 'dashboard')}")
    
    # Loading state with spinner
    with st.spinner(t('loading_leads_evolution', 'dashboard')):
        try:
            leads_evolution = DataService.get_leads_evolution(date_range)
            
            if leads_evolution.empty:
                st.info(f"📊 {t('no_leads_evolution_data', 'dashboard')}")
                return
            
            # Success feedback
            st.success(f"✅ {t('data_loaded', 'dashboard')}: {len(leads_evolution)} {t('records_found', 'dashboard')}")
            
            fig = px.line(
                leads_evolution,
                x='fecha',
                y='cantidad',
                color='estado_lead',
                title=t('leads_evolution_status', 'dashboard'),
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            
            # Enhanced chart styling
            fig.update_layout(
                height=350,
                showlegend=True,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                title=dict(font=dict(size=14, color='#2c3e50')),
                xaxis=dict(
                    title=t('date', 'dashboard'),
                    gridcolor='rgba(128,128,128,0.2)',
                    title_font=dict(color='#34495e')
                ),
                yaxis=dict(
                    title=t('leads_quantity', 'dashboard'),
                    gridcolor='rgba(128,128,128,0.2)',
                    title_font=dict(color='#34495e')
                )
            )
            
            # Add hover template for better UX
            fig.update_traces(
                hovertemplate=f"<b>%{{fullData.name}}</b><br>" +
                             f"{t('date', 'dashboard')}: %{{x}}<br>" +
                             f"{t('quantity', 'dashboard')}: %{{y}}<br>" +
                             "<extra></extra>"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ {t('error_loading_leads_evolution_chart', 'dashboard')}: {e}")
            st.info(f"💡 {t('suggestion_check_connection_dates', 'dashboard')}")

def render_daily_calls_chart(date_range):
    """Render daily calls volume chart with enhanced visual feedback."""
    st.markdown(f"#### 📞 {t('daily_calls_volume', 'dashboard')}")
    
    # Loading state with spinner
    with st.spinner(t('loading_calls_volume', 'dashboard')):
        try:
            daily_calls = DataService.get_daily_calls_volume(date_range)
            
            if daily_calls.empty:
                st.info(f"📊 {t('no_daily_calls_data', 'dashboard')}")
                return
            
            # Success feedback
            total_calls = daily_calls['total_llamadas'].sum()
            st.success(f"✅ {len(daily_calls)} {t('days_with', 'dashboard')} {total_calls} {t('total_calls_lowercase', 'dashboard')}")
            
            fig = px.bar(
                daily_calls,
                x='fecha',
                y='total_llamadas',
                title=t('daily_calls_volume', 'dashboard'),
                color='total_llamadas',
                color_continuous_scale='Blues',
                text='total_llamadas'
            )
            
            # Enhanced chart styling
            fig.update_layout(
                height=350,
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                title=dict(font=dict(size=14, color='#2c3e50')),
                xaxis=dict(
                    title=t('date', 'dashboard'),
                    gridcolor='rgba(128,128,128,0.2)',
                    title_font=dict(color='#34495e')
                ),
                yaxis=dict(
                    title=t('number_of_calls', 'dashboard'),
                    gridcolor='rgba(128,128,128,0.2)',
                    title_font=dict(color='#34495e')
                )
            )
            
            # Add hover template and text styling
            fig.update_traces(
                texttemplate='%{text}',
                textposition='outside',
                hovertemplate=f"<b>{t('daily_calls', 'dashboard')}</b><br>" +
                             f"{t('date', 'dashboard')}: %{{x}}<br>" +
                             f"{t('total', 'dashboard')}: %{{y}} {t('calls_lowercase', 'dashboard')}<br>" +
                             "<extra></extra>"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ {t('error_loading_daily_calls_chart', 'dashboard')}: {e}")
            st.info(f"💡 {t('suggestion_check_connection_dates', 'dashboard')}")

def render_calls_by_result_chart(date_range):
    """Render calls distribution by result chart with enhanced visual feedback."""
    st.markdown(f"#### 🎯 {t('distribution_by_result', 'dashboard')}")
    
    # Loading state with spinner
    with st.spinner(t('loading_results_distribution', 'dashboard')):
        try:
            calls_by_result = DataService.get_calls_by_result(date_range)
            
            if calls_by_result.empty:
                st.info(f"📊 {t('no_call_results_data', 'dashboard')}")
                return
            
            # Success feedback
            total_calls = calls_by_result['cantidad'].sum()
            st.success(f"✅ {total_calls} {t('calls_analyzed_by_result', 'dashboard')}")
            
            fig = px.pie(
                calls_by_result,
                values='cantidad',
                names='resultado_llamada',
                title=t('call_results_distribution', 'dashboard'),
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            
            # Enhanced chart styling
            fig.update_layout(
                height=350,
                font=dict(size=12),
                title=dict(font=dict(size=14, color='#2c3e50')),
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05
                )
            )
            
            # Enhanced hover and text info
            fig.update_traces(
                textposition='inside',
                textinfo='percent+label',
                hovertemplate=f"<b>%{{label}}</b><br>" +
                             f"{t('quantity', 'dashboard')}: %{{value}}<br>" +
                             f"{t('percentage', 'dashboard')}: %{{percent}}<br>" +
                             "<extra></extra>"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ {t('error_loading_results_chart', 'dashboard')}: {e}")
            st.info(f"💡 {t('suggestion_check_connection_dates', 'dashboard')}")

def render_conversion_funnel_chart(date_range):
    """Render conversion funnel chart with enhanced visual feedback."""
    st.markdown(f"#### 🔄 {t('conversion_funnel', 'dashboard')}")
    
    # Loading state with spinner
    with st.spinner(t('loading_conversion_funnel', 'dashboard')):
        try:
            funnel_data = DataService.get_conversion_funnel(date_range)
            
            if not funnel_data:
                st.info(f"📊 {t('no_funnel_data', 'dashboard')}")
                return
            
            # Success feedback
            total_leads = list(funnel_data.values())[0] if funnel_data else 0
            st.success(f"✅ {t('funnel_generated_with', 'dashboard')} {total_leads} {t('initial_leads', 'dashboard')}")
            
            fig = go.Figure(go.Funnel(
                y = list(funnel_data.keys()),
                x = list(funnel_data.values()),
                textinfo = "value+percent initial",
                marker = dict(
                    color = ["#3498db", "#2ecc71", "#f39c12", "#e74c3c", "#9b59b6"],
                    line = dict(width = 2, color = "white")
                )
            ))
            
            # Enhanced chart styling
            fig.update_layout(
                height=350,
                title=dict(
                    text=t('leads_conversion_funnel', 'dashboard'),
                    font=dict(size=14, color='#2c3e50')
                ),
                font=dict(size=12),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            
            # Add annotations for better understanding
            fig.add_annotation(
                text=f"💡 {t('funnel_stage_explanation', 'dashboard')}",
                xref="paper", yref="paper",
                x=0.5, y=-0.1,
                showarrow=False,
                font=dict(size=10, color='#7f8c8d')
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
        except Exception as e:
            st.error(f"❌ {t('error_loading_funnel', 'dashboard')}: {e}")
            st.info(f"💡 {t('suggestion_check_leads_calls_data', 'dashboard')}")

def render_executive_summary(date_range):
    """Render executive summary section."""
    st.markdown(f"### 📋 {t('executive_summary', 'dashboard')}")
    
    try:
        summary = DataService.get_executive_summary(date_range)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"#### 📊 {t('current_leads_status', 'dashboard')}")
            if summary.get('leads_distribution'):
                for estado, cantidad in summary['leads_distribution'].items():
                    st.write(f"• **{estado.title()}**: {cantidad} leads")
            else:
                st.info(t('no_leads_distribution_data', 'dashboard'))
        
        with col2:
            st.markdown(f"#### 📞 {t('calls_performance', 'dashboard')}")
            if summary.get('calls_performance'):
                perf = summary['calls_performance']
                st.write(f"• **{t('success_rate', 'dashboard')}**: {perf.get('success_rate', 0):.1f}%")
                st.write(f"• **{t('average_duration', 'dashboard')}**: {perf.get('avg_duration', 0):.1f} min")
                st.write(f"• **{t('best_time', 'dashboard')}**: {perf.get('best_hour', 'N/A')}")
            else:
                st.info(t('no_performance_data', 'dashboard'))
        
        # Recommendations
        st.markdown(f"#### 💡 {t('recommended_next_actions', 'dashboard')}")
        recommendations = generate_recommendations(summary)
        for rec in recommendations:
            st.write(f"• {rec}")
            
    except Exception as e:
        st.error(f"{t('error_executive_summary', 'dashboard')}: {e}")

def generate_recommendations(summary):
    """Generate actionable recommendations based on data."""
    recommendations = []
    
    try:
        # Based on leads distribution
        if summary.get('leads_distribution'):
            total_leads = sum(summary['leads_distribution'].values())
            new_leads = summary['leads_distribution'].get('nuevo', 0)
            
            if new_leads / total_leads > 0.5:
                recommendations.append(t('prioritize_new_leads_followup', 'dashboard'))
            
            if summary['leads_distribution'].get('no_contactado', 0) > 0:
                recommendations.append(t('contact_pending_first_call_leads', 'dashboard'))
        
        # Based on calls performance
        if summary.get('calls_performance'):
            success_rate = summary['calls_performance'].get('success_rate', 0)
            
            if success_rate < 50:
                recommendations.append(t('review_calls_strategy_improve_success', 'dashboard'))
            elif success_rate > 70:
                recommendations.append(t('maintain_current_strategy_excellent', 'dashboard'))
        
        # Default recommendations
        if not recommendations:
            recommendations = [
                t('review_uncontacted_leads_7_days', 'dashboard'),
                t('analyze_optimal_call_times', 'dashboard'),
                t('evaluate_agent_performance', 'dashboard')
            ]
            
    except Exception:
        recommendations = [t('review_data_system_configuration', 'dashboard')]
    
    return recommendations