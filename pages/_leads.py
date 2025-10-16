"""
Página de Leads - Call Analytics Dashboard
Enfocada exclusivamente en leads_pluscargo_basic
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from services.data_service import DataService
from utils.formatters import format_number, format_percentage
from utils.i18n_helpers import t
import logging

logger = logging.getLogger(__name__)

def render_leads_page():
    """Renderiza la página de gestión de leads"""
    
    # Título principal
    st.title(f"👥 {t('leads_management', 'common')}")
    st.markdown("---")
    
    # Inicializar servicio de datos
    data_service = DataService()
    
    # Filtros
    st.header(f"🔍 {t('filters', 'common')}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        estado_filter = st.selectbox(
            t('lead_status', 'common'),
            options=[t('all', 'common')] + data_service.get_lead_statuses(),
            key="leads_estado_filter"
        )
    
    with col2:
        rubro_filter = st.selectbox(
            t('industry', 'common'),
            options=[t('all', 'common')] + data_service.get_industries(),
            key="leads_rubro_filter"
        )
    
    with col3:
        fecha_filter = st.date_input(
            t('date_range', 'common'),
            value=[datetime.now() - timedelta(days=30), datetime.now()],
            key="leads_fecha_filter"
        )
    
    st.markdown("---")
    st.subheader(f"📄 {t('pagination', 'common')}")
    
    col1, col2 = st.columns(2)
    with col1:
        page_size = st.selectbox(
            t('records_per_page', 'common'),
            options=[10, 25, 50, 100],
            index=1,
            key="leads_page_size"
        )
    
    with col2:
        # Obtener total de leads para calcular páginas
        total_leads = data_service.get_leads_count(
            estado_filter if estado_filter != t('all', 'common') else None,
            rubro_filter if rubro_filter != t('all', 'common') else None,
            fecha_filter
        )
        
        total_pages = max(1, (total_leads + page_size - 1) // page_size)
        current_page = st.number_input(
            f"{t('page', 'common')} (1-{total_pages})",
            min_value=1,
            max_value=total_pages,
            value=1,
            key="leads_current_page"
        )
    
    # Obtener datos de leads
    leads_data = data_service.get_leads_data(
        estado_filter if estado_filter != t('all', 'common') else None,
        rubro_filter if rubro_filter != t('all', 'common') else None,
        fecha_filter,
        page_size,
        (current_page - 1) * page_size
    )
    
    st.markdown("---")
    st.header(f"📋 {t('leads_table', 'common')}")
    
    if not leads_data.empty:
        # Configurar columnas para mostrar
        display_columns = {
            'nombre': t('name', 'common'),
            'apellido': t('last_name', 'common'),
            'nombre_empresa': t('company', 'common'),
            'rubro': t('industry', 'common'),
            'estado_lead': t('status', 'common'),
            'telefono_contacto': t('phone', 'common'),
            'correo_contacto': t('email', 'common'),
            'intentos_llamada': t('call_attempts', 'common'),
            'fecha_creacion': t('created_date', 'common')
        }
        
        # Preparar datos para mostrar
        display_data = leads_data[list(display_columns.keys())].copy()
        display_data.columns = list(display_columns.values())
        
        # Formatear fechas
        if t('created_date', 'common') in display_data.columns:
            display_data[t('created_date', 'common')] = pd.to_datetime(
                display_data[t('created_date', 'common')]
            ).dt.strftime('%d/%m/%Y')
        
        # Mostrar tabla con selección
        selected_indices = st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            key="leads_table"
        )
        
        # Información de paginación
        start_idx = (current_page - 1) * page_size + 1
        end_idx = min(current_page * page_size, total_leads)
        st.caption(f"{t('showing', 'common')} {start_idx}-{end_idx} {t('of', 'common')} {total_leads} {t('leads', 'common')}")
        
    else:
        st.info(t('no_leads_found', 'common'))
    
    st.markdown("---")
    
    # Acciones rápidas
    if not leads_data.empty:
        st.subheader(f"⚡ {t('quick_actions', 'common')}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"📞 {t('schedule_calls', 'common')}", use_container_width=True):
                st.success(t('calls_scheduled', 'common'))
        
        with col2:
            if st.button(f"📧 {t('send_emails', 'common')}", use_container_width=True):
                st.success(t('emails_sent', 'common'))
        
        with col3:
            if st.button(f"📊 {t('export_data', 'common')}", use_container_width=True):
                st.success(t('data_exported', 'common'))
    
    st.markdown("---")
    st.subheader(f"🔍 {t('detailed_lead_view', 'common')}")
    
    # Vista detallada del lead seleccionado
    if not leads_data.empty and 'selection' in st.session_state.get('leads_table', {}):
        selection = st.session_state.leads_table['selection']
        if selection and 'rows' in selection and selection['rows']:
            selected_row = selection['rows'][0]
            if selected_row < len(leads_data):
                lead_data = leads_data.iloc[selected_row]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**{t('personal_information', 'common')}:**")
                    st.write(f"**{t('name', 'common')}:** {lead_data.get('nombre', 'N/A')} {lead_data.get('apellido', 'N/A')}")
                    st.write(f"**{t('position', 'common')}:** {lead_data.get('cargo_contacto', 'N/A')}")
                    st.write(f"**{t('phone', 'common')}:** {lead_data.get('telefono_contacto', 'N/A')}")
                    st.write(f"**{t('email', 'common')}:** {lead_data.get('correo_contacto', 'N/A')}")
                
                with col2:
                    st.markdown(f"**{t('company_information', 'common')}:**")
                    st.write(f"**{t('company', 'common')}:** {lead_data.get('nombre_empresa', 'N/A')}")
                    st.write(f"**{t('industry', 'common')}:** {lead_data.get('rubro', 'N/A')}")
                    st.write(f"**{t('origin_port', 'common')}:** {lead_data.get('foreign_port', 'N/A')}")
                    st.write(f"**{t('destination_port', 'common')}:** {lead_data.get('us_port', 'N/A')}")
                
                col3, col4 = st.columns(2)
                with col3:
                    st.markdown(f"**{t('status_and_activity', 'common')}:**")
                    
                    # Color del estado
                    estado_colors = {
                        t('new_status', 'common'): '🟢',
                        t('contacted_status', 'common'): '🟡',
                        t('interested_status', 'common'): '🟠',
                        t('follow_up_status', 'common'): '🔵',
                        t('converted_status', 'common'): '✅',
                        t('not_interested_status', 'common'): '❌',
                        t('not_contacted_status', 'common'): '⚪'
                    }
                    estado_color = estado_colors.get(lead_data.get('estado_lead', ''), '⚪')
                    
                    st.write(f"**{t('status', 'common')}:** {estado_color} {lead_data.get('estado_lead', 'N/A')}")
                
                with col4:
                    st.write(f"**{t('call_attempts', 'common')}:** {lead_data.get('intentos_llamada', 0)}")
                    
                    # Información de última llamada
                    if lead_data.get('ultima_llamada'):
                        if isinstance(lead_data['ultima_llamada'], str):
                            fecha = pd.to_datetime(lead_data['ultima_llamada']).strftime('%d/%m/%Y %H:%M')
                        else:
                            fecha = lead_data['ultima_llamada'].strftime('%d/%m/%Y %H:%M')
                        st.write(f"**{t('last_call', 'common')}:** {fecha}")
                    elif lead_data.get('ultima_llamada'):
                        ultima_llamada = lead_data['ultima_llamada']
                        st.write(f"**{t('last_call', 'common')}:** {ultima_llamada}")
                    else:
                        st.write(f"**{t('last_call', 'common')}:** {t('no_calls', 'common')}")
    
    else:
        st.info(t('select_lead_for_details', 'common'))
    
    st.markdown("---")
    
    # Estadísticas generales
    st.header(f"📊 {t('leads_statistics', 'common')}")
    
    if not leads_data.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                t('total_leads', 'common'),
                format_number(len(leads_data))
            )
        
        with col2:
            contacted = len(leads_data[leads_data['intentos_llamada'] > 0])
            st.metric(
                t('contacted_leads', 'common'),
                format_number(contacted),
                f"{format_percentage(contacted / len(leads_data))}"
            )
        
        with col3:
            converted = len(leads_data[leads_data['estado_lead'] == 'Convertido'])
            st.metric(
                t('converted_leads', 'common'),
                format_number(converted),
                f"{format_percentage(converted / len(leads_data))}"
            )
        
        with col4:
            avg_attempts = leads_data['intentos_llamada'].mean()
            st.metric(
                t('avg_call_attempts', 'common'),
                f"{avg_attempts:.1f}"
            )
    
    st.markdown("---")
    
    # Gráficos de distribución
    if not leads_data.empty:
        st.subheader(f"📈 {t('status_distribution', 'common')}")
        
        # Distribución por estado
        status_counts = leads_data['estado_lead'].value_counts()
        
        col1, col2 = st.columns(2)
        
        with col1:
            fig_pie = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title=t('leads_by_status', 'common')
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            fig_bar = px.bar(
                x=status_counts.index,
                y=status_counts.values,
                title=t('leads_count_by_status', 'common')
            )
            fig_bar.update_layout(
                xaxis_title=t('status', 'common'),
                yaxis_title=t('count', 'common')
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Distribución por rubro
        st.subheader(f"🏢 {t('industry_distribution', 'common')}")
        
        industry_counts = leads_data['rubro'].value_counts().head(10)
        
        fig_industry = px.bar(
            x=industry_counts.values,
            y=industry_counts.index,
            orientation='h',
            title=t('top_industries', 'common')
        )
        fig_industry.update_layout(
            xaxis_title=t('count', 'common'),
            yaxis_title=t('industry', 'common')
        )
        st.plotly_chart(fig_industry, use_container_width=True)
        
        st.markdown("---")
        st.subheader(f"🎯 {t('conversion_funnel', 'common')}")
        
        # Embudo de conversión
        total = len(leads_data)
        contacted = len(leads_data[leads_data['intentos_llamada'] > 0])
        interested = len(leads_data[leads_data['estado_lead'].isin(['Interesado', 'Seguimiento'])])
        converted = len(leads_data[leads_data['estado_lead'] == 'Convertido'])
        
        funnel_data = {
            t('total_leads', 'common'): total,
            t('contacted', 'common'): contacted,
            t('interested', 'common'): interested,
            t('converted', 'common'): converted
        }
        
        fig_funnel = go.Figure(go.Funnel(
            y=list(funnel_data.keys()),
            x=list(funnel_data.values()),
            textinfo="value+percent initial"
        ))
        fig_funnel.update_layout(title=t('conversion_funnel', 'common'))
        st.plotly_chart(fig_funnel, use_container_width=True)

def render():
    """Renderiza la página de gestión de leads"""
    
    # Inicializar i18n
    from utils.i18n_helpers import init_i18n
    init_i18n()
    
    # Título principal
    bilingual_header(t('leads_management'), t('leads_management_description'))
    
    # Verificar conexión
    if not test_connection_status():
        return
    
    # Obtener datos
    data_service = DataService()
    leads_data = data_service.get_leads_data()
    
    if leads_data is None or leads_data.empty:
        st.warning(t('no_leads_data'))
        return
    
    # Filtros
    render_filters(leads_data)
    
    # Métricas principales
    render_main_kpis(leads_data)
    
    # Análisis de conversión
    render_conversion_analysis(leads_data)
    
    # Análisis temporal
    render_temporal_analysis(leads_data)
    
    # Distribución y análisis
    render_distribution_analysis(leads_data)
    
    # Tabla de leads
    render_leads_table(leads_data)

def test_connection_status():
    """Prueba el estado de la conexión"""
    try:
        # Probar conexión con Supabase
        response = supabase_client.table('leads').select('id').limit(1).execute()
        return True
    except Exception as e:
        st.error(t('connection_error'))
        st.error(f"Error: {str(e)}")
        return False

def render_filters(data):
    """Renderiza los filtros de la página"""
    st.sidebar.header(t('filters'))
    
    # Filtro por fecha
    col1, col2 = st.sidebar.columns(2)
    with col1:
        start_date = st.date_input(t('start_date'), 
                                 value=datetime.now() - timedelta(days=30))
    with col2:
        end_date = st.date_input(t('end_date'), 
                               value=datetime.now())
    
    # Filtro por estado
    if 'status' in data.columns:
        statuses = st.sidebar.multiselect(
            t('status'),
            options=data['status'].unique(),
            default=data['status'].unique()
        )
    
    # Filtro por fuente
    if 'source' in data.columns:
        sources = st.sidebar.multiselect(
            t('source'),
            options=data['source'].unique(),
            default=data['source'].unique()
        )

def render_main_kpis(data):
    """Renderiza las métricas principales"""
    bilingual_subheader(t('main_kpis'), t('main_kpis_description'))
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_leads = len(data)
        bilingual_metric(t('total_leads'), format_number(total_leads))
    
    with col2:
        if 'status' in data.columns:
            qualified_leads = len(data[data['status'] == 'qualified'])
            bilingual_metric(t('qualified_leads'), format_number(qualified_leads))
        else:
            bilingual_metric(t('qualified_leads'), "N/A")
    
    with col3:
        if 'status' in data.columns:
            conversion_rate = (len(data[data['status'] == 'converted']) / len(data)) * 100
            bilingual_metric(t('conversion_rate'), format_percentage(conversion_rate))
        else:
            bilingual_metric(t('conversion_rate'), "N/A")
    
    with col4:
        if 'created_at' in data.columns:
            today_leads = len(data[data['created_at'].dt.date == datetime.now().date()])
            bilingual_metric(t('today_leads'), format_number(today_leads))
        else:
            bilingual_metric(t('today_leads'), "N/A")

def render_conversion_analysis(data):
    """Renderiza el análisis de conversión"""
    bilingual_subheader(t('conversion_analysis'), t('conversion_analysis_description'))
    
    if 'status' in data.columns:
        # Embudo de conversión
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(t('conversion_funnel'))
            status_counts = data['status'].value_counts()
            
            fig = go.Figure(go.Funnel(
                y = status_counts.index,
                x = status_counts.values,
                textinfo = "value+percent initial"
            ))
            
            fig.update_layout(
                title=t('conversion_funnel'),
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader(t('status_distribution'))
            
            fig = px.pie(
                values=status_counts.values,
                names=status_counts.index,
                title=t('status_distribution')
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(t('no_status_data'))

def render_temporal_analysis(data):
    """Renderiza el análisis temporal"""
    bilingual_subheader(t('temporal_analysis'), t('temporal_analysis_description'))
    
    if 'created_at' in data.columns:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(t('leads_evolution'))
            
            # Evolución diaria de leads
            daily_leads = data.groupby(data['created_at'].dt.date).size().reset_index()
            daily_leads.columns = ['date', 'count']
            
            fig = px.line(
                daily_leads,
                x='date',
                y='count',
                title=t('daily_leads_creation')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader(t('hourly_distribution'))
            
            # Distribución por hora
            hourly_leads = data.groupby(data['created_at'].dt.hour).size().reset_index()
            hourly_leads.columns = ['hour', 'count']
            
            fig = px.bar(
                hourly_leads,
                x='hour',
                y='count',
                title=t('leads_by_hour')
            )
            
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info(t('no_temporal_data'))

def render_distribution_analysis(data):
    """Renderiza el análisis de distribución"""
    bilingual_subheader(t('distribution_analysis'), t('distribution_analysis_description'))
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'source' in data.columns:
            st.subheader(t('leads_by_source'))
            
            source_counts = data['source'].value_counts()
            
            fig = px.bar(
                x=source_counts.values,
                y=source_counts.index,
                orientation='h',
                title=t('leads_by_source')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t('no_source_data'))
    
    with col2:
        if 'industry' in data.columns:
            st.subheader(t('leads_by_industry'))
            
            industry_counts = data['industry'].value_counts()
            
            fig = px.pie(
                values=industry_counts.values,
                names=industry_counts.index,
                title=t('leads_by_industry')
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info(t('no_industry_data'))

def render_leads_table(data):
    """Renderiza la tabla de leads"""
    bilingual_subheader(t('leads_table'), t('leads_table_description'))
    
    # Configurar columnas a mostrar
    columns_to_show = []
    if 'name' in data.columns:
        columns_to_show.append('name')
    if 'email' in data.columns:
        columns_to_show.append('email')
    if 'phone' in data.columns:
        columns_to_show.append('phone')
    if 'status' in data.columns:
        columns_to_show.append('status')
    if 'source' in data.columns:
        columns_to_show.append('source')
    if 'created_at' in data.columns:
        columns_to_show.append('created_at')
    
    if columns_to_show:
        # Opciones de visualización
        col1, col2 = st.columns(2)
        with col1:
            show_all = st.checkbox(t('show_all_leads'), value=False)
        with col2:
            if not show_all:
                limit = st.number_input(t('limit_results'), min_value=10, max_value=1000, value=50)
        
        # Mostrar tabla
        display_data = data[columns_to_show]
        if not show_all:
            display_data = display_data.head(limit)
        
        st.dataframe(
            display_data,
            use_container_width=True,
            hide_index=True
        )
        
        # Botón de exportación
        if st.button(t('export_leads')):
            csv = display_data.to_csv(index=False)
            st.download_button(
                label=t('download_csv'),
                data=csv,
                file_name=f"leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.warning(t('no_leads_columns'))
    st.markdown("---")
    
    # Acciones rápidas
    if not leads_data.empty:
        st.subheader(f"⚡ {t('quick_actions', 'management')}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button(f"📞 {t('schedule_calls', 'management')}", use_container_width=True):
                st.success(t('calls_scheduled', 'management'))
        
        with col2:
            if st.button(f"📧 {t('send_emails', 'management')}", use_container_width=True):
                st.success(t('emails_sent', 'management'))
        
        with col3:
            if st.button(f"📊 {t('export_data', 'management')}", use_container_width=True):
                st.success(t('data_exported', 'management'))
    
    st.markdown("---")
    st.subheader(f"🔍 {t('detailed_lead_view', 'management')}")
    
    # Vista detallada del lead seleccionado
    if not leads_data.empty and 'selection' in st.session_state.get('leads_table', {}):
        selection = st.session_state.leads_table['selection']
        if selection and 'rows' in selection and selection['rows']:
            selected_row = selection['rows'][0]
            if selected_row < len(leads_data):
                lead_data = leads_data.iloc[selected_row]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**{t('personal_information', 'management')}:**")
                    st.write(f"**{t('name', 'common')}:** {lead_data.get('nombre', 'N/A')} {lead_data.get('apellido', 'N/A')}")
                    st.write(f"**{t('position', 'management')}:** {lead_data.get('cargo_contacto', 'N/A')}")
                    st.write(f"**{t('phone', 'common')}:** {lead_data.get('telefono_contacto', 'N/A')}")
                    st.write(f"**{t('email', 'common')}:** {lead_data.get('correo_contacto', 'N/A')}")
                
                with col2:
                    st.markdown(f"**{t('company_information', 'management')}:**")
                    st.write(f"**{t('company', 'common')}:** {lead_data.get('nombre_empresa', 'N/A')}")
                    st.write(f"**{t('industry', 'common')}:** {lead_data.get('rubro', 'N/A')}")
                    st.write(f"**{t('origin_port', 'management')}:** {lead_data.get('foreign_port', 'N/A')}")
                    st.write(f"**{t('destination_port', 'management')}:** {lead_data.get('us_port', 'N/A')}")
                
                col3, col4 = st.columns(2)
                with col3:
                    st.markdown(f"**{t('status_and_activity', 'management')}:**")
                    
                    # Color del estado
                    estado_colors = {
                        t('new_status', 'common'): '🟢',
                        t('contacted_status', 'common'): '🟡',
                        t('interested_status', 'common'): '🟠',
                        t('follow_up_status', 'common'): '🔵',
                        t('converted_status', 'common'): '✅',
                        t('not_interested_status', 'common'): '❌',
                        t('not_contacted_status', 'common'): '⚪'
                    }
                    estado_color = estado_colors.get(lead_data.get('estado_lead', ''), '⚪')
                    
                    st.write(f"**{t('status', 'common')}:** {estado_color} {lead_data.get('estado_lead', 'N/A')}")
                
                with col4:
                    st.write(f"**{t('call_attempts', 'management')}:** {lead_data.get('intentos_llamada', 0)}")
                    
                    # Información de última llamada
                    if lead_data.get('ultima_llamada'):
                        if isinstance(lead_data['ultima_llamada'], str):
                            fecha = pd.to_datetime(lead_data['ultima_llamada']).strftime('%d/%m/%Y %H:%M')
                        else:
                            fecha = lead_data['ultima_llamada'].strftime('%d/%m/%Y %H:%M')
                        st.write(f"**{t('last_call', 'management')}:** {fecha}")
                    elif lead_data.get('ultima_llamada'):
                        ultima_llamada = lead_data['ultima_llamada']
                        st.write(f"**{t('last_call', 'management')}:** {ultima_llamada}")
                    else:
                        st.write(f"**{t('last_call', 'management')}:** {t('no_calls', 'management')}")
    
    else:
        st.info(t('select_lead_for_details', 'management'))

def render():
    """Main render function called by app.py"""
    render_leads_page()

if __name__ == "__main__":
    render_leads_page()