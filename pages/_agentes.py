"""
Agentes page - Agent performance analysis and comparative visualizations.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
from services.data_service import get_agents_performance, get_calls_data
from services.supabase_client import test_connection
from config.settings import CHART_COLORS
from utils.i18n_helpers import t
import logging

logger = logging.getLogger(__name__)

def render():
    """Render the agents page."""
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
        
        # Get date range from session state
        date_range = st.session_state.get('date_range', (
            datetime.now().date() - timedelta(days=30),
            datetime.now().date()
        ))
        
        # Convert dates to strings for API
        start_date = date_range[0].strftime("%Y-%m-%d")
        end_date = date_range[1].strftime("%Y-%m-%d")
        
        # Show connection status
        if st.session_state.connection_status == 'connected':
            st.success(f"✅ {t('agents.connected_supabase_realtime', 'management')}")
        else:
            st.warning(f"⚠️ {t('agents.no_connection_supabase_example', 'management')}")
        
        # Get agents performance data
        with st.spinner(t('agents.loading_agent_performance', 'management')):
            agents_df = get_agents_performance((start_date, end_date))
        
        if agents_df.empty:
            st.info(t('agents.no_agent_data_period', 'management'))
            return
        
        # Display agent filters
        render_agent_filters(agents_df)
        
        # Display performance overview
        render_performance_overview(agents_df)
        
        # Display charts
        col1, col2 = st.columns(2)
        
        with col1:
            render_agents_comparison_chart(agents_df)
            render_conversion_rate_comparison(agents_df)
        
        with col2:
            render_call_volume_chart(agents_df)
            render_duration_comparison_chart(agents_df)
        
        # Display detailed agents table
        render_agents_detailed_table(agents_df, start_date, end_date)
        
        # Display individual agent analysis
        render_individual_agent_analysis(agents_df, start_date, end_date)
        
    except Exception as e:
         st.error(f"{t('agents.error_loading_agents_page', 'management')}: {e}")
         logger.error(f"Agents page rendering error: {e}", exc_info=True)

def render_agent_filters(agents_df: pd.DataFrame):
    """Render agent filtering options."""
    st.markdown(f"### 🔍 {t('agents.agent_filters', 'management')}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Active/Inactive filter
        status_filter = st.selectbox(
            "Estado del Agente",
            options=["Todos", "Activos", "Inactivos"],
            key="agent_status_filter"
        )
        
        if status_filter == "Activos":
            agents_df = agents_df[agents_df['active'] == True]
        elif status_filter == "Inactivos":
            agents_df = agents_df[agents_df['active'] == False]
    
    with col2:
        # Role filter
        if 'role' in agents_df.columns:
            roles = ["Todos"] + list(agents_df['role'].unique())
            role_filter = st.selectbox(
                "Rol",
                options=roles,
                key="agent_role_filter"
            )
            
            if role_filter != "Todos":
                agents_df = agents_df[agents_df['role'] == role_filter]
    
    with col3:
        # Performance filter
        performance_filter = st.selectbox(
            "Rendimiento",
            options=["Todos", "Alto (>70%)", "Medio (50-70%)", "Bajo (<50%)"],
            key="agent_performance_filter"
        )
        
        if performance_filter == "Alto (>70%)":
            agents_df = agents_df[agents_df['conversion_rate'] > 70]
        elif performance_filter == "Medio (50-70%)":
            agents_df = agents_df[(agents_df['conversion_rate'] >= 50) & (agents_df['conversion_rate'] <= 70)]
        elif performance_filter == "Bajo (<50%)":
            agents_df = agents_df[agents_df['conversion_rate'] < 50]
    
    # Update session state with filtered agents
    st.session_state.filtered_agents_df = agents_df

def render_performance_overview(agents_df: pd.DataFrame):
    """Render performance overview metrics."""
    st.markdown(f"### 📊 {t('agents.performance_overview', 'management')}")
    
    # Calculate overview metrics
    total_agents = len(agents_df)
    active_agents = len(agents_df[agents_df['active'] == True]) if 'active' in agents_df.columns else total_agents
    avg_conversion = agents_df['conversion_rate'].mean()
    top_performer = agents_df.loc[agents_df['conversion_rate'].idxmax()] if not agents_df.empty else None
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label=f"👥 {t('agents.total_agents', 'management')}",
            value=f"{total_agents:,}",
            delta=f"{active_agents} {t('agents.active', 'management')}"
        )
    
    with col2:
        st.metric(
            label=f"📈 {t('agents.average_conversion', 'management')}",
            value=f"{avg_conversion:.1f}%",
            delta=f"{t('agents.excellent', 'management') if avg_conversion >= 70 else t('agents.good', 'management') if avg_conversion >= 50 else t('agents.improvable', 'management')}"
        )
    
    with col3:
        total_calls = agents_df['total_calls'].sum()
        st.metric(
            label=f"📞 {t('agents.total_calls', 'management')}",
            value=f"{total_calls:,}",
            delta=f"{total_calls/max(active_agents, 1):.1f} {t('agents.per_agent', 'management')}"
        )
    
    with col4:
        if top_performer is not None:
            st.metric(
                label=f"🏆 {t('agents.best_agent', 'management')}",
                value=top_performer['name'][:15] + "..." if len(top_performer['name']) > 15 else top_performer['name'],
                delta=f"{top_performer['conversion_rate']:.1f}% {t('agents.conversion', 'management')}"
            )

def render_agents_comparison_chart(agents_df: pd.DataFrame):
    """Render agents performance comparison chart."""
    st.markdown(f"### 📊 {t('agents.performance_comparison', 'management')}")
    
    try:
        if agents_df.empty:
            st.info(t('agents.no_agent_data_period', 'management'))
            return
        
        # Sort by conversion rate and take top 10
        top_agents = agents_df.nlargest(10, 'conversion_rate')
        
        # Create bar chart
        fig = px.bar(
            top_agents,
            x='name',
            y='conversion_rate',
            title="Top 10 Agentes por Tasa de Conversión",
            labels={'name': 'Agente', 'conversion_rate': 'Tasa de Conversión (%)'},
            color='conversion_rate',
            color_continuous_scale='RdYlGn',
            text='conversion_rate'
        )
        
        fig.update_traces(
            texttemplate='%{text:.1f}%',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Conversión: %{y:.1f}%<br>Llamadas: %{customdata[0]}<br>Exitosas: %{customdata[1]}<extra></extra>',
            customdata=top_agents[['total_calls', 'successful_calls']]
        )
        
        fig.update_layout(
            xaxis_title="Agente",
            yaxis_title="Tasa de Conversión (%)",
            xaxis_tickangle=-45,
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al generar gráfico de comparación: {e}")
        logger.error(f"Agents comparison chart error: {e}")

def render_call_volume_chart(agents_df: pd.DataFrame):
    """Render call volume by agent chart."""
    st.markdown(f"### 📞 {t('agents.call_volume', 'management')}")
    
    try:
        if agents_df.empty:
            st.info(t('agents.no_call_volume_data', 'management'))
            return
        
        # Sort by total calls and take top 10
        top_volume = agents_df.nlargest(10, 'total_calls')
        
        # Create horizontal bar chart
        fig = px.bar(
            top_volume,
            x='total_calls',
            y='name',
            orientation='h',
            title="Top 10 Agentes por Volumen de Llamadas",
            labels={'total_calls': 'Total Llamadas', 'name': 'Agente'},
            color='total_calls',
            color_continuous_scale='Blues',
            text='total_calls'
        )
        
        fig.update_traces(
            texttemplate='%{text}',
            textposition='outside',
            hovertemplate='<b>%{y}</b><br>Total: %{x}<br>Exitosas: %{customdata[0]}<br>Conversión: %{customdata[1]:.1f}%<extra></extra>',
            customdata=top_volume[['successful_calls', 'conversion_rate']]
        )
        
        fig.update_layout(
            xaxis_title="Total Llamadas",
            yaxis_title="Agente",
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"{t('agents.error_volume_chart', 'management')}: {e}")
        logger.error(f"Call volume chart error: {e}")

def render_conversion_rate_comparison(agents_df: pd.DataFrame):
    """Render conversion rate comparison scatter plot."""
    st.markdown(f"### 🎯 {t('agents.conversion_volume_analysis', 'management')}")
    
    try:
        if agents_df.empty:
            st.info(t('agents.no_call_volume_data', 'management'))
            return
        
        # Create scatter plot
        fig = px.scatter(
            agents_df,
            x='total_calls',
            y='conversion_rate',
            size='successful_calls',
            color='avg_duration',
            hover_name='name',
            title="Conversión vs Volumen de Llamadas",
            labels={
                'total_calls': 'Total Llamadas',
                'conversion_rate': 'Tasa de Conversión (%)',
                'avg_duration': 'Duración Promedio (min)',
                'successful_calls': 'Llamadas Exitosas'
            },
            color_continuous_scale='Viridis'
        )
        
        fig.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>Total: %{x}<br>Conversión: %{y:.1f}%<br>Duración: %{marker.color:.1f} min<br>Exitosas: %{marker.size}<extra></extra>'
        )
        
        # Add trend line
        if len(agents_df) > 1:
            fig.add_trace(
                px.scatter(
                    agents_df, 
                    x='total_calls', 
                    y='conversion_rate',
                    trendline='ols'
                ).data[1]
            )
        
        fig.update_layout(
            xaxis_title="Total Llamadas",
            yaxis_title="Tasa de Conversión (%)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error al generar análisis de conversión: {e}")
        logger.error(f"Conversion analysis chart error: {e}")

def render_duration_comparison_chart(agents_df: pd.DataFrame):
    """Render duration comparison chart."""
    st.markdown(f"### ⏱️ {t('agents.duration_comparison', 'management')}")
    
    try:
        if agents_df.empty:
            st.info(t('agents.no_call_volume_data', 'management'))
            return
        
        # Sort by average duration and take top 10
        top_duration = agents_df.nlargest(10, 'avg_duration')
        
        # Create bar chart
        fig = px.bar(
            top_duration,
            x='name',
            y='avg_duration',
            title="Top 10 Agentes por Duración Promedio",
            labels={'name': 'Agente', 'avg_duration': 'Duración Promedio (min)'},
            color='avg_duration',
            color_continuous_scale='Oranges',
            text='avg_duration'
        )
        
        fig.update_traces(
            texttemplate='%{text:.1f}m',
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Duración: %{y:.1f} min<br>Total: %{customdata[0]} llamadas<br>Conversión: %{customdata[1]:.1f}%<extra></extra>',
            customdata=top_duration[['total_calls', 'conversion_rate']]
        )
        
        fig.update_layout(
            xaxis_title="Agente",
            yaxis_title="Duración Promedio (minutos)",
            xaxis_tickangle=-45,
            height=400,
            showlegend=False
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"{t('agents.error_duration_chart', 'management')}: {e}")
        logger.error(f"Duration comparison chart error: {e}")

def render_agents_detailed_table(agents_df: pd.DataFrame, start_date: str, end_date: str):
    """Render detailed agents performance table."""
    st.markdown(f"### 📋 {t('agents.detailed_agents_table', 'management')}")
    
    try:
        if agents_df.empty:
            st.info(t('agents.no_agent_data_available', 'management'))
            return
        
        # Prepare display dataframe
        display_df = agents_df.copy()
        
        # Select and rename columns for display
        columns_to_show = {
            'name': 'Nombre',
            'email': 'Email',
            'role': 'Rol',
            'active': 'Activo',
            'total_calls': 'Total Llamadas',
            'successful_calls': 'Exitosas',
            'conversion_rate': 'Conversión (%)',
            'avg_duration': 'Duración Prom. (min)',
            'total_duration': 'Tiempo Total (min)'
        }
        
        # Filter columns that exist in the dataframe
        available_columns = {k: v for k, v in columns_to_show.items() if k in display_df.columns}
        display_df = display_df[list(available_columns.keys())].rename(columns=available_columns)
        
        # Sort by conversion rate descending
        if 'Conversión (%)' in display_df.columns:
            display_df = display_df.sort_values('Conversión (%)', ascending=False)
        
        # Display table with formatting
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Nombre": st.column_config.TextColumn("Nombre", width="medium"),
                "Email": st.column_config.TextColumn("Email", width="medium"),
                "Rol": st.column_config.TextColumn("Rol", width="small"),
                "Activo": st.column_config.CheckboxColumn("Activo", width="small"),
                "Total Llamadas": st.column_config.NumberColumn("Total Llamadas", format="%d"),
                "Exitosas": st.column_config.NumberColumn("Exitosas", format="%d"),
                "Conversión (%)": st.column_config.NumberColumn("Conversión (%)", format="%.1f%%"),
                "Duración Prom. (min)": st.column_config.NumberColumn("Duración Prom. (min)", format="%.1f"),
                "Tiempo Total (min)": st.column_config.NumberColumn("Tiempo Total (min)", format="%.1f")
            }
        )
        
        # Export button
        if st.button(f"📥 {t('export_agents_data', 'management')}", key="export_agents_data"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                label=t('download_csv', 'common'),
                data=csv,
                file_name=f"agentes_rendimiento_{start_date}_to_{end_date}.csv",
                mime="text/csv"
            )
        
    except Exception as e:
        st.error(f"{t('agents.error_agents_table', 'management')}: {e}")
        logger.error(f"Agents detailed table error: {e}")

def render_individual_agent_analysis(agents_df: pd.DataFrame, start_date: str, end_date: str):
    """Render individual agent detailed analysis."""
    st.markdown(f"### 🔍 {t('agents.individual_agent_analysis', 'management')}")
    
    try:
        if agents_df.empty:
            st.info(t('agents.no_agents_individual_analysis', 'management'))
            return
        
        # Agent selector
        agent_names = agents_df['name'].tolist()
        selected_agent = st.selectbox(
            t('agents.select_agent_detailed_analysis', 'management'),
            options=agent_names,
            key="individual_agent_selector"
        )
        
        if not selected_agent:
            return
        
        # Get selected agent data
        agent_data = agents_df[agents_df['name'] == selected_agent].iloc[0]
        
        # Display agent info
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(f"""
            **👤 {t('agents.agent_information', 'management')}**
            - **{t('agents.name', 'management')}:** {agent_data['name']}
            - **{t('agents.email', 'management')}:** {agent_data.get('email', 'N/A')}
            - **{t('agents.role', 'management')}:** {agent_data.get('role', 'N/A')}
            - **{t('agents.status', 'management')}:** {t('agents.active', 'management') if agent_data.get('active', True) else t('agents.inactive', 'management')}
            """)
        
        with col2:
            st.markdown(f"""
            **📊 {t('agents.performance_metrics', 'management')}**
            - **{t('agents.total_calls', 'management')}:** {agent_data['total_calls']:,}
            - **{t('agents.successful_calls', 'management')}:** {agent_data['successful_calls']:,}
            - **{t('agents.conversion_rate', 'management')}:** {agent_data['conversion_rate']:.1f}%
            """)
        
        with col3:
            st.markdown(f"""
            **⏱️ {t('agents.time_metrics', 'management')}**
            - **{t('agents.average_duration', 'management')}:** {agent_data['avg_duration']:.1f} min
            - **{t('agents.total_time', 'management')}:** {agent_data['total_duration']:.1f} min
            - **{t('agents.efficiency', 'management')}:** {min(100, agent_data['conversion_rate'] + (agent_data['avg_duration']/10)):.0f}/100
            """)
        
        # Get detailed calls data for this agent
        agent_calls = get_calls_data(
            (start_date, end_date),
            filters={"agent_id": agent_data['id']},
            limit=1000
        )
        
        if not agent_calls.empty:
            # Daily performance chart
            st.markdown(f"#### 📈 {t('agents.daily_performance', 'management')}")
            
            agent_calls['call_date'] = pd.to_datetime(agent_calls['call_date'])
            daily_performance = agent_calls.groupby(agent_calls['call_date'].dt.date).agg({
                'id': 'count',
                'call_status': lambda x: (x == 'completed').sum()
            })
            daily_performance.columns = ['total_calls', 'successful_calls']
            daily_performance['conversion_rate'] = (daily_performance['successful_calls'] / daily_performance['total_calls'] * 100).round(2)
            daily_performance = daily_performance.reset_index()
            daily_performance['call_date'] = pd.to_datetime(daily_performance['call_date'])
            
            # Create daily performance chart
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Llamadas por Día', 'Tasa de Conversión Diaria'),
                vertical_spacing=0.1
            )
            
            # Calls volume
            fig.add_trace(
                go.Bar(
                    x=daily_performance['call_date'],
                    y=daily_performance['total_calls'],
                    name='Total Llamadas',
                    marker_color=CHART_COLORS[0]
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Bar(
                    x=daily_performance['call_date'],
                    y=daily_performance['successful_calls'],
                    name='Exitosas',
                    marker_color=CHART_COLORS[1]
                ),
                row=1, col=1
            )
            
            # Conversion rate
            fig.add_trace(
                go.Scatter(
                    x=daily_performance['call_date'],
                    y=daily_performance['conversion_rate'],
                    mode='lines+markers',
                    name='Conversión (%)',
                    line=dict(color=CHART_COLORS[2], width=3),
                    marker=dict(size=6)
                ),
                row=2, col=1
            )
            
            fig.update_layout(
                height=600,
                title_text=f"{t('agents.detailed_analysis', 'management')} - {selected_agent}",
                showlegend=True
            )
            
            fig.update_xaxes(title_text="Fecha", row=2, col=1)
            fig.update_yaxes(title_text="Número de Llamadas", row=1, col=1)
            fig.update_yaxes(title_text="Tasa de Conversión (%)", row=2, col=1)
            
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"{t('agents.error_individual_analysis', 'management')}: {e}")
        logger.error(f"Individual agent analysis error: {e}")