"""
Página de Llamadas - Call Analytics Dashboard
Enfocada exclusivamente en call_results_pluscargo_basic
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

def render_llamadas_page():
    """Render the calls page with comprehensive call analytics."""
    
    st.title(f"📞 {t('call_analysis', 'common')}")
    st.markdown("---")
    
    # Get date range from session state (set by global filters)
    date_range = st.session_state.get('date_range', (
        datetime.now().date() - timedelta(days=30),
        datetime.now().date()
    ))
    
    # Sidebar filters
    with st.sidebar:
        st.header(f"🔍 {t('filters', 'common')}")
        
        # Call result filter
        result_options = [
            t('all', 'common'), 
            t('call_result_successful', 'common'), 
            t('call_result_no_answer', 'common'), 
            t('call_result_busy', 'common'), 
            t('call_result_voicemail', 'common'), 
            t('call_result_wrong_number', 'common'), 
            t('call_result_rejected', 'common')
        ]
        selected_result = st.selectbox(t('call_result', 'common'), result_options)
        
        # Duration filter
        st.subheader(f"⏱️ {t('duration', 'common')}")
        duration_filter = st.selectbox(
            t('filter_by_duration', 'common'),
            [t('all_feminine', 'common'), t('short_calls', 'common'), t('medium_calls', 'common'), t('long_calls', 'common')]
        )
        
        # Agent filter (if available)
        agent_filter = st.text_input(f"🧑‍💼 {t('filter_by_agent', 'common')}", placeholder=t('agent_id_or_name', 'common'))
        
        # Pagination
        st.markdown("---")
        st.subheader(f"📄 {t('pagination', 'common')}")
        page_size = st.selectbox(t('records_per_page', 'common'), [25, 50, 100, 200], index=1)
    
    # Build filters
    filters = {}
    if selected_result != t('all', 'common'):
        # Map translated result back to database value
        result_mapping = {
            t('call_result_successful', 'common'): "exitosa",
            t('call_result_no_answer', 'common'): "no_contesta",
            t('call_result_busy', 'common'): "ocupado",
            t('call_result_voicemail', 'common'): "buzón",
            t('call_result_wrong_number', 'common'): "número_incorrecto",
            t('call_result_rejected', 'common'): "rechazada"
        }
        filters["resultado_llamada"] = result_mapping.get(selected_result, selected_result)
    if agent_filter:
        filters["agent_id"] = agent_filter
    
    # Load data
    try:
        # Get calls summary
        calls_summary = DataService.get_calls_summary(date_range)
        
        # Get calls data
        calls_df = DataService.get_calls_data(date_range, filters=filters, limit=1000)
        
        # Apply duration filter
        if duration_filter != t('all_feminine', 'common') and not calls_df.empty and "duracion_segundos" in calls_df.columns:
            if duration_filter == t('short_calls', 'common'):
                calls_df = calls_df[calls_df["duracion_segundos"] < 60]
            elif duration_filter == t('medium_calls', 'common'):
                calls_df = calls_df[(calls_df["duracion_segundos"] >= 60) & (calls_df["duracion_segundos"] <= 300)]
            elif duration_filter == t('long_calls', 'common'):
                calls_df = calls_df[calls_df["duracion_segundos"] > 300]
        
        # Data Table Section
        st.markdown("---")
        st.header(f"📋 {t('calls_table', 'reports')}")
        
        if not calls_df.empty:
            # Pagination
            total_records = len(calls_df)
            total_pages = (total_records - 1) // page_size + 1 if total_records > 0 else 1
            
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                current_page = st.number_input(
                    f"{t('page', 'common')} (1-{total_pages})",
                    min_value=1,
                    max_value=total_pages,
                    value=1
                )
            
            # Calculate pagination
            start_idx = (current_page - 1) * page_size
            end_idx = start_idx + page_size
            paginated_df = calls_df.iloc[start_idx:end_idx]
            
            # Display info
            st.info(t('showing_records', 'common').format(
                showing=len(paginated_df), 
                total=total_records, 
                current_page=current_page, 
                total_pages=total_pages
            ))
            
            # Filter out columns we want to hide and prepare display
            display_df = paginated_df.copy()
            
            # Hide specific columns
            columns_to_hide = ['id', 'lead_id', 'created_at', 'updated_at', 'audio_url']
            for col in columns_to_hide:
                if col in display_df.columns:
                    display_df = display_df.drop(col, axis=1)
            
            # Format display
            if not display_df.empty:
                # Format duration
                if "duracion_segundos" in display_df.columns:
                    display_df["duration_minutes"] = (display_df["duracion_segundos"] / 60).round(1)
                
                # Format date
                if "fecha_llamada" in display_df.columns:
                    display_df["fecha_llamada"] = pd.to_datetime(display_df["fecha_llamada"]).dt.strftime('%Y-%m-%d %H:%M')
                
                # Rename columns for better display (only rename columns that exist)
                column_names = {}
                if "fecha_llamada" in display_df.columns:
                    column_names["fecha_llamada"] = t('date_time', 'common')
                if "resultado_llamada" in display_df.columns:
                    column_names["resultado_llamada"] = t('result', 'common')
                if "duracion_segundos" in display_df.columns:
                    column_names["duracion_segundos"] = t('duration_seconds', 'common')
                if "duration_minutes" in display_df.columns:
                    column_names["duration_minutes"] = t('duration_minutes', 'common')
                if "agent_id" in display_df.columns:
                    column_names["agent_id"] = t('agent', 'common')
                if "phone_number" in display_df.columns:
                    column_names["phone_number"] = t('phone', 'common')
                if "notes" in display_df.columns:
                    column_names["notes"] = t('notes', 'common')
                if "nombre_lead" in display_df.columns:
                    column_names["nombre_lead"] = "Nombre del Lead"
                
                # Apply column renaming
                if column_names:
                    display_df = display_df.rename(columns=column_names)
                
                # Reorder columns to put "Nombre del Lead" first
                if "Nombre del Lead" in display_df.columns:
                    # Get all columns except "Nombre del Lead"
                    other_columns = [col for col in display_df.columns if col != "Nombre del Lead"]
                    # Create new column order with "Nombre del Lead" first
                    new_column_order = ["Nombre del Lead"] + other_columns
                    # Reorder the DataFrame
                    display_df = display_df[new_column_order]
                
                # Style the dataframe
                def style_result(val):
                    color_map = {
                        "exitosa": "background-color: #d4edda",
                        "no_contesta": "background-color: #f8d7da",
                        "ocupado": "background-color: #fff3cd",
                        "buzón": "background-color: #e2e3e5",
                        "número_incorrecto": "background-color: #ffeaa7",
                        "rechazada": "background-color: #f8d7da"
                    }
                    return color_map.get(val, "")
                
                # Interactive table with row selection
                st.markdown("**💡 Haz clic en una fila para ver los detalles completos**")
                
                # Initialize session state for row selection
                if "selected_call_row" not in st.session_state:
                    st.session_state.selected_call_row = None
                if "clear_selection_flag" not in st.session_state:
                    st.session_state.clear_selection_flag = False
                
                # Add a selection column for better UX
                display_df_with_selection = display_df.copy()
                
                # Reset all selections if clear flag is set
                if st.session_state.clear_selection_flag:
                    display_df_with_selection.insert(0, "Seleccionar", False)
                    st.session_state.clear_selection_flag = False
                    st.session_state.selected_call_row = None
                else:
                    # Add selection column with current state
                    selection_values = [False] * len(display_df_with_selection)
                    if st.session_state.selected_call_row is not None and st.session_state.selected_call_row < len(selection_values):
                        selection_values[st.session_state.selected_call_row] = True
                    display_df_with_selection.insert(0, "Seleccionar", selection_values)
                
                # Use data_editor for row selection
                edited_df = st.data_editor(
                    display_df_with_selection,
                    use_container_width=True,
                    height=400,
                    hide_index=True,
                    column_config={
                        "Seleccionar": st.column_config.CheckboxColumn(
                            "Seleccionar",
                            help="Selecciona una fila para ver detalles",
                            default=False,
                        )
                    },
                    disabled=[col for col in display_df_with_selection.columns if col != "Seleccionar"],
                    key="calls_data_editor"
                )
                
                # Check if any row is selected and update session state
                selected_rows = edited_df[edited_df["Seleccionar"] == True]
                
                if not selected_rows.empty:
                    # Get the first selected row
                    selected_row_idx = selected_rows.index[0]
                    st.session_state.selected_call_row = selected_row_idx
                    # Get the original row data from paginated_df
                    original_row_idx = selected_row_idx + start_idx
                    selected_call_data = calls_df.iloc[original_row_idx]
                elif st.session_state.selected_call_row is not None:
                    # If no rows selected but we have a stored selection, clear it
                    st.session_state.selected_call_row = None
                
                # Show details if we have a selected row
                if not selected_rows.empty or (st.session_state.selected_call_row is not None and not st.session_state.clear_selection_flag):
                    
                    # Create floating card with call details
                    with st.container():
                        st.markdown("---")
                        st.markdown("### 🔍 **Detalles de la Llamada Seleccionada**")
                        
                        # Create an attractive card layout
                        card_container = st.container()
                        with card_container:
                            # Header with call result status
                            result_status = selected_call_data.get('resultado_llamada', 'N/A')
                            status_colors = {
                                "exitosa": "🟢",
                                "no_contesta": "🔴", 
                                "ocupado": "🟡",
                                "buzón": "⚪",
                                "número_incorrecto": "🟠",
                                "rechazada": "🔴"
                            }
                            status_icon = status_colors.get(result_status, "⚫")
                            
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(90deg, #f0f2f6 0%, #ffffff 100%);
                                padding: 20px;
                                border-radius: 10px;
                                border-left: 4px solid #1f77b4;
                                margin: 10px 0;
                                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                            ">
                                <h4 style="margin: 0; color: #1f77b4;">
                                    {status_icon} Llamada - {result_status.title()}
                                </h4>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Main details in columns
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.markdown("**📅 Información Temporal**")
                                fecha = selected_call_data.get('fecha_llamada', 'N/A')
                                if fecha != 'N/A':
                                    try:
                                        fecha_formatted = pd.to_datetime(fecha).strftime('%d/%m/%Y %H:%M:%S')
                                    except:
                                        fecha_formatted = str(fecha)
                                else:
                                    fecha_formatted = 'N/A'
                                
                                st.write(f"🕐 **Fecha y Hora:** {fecha_formatted}")
                                
                                duracion = selected_call_data.get('duracion_segundos', 0)
                                if duracion and duracion > 0:
                                    minutos = int(duracion // 60)
                                    segundos = int(duracion % 60)
                                    duracion_formatted = f"{minutos}m {segundos}s"
                                else:
                                    duracion_formatted = "0s"
                                st.write(f"⏱️ **Duración:** {duracion_formatted}")
                            
                            with col2:
                                st.markdown("**👤 Información de Contacto**")
                                st.write(f"📞 **Teléfono:** {selected_call_data.get('phone_number', 'N/A')}")
                                st.write(f"👤 **Lead:** {selected_call_data.get('nombre_lead', 'N/A')}")
                                st.write(f"👨‍💼 **Agente:** {selected_call_data.get('agent_id', 'N/A')}")
                            
                            with col3:
                                st.markdown("**📊 Información Adicional**")
                                st.write(f"📈 **Resultado:** {result_status}")
                                
                                # Show any additional columns that exist
                                additional_info = []
                                for col in selected_call_data.index:
                                    if col not in ['fecha_llamada', 'duracion_segundos', 'phone_number', 'lead_id', 'agent_id', 'resultado_llamada', 'notes']:
                                        value = selected_call_data.get(col, 'N/A')
                                        if value and str(value).strip() and str(value) != 'N/A':
                                            additional_info.append(f"**{col}:** {value}")
                                
                                if additional_info:
                                    for info in additional_info[:3]:  # Limit to 3 additional fields
                                        st.write(f"ℹ️ {info}")
                            
                            # Notes section (full width)
                            st.markdown("**📝 Notas de la Llamada**")
                            
                            # Priority: transcripcion > notes > default message
                            transcripcion = selected_call_data.get('transcripcion', '')
                            notes = selected_call_data.get('notes', '')
                            
                            content_to_show = None
                            if transcripcion and str(transcripcion).strip() and str(transcripcion) != 'N/A':
                                content_to_show = transcripcion
                            elif notes and str(notes).strip() and str(notes) != 'N/A':
                                content_to_show = notes
                            
                            if content_to_show:
                                st.markdown(f"""
                                <div style="
                                    background-color: #f8f9fa;
                                    padding: 15px;
                                    border-radius: 8px;
                                    border-left: 3px solid #28a745;
                                    margin: 10px 0;
                                ">
                                    <p style="margin: 0; font-style: italic; color: #495057;">
                                        "{content_to_show}"
                                    </p>
                                </div>
                                """, unsafe_allow_html=True)
                            else:
                                st.info("No hay transcripción ni notas disponibles para esta llamada")
                            
                            # Action buttons
                            st.markdown("---")
                            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
                            
                            with col_btn1:
                                if st.button("🔄 Actualizar Vista", key="refresh_call_detail"):
                                    st.rerun()
                            
                            with col_btn2:
                                # Clear selection button
                                if st.button("❌ Cerrar Detalles", key="clear_selection"):
                                    st.session_state.clear_selection_flag = True
                                    st.session_state.selected_call_row = None
                                    st.rerun()
                else:
                    # Show instruction when no row is selected
                    st.info("👆 Selecciona una fila en la tabla de arriba para ver los detalles completos de la llamada")
                
                # Export options
                st.markdown("---")
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    csv = calls_df.to_csv(index=False)
                    st.download_button(
                        label=f"📥 {t('download_csv', 'common')}",
                        data=csv,
                        file_name=f"llamadas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    st.info(f"💡 {t('download_available_csv', 'common')}")
                
                # Call Detail Modal
                st.markdown("---")
                st.subheader(f"🔍 {t('detailed_call_view', 'reports')}")
                
                if not calls_df.empty:
                    call_options = [
                        f"{row.get('fecha_llamada', 'N/A')} - {row.get('resultado_llamada', 'N/A')} - {row.get('agent_id', 'N/A')}" 
                        for _, row in calls_df.iterrows()
                    ]
                    
                    if call_options:
                        selected_call = st.selectbox(t('select_call', 'common'), [t('none', 'common')] + call_options[:50])
                        
                        if selected_call != t('none', 'common'):
                            # Find the selected call
                            call_idx = call_options.index(selected_call)
                            call_data = calls_df.iloc[call_idx]
                            
                            # Display call details
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown(f"**{t('call_information', 'common')}:**")
                                st.write(f"**{t('date_time', 'common')}:** {call_data.get('fecha_llamada', 'N/A')}")
                                st.write(f"**{t('result', 'common')}:** {call_data.get('resultado_llamada', 'N/A')}")
                                st.write(f"**{t('duration', 'common')}:** {call_data.get('duracion_segundos', 0)} {t('seconds', 'common')}")
                                st.write(f"**{t('phone', 'common')}:** {call_data.get('phone_number', 'N/A')}")
                            
                            with col2:
                                st.markdown(f"**{t('additional_information', 'common')}:**")
                                st.write(f"**{t('agent', 'common')}:** {call_data.get('agent_id', 'N/A')}")
                                st.write(f"**{t('lead_id', 'common')}:** {call_data.get('lead_id', 'N/A')}")
                                st.write(f"**{t('notes', 'common')}:** {call_data.get('notes', t('no_notes', 'common'))}")
            
            else:
                st.info(t('no_table_data', 'common'))
        
        else:
            st.warning(t('no_calls_found_filters', 'common'))
            
            # Show empty state with helpful message
            st.markdown(f"""
            ### 💡 {t('suggestions', 'common')}:
            - {t('verify_applied_filters', 'common')}
            - {t('try_different_date_range', 'common')}
            - {t('check_database_connection', 'common')}
            """)
    
    except Exception as e:
        logger.error(f"Error in render_llamadas_page: {e}")
        st.error(t('error_loading_calls_data', 'common'))
        st.exception(e)
    
    # Performance Metrics Section
    st.markdown("---")
    st.header(f"📊 {t('performance_metrics', 'common')}")
    
    try:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_calls = calls_summary.get("total_calls", 0)
            st.metric(t('total_calls', 'common'), format_number(total_calls))
        
        with col2:
            contact_rate = calls_summary.get("contact_rate", 0)
            st.metric(t('contact_rate', 'common'), f"{contact_rate}%")
        
        with col3:
            if not calls_df.empty and "duracion_segundos" in calls_df.columns:
                avg_duration = calls_df["duracion_segundos"].mean() / 60
                st.metric(t('average_duration', 'common'), f"{avg_duration:.1f} min")
            else:
                st.metric(t('average_duration', 'common'), "N/A")
        
        with col4:
            if not calls_df.empty:
                daily_avg = len(calls_df) / max(1, (date_range[1] - date_range[0]).days)
                st.metric(t('daily_average', 'common'), f"{daily_avg:.1f}")
            else:
                st.metric(t('daily_average', 'common'), "0")
        
        # Charts Section
        st.markdown("---")
        
        # Daily volume chart
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📈 {t('daily_call_volume', 'common')}")
            daily_volume = DataService.get_daily_calls_volume(date_range)
            
            if not daily_volume.empty:
                fig_volume = px.line(
                    daily_volume,
                    x='fecha',
                    y='total_llamadas',
                    title=t('calls_per_day', 'common'),
                    markers=True
                )
                fig_volume.update_layout(
                    height=400,
                    xaxis_title=t('date', 'common'),
                    yaxis_title=t('number_of_calls', 'common')
                )
                fig_volume.update_traces(line_color='#1f77b4', marker_color='#1f77b4')
                st.plotly_chart(fig_volume, use_container_width=True)
            else:
                st.info(t('no_daily_volume_data', 'common'))
        
        with col2:
            st.subheader(f"🎯 {t('results_distribution', 'common')}")
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
                    title=t('call_results', 'common'),
                    color_discrete_sequence=colors
                )
                fig_results.update_traces(textposition='inside', textinfo='percent+label')
                fig_results.update_layout(height=400)
                st.plotly_chart(fig_results, use_container_width=True)
            else:
                st.info(t('no_results_data', 'common'))
        
        # Hourly analysis
        if not calls_df.empty and "fecha_llamada" in calls_df.columns:
            st.markdown("---")
            st.subheader(f"🕐 {t('hourly_analysis', 'reports')}")
            
            # Extract hour from fecha_llamada
            calls_df['call_hour'] = pd.to_datetime(calls_df['fecha_llamada']).dt.hour
            hourly_data = calls_df.groupby('call_hour').size().reset_index(name='total_calls')
            
            fig_hourly = px.bar(
                hourly_data,
                x='call_hour',
                y='total_calls',
                title=t('calls_distribution_by_hour', 'common'),
                color='total_calls',
                color_continuous_scale="viridis"
            )
            fig_hourly.update_layout(
                height=400,
                xaxis_title=t('hour_of_day', 'common'),
                yaxis_title=t('number_of_calls', 'common'),
                xaxis=dict(tickmode='linear', tick0=0, dtick=1)
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
        
        # Performance by Agent (if agent data available)
        if not calls_df.empty and "agent_id" in calls_df.columns:
            st.markdown("---")
            st.subheader(f"👥 {t('agent_performance', 'reports')}")
            
            agent_performance = calls_df.groupby('agent_id').agg({
                'resultado_llamada': ['count', lambda x: (x == 'exitosa').sum()],
                'duracion_segundos': 'mean'
            }).round(2)
            
            agent_performance.columns = ['total_calls', 'successful_calls', 'avg_duration']
            agent_performance['success_rate'] = (
                agent_performance['successful_calls'] / agent_performance['total_calls'] * 100
            ).round(1)
            agent_performance['avg_duration'] = (agent_performance['avg_duration'] / 60).round(1)
            
            # Display top performers
            top_agents = agent_performance.sort_values('success_rate', ascending=False).head(10)
            
            fig_agents = px.bar(
                top_agents.reset_index(),
                x='agent_id',
                y='success_rate',
                title=t('top_10_agents_success_rate', 'common'),
                color='success_rate',
                color_continuous_scale="RdYlGn"
            )
            fig_agents.update_layout(
                height=400,
                xaxis_title=t('agent_id', 'common'),
                yaxis_title=t('success_rate_percent', 'common')
            )
            st.plotly_chart(fig_agents, use_container_width=True)
    
    except Exception as e:
        logger.error(f"Error in metrics section: {e}")
        st.error("Error al cargar las métricas y gráficos")

def render():
    """Main render function called by app.py"""
    render_llamadas_page()

if __name__ == "__main__":
    render_llamadas_page()