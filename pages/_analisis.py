"""
Página de Análisis y Correlación - Call Analytics Dashboard
Análisis avanzado entre leads_pluscargo_simple y call_results_pluscargo_simple
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from services.data_service import DataService
from utils.formatters import format_number, format_percentage
from utils.i18n_helpers import t

def render_analisis_page():
    """Renderiza la página de análisis y correlación"""
    
    # Título principal
    st.title(f"📈 {t('analysis_correlation', 'common')}")
    st.markdown("---")
    
    # Inicializar servicio de datos
    data_service = DataService()
    
    # Obtener datos
    date_range = (datetime.now() - timedelta(days=30), datetime.now())
    leads_data = data_service.get_leads_data()
    calls_data = data_service.get_calls_data(date_range)
    
    if leads_data.empty and calls_data.empty:
        st.warning(t('no_data_available', 'common'))
        return
    
    # Métricas de conversión
    st.header(f"🎯 {t('conversion_metrics', 'reports')}")
    
    if not leads_data.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_leads = len(leads_data)
            st.metric(t('total_leads', 'management'), format_number(total_leads))
        
        with col2:
            contacted = len(leads_data[leads_data['intentos_llamada'] > 0])
            contact_rate = (contacted / total_leads * 100) if total_leads > 0 else 0
            st.metric(
                t('contact_rate', 'reports'),
                f"{contact_rate:.1f}%",
                format_number(contacted)
            )
        
        with col3:
            interested = len(leads_data[leads_data['estado_lead'].isin([t('lead_status_interested', 'common'), t('lead_status_follow_up', 'common')])])
            interest_rate = (interested / contacted * 100) if contacted > 0 else 0
            st.metric(
                t('interest_rate', 'reports'),
                f"{interest_rate:.1f}%",
                format_number(interested)
            )
        
        with col4:
            converted = len(leads_data[leads_data['estado_lead'] == t('lead_status_converted', 'common')])
            conversion_rate = (converted / total_leads * 100) if total_leads > 0 else 0
            st.metric(
                t('conversion_rate', 'management'),
                f"{conversion_rate:.1f}%",
                format_number(converted)
            )
    
    # Análisis de embudo de conversión
    st.markdown("---")
    st.header(f"🔄 {t('conversion_funnel', 'management')}")
    
    if not leads_data.empty:
        # Calcular métricas del embudo
        total = len(leads_data)
        contacted = len(leads_data[leads_data['intentos_llamada'] > 0])
        interested = len(leads_data[leads_data['estado_lead'].isin([t('lead_status_interested', 'common'), t('lead_status_follow_up', 'common')])])
        qualified = len(leads_data[leads_data['estado_lead'] == t('lead_status_qualified', 'common')])
        converted = len(leads_data[leads_data['estado_lead'] == t('lead_status_converted', 'common')])
        
        # Crear gráfico de embudo
        funnel_data = {
            t('total_leads', 'management'): total,
            t('contacted', 'management'): contacted,
            t('interested', 'management'): interested,
            t('qualified', 'reports'): qualified,
            t('converted', 'management'): converted
        }
        
        fig_funnel = go.Figure(go.Funnel(
            y=list(funnel_data.keys()),
            x=list(funnel_data.values()),
            textinfo="value+percent initial",
            marker_color=["#ff6b6b", "#4ecdc4", "#45b7d1", "#feca57", "#48dbfb"]
        ))
        fig_funnel.update_layout(
            title=t('conversion_funnel', 'management'),
            height=400
        )
        st.plotly_chart(fig_funnel, use_container_width=True)
        
        # Detalles del embudo
        st.subheader(f"📊 {t('funnel_details', 'reports')}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**{t('contact_conversion', 'reports')}:** {(contacted/total*100):.1f}%")
            st.write(f"**{t('interest_conversion', 'reports')}:** {(interested/contacted*100) if contacted > 0 else 0:.1f}%")
        
        with col2:
            st.write(f"**{t('qualification_conversion', 'reports')}:** {(qualified/interested*100) if interested > 0 else 0:.1f}%")
            st.write(f"**{t('final_conversion', 'reports')}:** {(converted/total*100):.1f}%")
    
    # Análisis temporal
    st.markdown("---")
    st.header(f"📅 {t('temporal_analysis', 'reports')}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"📈 {t('leads_evolution', 'reports')}")
        
        if not leads_data.empty and 'fecha_creacion' in leads_data.columns:
            # Evolución de leads por día
            leads_data['fecha'] = pd.to_datetime(leads_data['fecha_creacion']).dt.date
            daily_leads = leads_data.groupby('fecha').size().reset_index(name='count')
            
            fig_leads = px.line(
                daily_leads,
                x='fecha',
                y='count',
                title=t('daily_leads_creation', 'reports'),
                labels={'fecha': t('date', 'common'), 'count': t('leads', 'common')}
            )
            st.plotly_chart(fig_leads, use_container_width=True)
        else:
            st.info(t('no_temporal_data', 'reports'))
    
    with col2:
        st.subheader(f"📞 {t('call_volume', 'reports')}")
        
        if not calls_data.empty and 'fecha_llamada' in calls_data.columns:
            # Volumen de llamadas por día
            calls_data['fecha'] = pd.to_datetime(calls_data['fecha_llamada']).dt.date
            daily_calls = calls_data.groupby('fecha').size().reset_index(name='count')
            
            fig_calls = px.line(
                daily_calls,
                x='fecha',
                y='count',
                title=t('daily_call_volume', 'reports'),
                labels={'fecha': t('date', 'common'), 'count': t('calls', 'common')}
            )
            st.plotly_chart(fig_calls, use_container_width=True)
        else:
            st.info(t('no_call_data', 'reports'))
    
    # Análisis de calidad de leads
    st.markdown("---")
    st.header(f"🎯 {t('lead_quality_analysis', 'reports')}")
    
    if not leads_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"🏭 {t('performance_by_industry', 'reports')}")
            
            if 'rubro' in leads_data.columns:
                # Performance por industria
                industry_performance = leads_data.groupby('rubro').agg({
                    'estado_lead': 'count',
                    'intentos_llamada': 'mean'
                }).round(2)
                industry_performance.columns = [t('total_leads', 'management'), t('avg_attempts', 'reports')]
                
                # Calcular tasa de conversión por industria
                conversion_by_industry = leads_data[leads_data['estado_lead'] == t('lead_status_converted', 'common')].groupby('rubro').size()
                total_by_industry = leads_data.groupby('rubro').size()
                conversion_rate_by_industry = (conversion_by_industry / total_by_industry * 100).fillna(0)
                
                industry_performance[t('conversion_rate', 'management')] = conversion_rate_by_industry
                
                # Mostrar top 10 industrias
                top_industries = industry_performance.head(10)
                
                fig_industry = px.bar(
                    x=top_industries.index,
                    y=top_industries[t('conversion_rate', 'management')],
                    title=t('conversion_rate_by_industry', 'reports'),
                    labels={'x': t('industry', 'common'), 'y': t('conversion_rate', 'management')}
                )
                fig_industry.update_xaxis(tickangle=45)
                st.plotly_chart(fig_industry, use_container_width=True)
            else:
                st.info(t('no_industry_data', 'reports'))
        
        with col2:
            st.subheader(f"📊 {t('performance_by_source', 'reports')}")
            
            if 'fuente' in leads_data.columns:
                # Performance por fuente
                source_performance = leads_data.groupby('fuente').agg({
                    'estado_lead': 'count',
                    'intentos_llamada': 'mean'
                }).round(2)
                source_performance.columns = [t('total_leads', 'management'), t('avg_attempts', 'reports')]
                
                # Calcular tasa de conversión por fuente
                conversion_by_source = leads_data[leads_data['estado_lead'] == t('lead_status_converted', 'common')].groupby('fuente').size()
                total_by_source = leads_data.groupby('fuente').size()
                conversion_rate_by_source = (conversion_by_source / total_by_source * 100).fillna(0)
                
                source_performance[t('conversion_rate', 'management')] = conversion_rate_by_source
                
                fig_source = px.pie(
                    values=source_performance[t('total_leads', 'management')],
                    names=source_performance.index,
                    title=t('leads_by_source', 'reports')
                )
                st.plotly_chart(fig_source, use_container_width=True)
            else:
                st.info(t('no_source_data', 'reports'))
    
    # Análisis de performance de llamadas
    st.markdown("---")
    st.header(f"📞 {t('call_performance_analysis', 'reports')}")
    
    if not calls_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"👥 {t('top_agents', 'reports')}")
            
            if 'agent_id' in calls_data.columns:
                # Performance por agente
                agent_performance = calls_data.groupby('agent_id').agg({
                    'resultado_llamada': 'count',
                    'duracion_segundos': 'mean'
                }).round(2)
                agent_performance.columns = [t('total_calls', 'management'), t('avg_duration', 'reports')]
                
                # Calcular tasa de éxito por agente
                successful_calls = calls_data[calls_data['resultado_llamada'].isin([t('call_result_successful', 'common'), t('lead_status_interested', 'common')])].groupby('agent_id').size()
                total_calls_agent = calls_data.groupby('agent_id').size()
                success_rate_agent = (successful_calls / total_calls_agent * 100).fillna(0)
                
                agent_performance[t('success_rate', 'reports')] = success_rate_agent
                
                # Top 10 agentes
                top_agents = agent_performance.nlargest(10, t('success_rate', 'reports'))
                
                fig_agents = px.bar(
                    x=top_agents.index,
                    y=top_agents[t('success_rate', 'reports')],
                    title=t('success_rate_by_agent', 'reports'),
                    labels={'x': t('agent', 'common'), 'y': t('success_rate', 'reports')}
                )
                st.plotly_chart(fig_agents, use_container_width=True)
            else:
                st.info(t('no_agent_data', 'reports'))
        
        with col2:
            st.subheader(f"⏰ {t('hourly_analysis', 'reports')}")
            
            if 'fecha_llamada' in calls_data.columns:
                # Análisis por hora del día
                calls_data['hora'] = pd.to_datetime(calls_data['fecha_llamada']).dt.hour
                hourly_calls = calls_data.groupby('hora').size().reset_index(name='count')
                
                # Calcular tasa de éxito por hora
                successful_hourly = calls_data[calls_data['resultado_llamada'].isin([t('call_result_successful', 'common'), t('lead_status_interested', 'common')])].groupby('hora').size()
                total_hourly = calls_data.groupby('hora').size()
                success_rate_hourly = (successful_hourly / total_hourly * 100).fillna(0).reset_index(name='success_rate')
                
                fig_hourly = px.line(
                    success_rate_hourly,
                    x='hora',
                    y='success_rate',
                    title=t('success_rate_by_hour', 'reports'),
                    labels={'hora': t('hour', 'common'), 'success_rate': t('success_rate', 'reports')}
                )
                st.plotly_chart(fig_hourly, use_container_width=True)
            else:
                st.info(t('no_hourly_data', 'reports'))
    
    # Insights y recomendaciones
    st.markdown("---")
    st.header(f"💡 {t('insights_recommendations', 'reports')}")
    
    # Generar insights automáticos
    insights = []
    
    if not leads_data.empty:
        # Insight sobre tasa de conversión
        if conversion_rate > 10:
            insights.append(f"✅ {t('good_conversion_rate', 'reports')}: {conversion_rate:.1f}%")
        else:
            insights.append(f"⚠️ {t('low_conversion_rate', 'reports')}: {conversion_rate:.1f}%")
        
        # Insight sobre contacto
        if contact_rate > 70:
            insights.append(f"✅ {t('good_contact_rate', 'reports')}: {contact_rate:.1f}%")
        else:
            insights.append(f"⚠️ {t('low_contact_rate', 'reports')}: {contact_rate:.1f}%")
    
    if not calls_data.empty and 'duracion_segundos' in calls_data.columns:
        avg_duration = calls_data['duracion_segundos'].mean() / 60  # Convertir a minutos
        if avg_duration > 5:
            insights.append(f"✅ {t('good_call_duration', 'reports')}: {avg_duration:.1f} {t('minutes', 'common')}")
        else:
            insights.append(f"⚠️ {t('short_call_duration', 'reports')}: {avg_duration:.1f} {t('minutes', 'common')}")
    
    # Mostrar insights
    for insight in insights:
        st.markdown(insight)
    
    # Recomendaciones
    st.subheader(f"🎯 {t('actionable_recommendations', 'reports')}")
    
    recommendations = [
        t('focus_high_conversion_industries', 'reports'),
        t('optimize_call_timing', 'reports'),
        t('improve_lead_qualification', 'reports'),
        t('train_underperforming_agents', 'reports'),
        t('increase_follow_up_frequency', 'reports')
    ]
    
    for rec in recommendations:
        st.markdown(rec)
    
    # Resumen ejecutivo
    st.markdown("---")
    st.header(f"📋 {t('executive_summary', 'reports')}")
    
    if not leads_data.empty or not calls_data.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📊 {t('key_metrics', 'reports')}")
            st.write(f"**{t('total_leads', 'management')}:** {format_number(total_leads) if not leads_data.empty else 0}")
            st.write(f"**{t('total_calls', 'management')}:** {format_number(len(calls_data)) if not calls_data.empty else 0}")
            st.write(f"**{t('contact_rate', 'reports')}:** {contact_rate:.1f}%" if not leads_data.empty else "0%")
            st.write(f"**{t('conversion_rate', 'management')}:** {conversion_rate:.1f}%" if not leads_data.empty else "0%")
        
        with col2:
            st.subheader(f"🎯 {t('goals_vs_reality', 'reports')}")
            # Aquí se pueden agregar métricas de objetivos vs realidad
            st.info(t('goals_tracking_development', 'reports'))

def render():
    """Main render function called by app.py"""
    render_analisis_page()

if __name__ == "__main__":
    render_analisis_page()