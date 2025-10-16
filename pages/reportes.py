"""
Reportes page - Dynamic report generation and export functionality.
"""
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime, timedelta
import io
from services.data_service import get_dashboard_metrics, get_agents_performance, get_calls_data
from services.supabase_client import test_connection
from config.settings import CHART_COLORS
from utils.i18n_helpers import t, init_i18n, bilingual_metric, bilingual_header, bilingual_subheader, bilingual_selectbox
import logging

logger = logging.getLogger(__name__)

def render():
    """Render the reports page."""
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
            st.success(f"✅ {t('connected_supabase')} - {t('reports.generating_realtime_reports')}")
        else:
            st.warning(f"⚠️ {t('no_connection_supabase')} - {t('reports.generating_sample_reports')}")
        
        # Report configuration
        render_report_configuration()
        
        # Generate and display reports based on configuration
        if st.session_state.get('generate_report', False):
            render_generated_report()
        
    except Exception as e:
        st.error(f"{t('reports.error_loading_page')}: {e}")
        logger.error(f"Reports page rendering error: {e}", exc_info=True)

def render_report_configuration():
    """Render report configuration options."""
    bilingual_subheader("reports.report_configuration", "📋")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Report type selection
        report_type = bilingual_selectbox(
            "reports.report_type",
            options=[
                t("reports.executive_report"),
                t("reports.agents_performance_analysis"),
                t("reports.detailed_calls_analysis"),
                t("reports.conversion_report"),
                t("reports.temporal_analysis"),
                t("reports.custom_report")
            ],
            key="report_type"
        )
        
        # Date range for report
        col1_1, col1_2 = st.columns(2)
        with col1_1:
            start_date = st.date_input(
                t("reports.start_date"),
                value=datetime.now().date() - timedelta(days=30),
                key="report_start_date"
            )
        with col1_2:
            end_date = st.date_input(
                t("reports.end_date"),
                value=datetime.now().date(),
                key="report_end_date"
            )
    
    with col2:
        # Report format options
        report_format = bilingual_selectbox(
            "reports.export_format",
            options=["PDF", "Excel", "CSV", t("reports.visualization_only")],
            key="report_format"
        )
        
        # Additional options
        include_charts = st.checkbox(t("reports.include_charts"), value=True, key="include_charts")
        include_raw_data = st.checkbox(t("reports.include_detailed_data"), value=False, key="include_raw_data")
        
        # Custom filters for personalized reports
        if report_type == t("reports.custom_report"):
            st.markdown(f"**{t('reports.custom_filters')}:**")
            custom_agent_filter = st.multiselect(
                t("reports.specific_agents"),
                options=[],  # Would be populated from agents data
                key="custom_agent_filter"
            )
            
            custom_status_filter = st.multiselect(
                t("reports.call_statuses"),
                options=["completed", "failed", "busy", "no_answer", "cancelled"],
                key="custom_status_filter"
            )
    
    # Generate report button
    if st.button(f"🔄 {t('reports.generate_report')}", key="generate_report_btn", type="primary"):
        st.session_state.generate_report = True
        st.session_state.report_config = {
            'type': report_type,
            'start_date': start_date.strftime("%Y-%m-%d"),
            'end_date': end_date.strftime("%Y-%m-%d"),
            'format': report_format,
            'include_charts': include_charts,
            'include_raw_data': include_raw_data
        }
        st.rerun()

def render_generated_report():
    """Render the generated report based on configuration."""
    config = st.session_state.get('report_config', {})
    
    if not config:
        st.error(t("reports.no_report_config"))
        return
    
    st.markdown("---")
    st.markdown(f"## 📊 {config['type']}")
    st.markdown(f"**{t('reports.period')}:** {config['start_date']} {t('common.to')} {config['end_date']}")
    st.markdown(f"**{t('reports.generated')}:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Generate report content based on type
    if config['type'] == t("reports.executive_report"):
        render_executive_report(config)
    elif config['type'] == t("reports.agents_performance_analysis"):
        render_agents_performance_report(config)
    elif config['type'] == t("reports.detailed_calls_analysis"):
        render_detailed_calls_report(config)
    elif config['type'] == t("reports.conversion_report"):
        render_conversion_report(config)
    elif config['type'] == t("reports.temporal_analysis"):
        render_temporal_analysis_report(config)
    elif config['type'] == t("reports.custom_report"):
        render_custom_report(config)
    
    # Export options
    render_export_options(config)

def render_executive_report(config):
    """Render executive summary report."""
    bilingual_subheader("reports.executive_summary", "📈")
    
    try:
        # Get data
        metrics = get_dashboard_metrics((config['start_date'], config['end_date']))
        agents_df = get_agents_performance((config['start_date'], config['end_date']))
        calls_df = get_calls_data((config['start_date'], config['end_date']), limit=5000)
        
        # Key metrics summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            bilingual_metric("dashboard.total_calls", f"{metrics['total_calls']:,}", "📞")
        with col2:
            bilingual_metric("dashboard.conversion_rate", f"{metrics['conversion_rate']:.1f}%", "✅")
        with col3:
            bilingual_metric("dashboard.avg_duration", f"{metrics['avg_duration']:.1f} min", "⏱️")
        with col4:
            bilingual_metric("dashboard.unique_agents", f"{metrics['unique_agents']:,}", "👥")
        
        # Executive insights
        st.markdown(f"#### 🎯 {t('reports.key_insights')}")
        
        insights = []
        
        # Performance insights
        if metrics['conversion_rate'] >= 70:
            insights.append(f"✅ **{t('reports.excellent_performance')}**: {t('reports.conversion_exceeds_70')}")
        elif metrics['conversion_rate'] >= 50:
            insights.append(f"⚠️ **{t('reports.moderate_performance')}**: {t('reports.conversion_between_50_70')}")
        else:
            insights.append(f"🔴 **{t('reports.improvement_area')}**: {t('reports.conversion_below_50')}")
        
        # Volume insights
        avg_calls_per_day = metrics['total_calls'] / max(1, (datetime.strptime(config['end_date'], "%Y-%m-%d") - datetime.strptime(config['start_date'], "%Y-%m-%d")).days + 1)
        insights.append(f"📊 **{t('reports.daily_average_volume')}**: {avg_calls_per_day:.1f} {t('reports.calls_per_day')}")
        
        # Agent insights
        if not agents_df.empty:
            top_agent = agents_df.loc[agents_df['conversion_rate'].idxmax()]
            insights.append(f"🏆 **{t('reports.best_agent')}**: {top_agent['name']} {t('common.with')} {top_agent['conversion_rate']:.1f}% {t('common.of')} {t('reports.conversion')}")
        
        for insight in insights:
            st.markdown(f"- {insight}")
        
        # Charts for executive report
        if config.get('include_charts', True):
            col1, col2 = st.columns(2)
            
            with col1:
                # Conversion trend
                if not calls_df.empty:
                    calls_df['call_date'] = pd.to_datetime(calls_df['call_date'])
                    daily_conversion = calls_df.groupby(calls_df['call_date'].dt.date).agg({
                        'call_status': ['count', lambda x: (x == 'completed').sum()]
                    })
                    daily_conversion.columns = ['total', 'successful']
                    daily_conversion['conversion_rate'] = (daily_conversion['successful'] / daily_conversion['total'] * 100).round(2)
                    
                    fig = px.line(
                        x=daily_conversion.index,
                        y=daily_conversion['conversion_rate'],
                        title=t("reports.daily_conversion_trend"),
                        labels={'x': t('common.date'), 'y': f"{t('reports.conversion_rate')} (%)"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top agents performance
                if not agents_df.empty:
                    top_5_agents = agents_df.nlargest(5, 'conversion_rate')
                    fig = px.bar(
                        top_5_agents,
                        x='name',
                        y='conversion_rate',
                        title=t("reports.top_5_agents_conversion"),
                        labels={'name': t('common.agent'), 'conversion_rate': f"{t('reports.conversion')} (%)"}
                    )
                    fig.update_xaxes(tickangle=-45)
                    st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"{t('reports.error_generating_executive')}: {e}")
        logger.error(f"Executive report error: {e}")

def render_agents_performance_report(config):
    """Render agents performance report."""
    bilingual_subheader("reports.agents_performance_analysis", "👥")
    
    try:
        agents_df = get_agents_performance((config['start_date'], config['end_date']))
        
        if agents_df.empty:
            st.info(t("reports.no_agents_data"))
            return
        
        # Performance summary
        st.markdown(f"#### 📊 {t('reports.performance_summary')}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_conversion = agents_df['conversion_rate'].mean()
            bilingual_metric("reports.average_conversion", f"{avg_conversion:.1f}%")
        
        with col2:
            top_performer = agents_df.loc[agents_df['conversion_rate'].idxmax()]
            bilingual_metric("reports.best_performance", f"{top_performer['conversion_rate']:.1f}%")
        
        with col3:
            total_calls = agents_df['total_calls'].sum()
            bilingual_metric("dashboard.total_calls", f"{total_calls:,}")
        
        # Detailed agents table
        st.markdown(f"#### 📋 {t('reports.detailed_performance_by_agent')}")
        
        display_df = agents_df[['name', 'total_calls', 'successful_calls', 'conversion_rate', 'avg_duration']].copy()
        display_df.columns = [t('common.agent'), t('reports.total_calls'), t('reports.successful'), f"{t('reports.conversion')} (%)", f"{t('reports.avg_duration')} (min)"]
        display_df = display_df.sort_values(f"{t('reports.conversion')} (%)", ascending=False)
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Performance distribution chart
        if config.get('include_charts', True):
            fig = px.histogram(
                agents_df,
                x='conversion_rate',
                nbins=10,
                title=t("reports.conversion_rates_distribution"),
                labels={'conversion_rate': f"{t('reports.conversion_rate')} (%)", 'count': t('reports.number_of_agents')}
            )
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"{t('reports.error_generating_agents')}: {e}")
        logger.error(f"Agents performance report error: {e}")

def render_detailed_calls_report(config):
    """Render detailed calls analysis report."""
    bilingual_subheader("reports.detailed_calls_analysis", "📞")
    
    try:
        calls_df = get_calls_data((config['start_date'], config['end_date']), limit=10000)
        
        if calls_df.empty:
            st.info(t("reports.no_calls_data"))
            return
        
        # Call statistics
        st.markdown(f"#### 📊 {t('reports.call_statistics')}")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            bilingual_metric("dashboard.total_calls", f"{len(calls_df):,}")
        
        with col2:
            successful = len(calls_df[calls_df['call_status'] == 'completed']) if 'call_status' in calls_df.columns else 0
            bilingual_metric("reports.successful_calls", f"{successful:,}")
        
        with col3:
            avg_duration = calls_df['duration_minutes'].mean() if 'duration_minutes' in calls_df.columns else 0
            bilingual_metric("reports.average_duration", f"{avg_duration:.1f} min")
        
        with col4:
            total_time = calls_df['duration_minutes'].sum() if 'duration_minutes' in calls_df.columns else 0
            bilingual_metric("reports.total_time", f"{total_time:.0f} min")
        
        # Status distribution
        if 'call_status' in calls_df.columns:
            st.markdown(f"#### 🎯 {t('reports.status_distribution')}")
            status_counts = calls_df['call_status'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                for status, count in status_counts.items():
                    percentage = (count / len(calls_df)) * 100
                    st.write(f"**{status}**: {count:,} ({percentage:.1f}%)")
            
            with col2:
                if config.get('include_charts', True):
                    fig = px.pie(
                        values=status_counts.values,
                        names=status_counts.index,
                        title=t("reports.status_distribution")
                    )
                    st.plotly_chart(fig, use_container_width=True)
        
        # Time analysis
        if 'call_date' in calls_df.columns and config.get('include_charts', True):
            st.markdown(f"#### ⏰ {t('reports.temporal_analysis')}")
            
            calls_df['call_date'] = pd.to_datetime(calls_df['call_date'])
            calls_df['hour'] = calls_df['call_date'].dt.hour
            calls_df['weekday'] = calls_df['call_date'].dt.day_name()
            
            col1, col2 = st.columns(2)
            
            with col1:
                hourly_dist = calls_df['hour'].value_counts().sort_index()
                fig = px.bar(
                    x=hourly_dist.index,
                    y=hourly_dist.values,
                    title=t("reports.hourly_distribution"),
                    labels={'x': t('reports.hour'), 'y': t('reports.number_of_calls')}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                weekday_dist = calls_df['weekday'].value_counts()
                fig = px.bar(
                    x=weekday_dist.index,
                    y=weekday_dist.values,
                    title=t("reports.weekday_distribution"),
                    labels={'x': t('reports.day'), 'y': t('reports.number_of_calls')}
                )
                st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"{t('reports.error_generating_calls')}: {e}")
        logger.error(f"Detailed calls report error: {e}")

def render_conversion_report(config):
    """Render conversion analysis report."""
    bilingual_subheader("reports.conversion_analysis", "🎯")
    
    try:
        calls_df = get_calls_data((config['start_date'], config['end_date']), limit=10000)
        
        if calls_df.empty:
            st.info(t("reports.no_conversion_data"))
            return
        
        # Conversion metrics
        total_calls = len(calls_df)
        successful_calls = len(calls_df[calls_df['call_status'] == 'completed']) if 'call_status' in calls_df.columns else 0
        conversion_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
        
        st.markdown(f"#### 📊 {t('reports.conversion_metrics')}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            bilingual_metric("reports.general_conversion_rate", f"{conversion_rate:.1f}%")
        
        with col2:
            bilingual_metric("reports.converted_calls", f"{successful_calls:,}")
        
        with col3:
            bilingual_metric("reports.missed_opportunities", f"{total_calls - successful_calls:,}")
        
        # Conversion by different dimensions
        if config.get('include_charts', True):
            st.markdown(f"#### 📈 {t('reports.conversion_analysis_by_dimensions')}")
            
            # Daily conversion trend
            if 'call_date' in calls_df.columns:
                calls_df['call_date'] = pd.to_datetime(calls_df['call_date'])
                daily_conversion = calls_df.groupby(calls_df['call_date'].dt.date).agg({
                    'call_status': ['count', lambda x: (x == 'completed').sum()]
                })
                daily_conversion.columns = ['total', 'successful']
                daily_conversion['conversion_rate'] = (daily_conversion['successful'] / daily_conversion['total'] * 100).round(2)
                
                fig = px.line(
                    x=daily_conversion.index,
                    y=daily_conversion['conversion_rate'],
                    title=t("reports.daily_conversion_trend"),
                    labels={'x': t('common.date'), 'y': f"{t('reports.conversion_rate')} (%)"}
                )
                
                # Add average line
                avg_line = daily_conversion['conversion_rate'].mean()
                fig.add_hline(y=avg_line, line_dash="dash", annotation_text=f"{t('reports.average')}: {avg_line:.1f}%")
                
                st.plotly_chart(fig, use_container_width=True)
        
        # Conversion factors analysis
        st.markdown(f"#### 🔍 {t('reports.conversion_factors')}")
        
        factors_analysis = []
        
        # Duration impact
        if 'duration_minutes' in calls_df.columns:
            successful_df = calls_df[calls_df['call_status'] == 'completed']
            failed_df = calls_df[calls_df['call_status'] != 'completed']
            
            if not successful_df.empty and not failed_df.empty:
                avg_duration_success = successful_df['duration_minutes'].mean()
                avg_duration_failed = failed_df['duration_minutes'].mean()
                
                factors_analysis.append(f"**{t('reports.avg_duration_successful')}**: {avg_duration_success:.1f} min")
                factors_analysis.append(f"**{t('reports.avg_duration_failed')}**: {avg_duration_failed:.1f} min")
                
                if avg_duration_success > avg_duration_failed:
                    factors_analysis.append(f"✅ {t('reports.longer_calls_more_successful')}")
                else:
                    factors_analysis.append(f"⚠️ {t('reports.shorter_calls_more_successful')}")
        
        # Time-based patterns
        if 'call_date' in calls_df.columns:
            calls_df['hour'] = calls_df['call_date'].dt.hour
            hourly_conversion = calls_df.groupby('hour').agg({
                'call_status': ['count', lambda x: (x == 'completed').sum()]
            })
            hourly_conversion.columns = ['total', 'successful']
            hourly_conversion['conversion_rate'] = (hourly_conversion['successful'] / hourly_conversion['total'] * 100).round(2)
            
            best_hour = hourly_conversion['conversion_rate'].idxmax()
            best_rate = hourly_conversion['conversion_rate'].max()
            
            factors_analysis.append(f"**{t('reports.best_hour_calls')}**: {best_hour}:00 {t('common.with')} {best_rate:.1f}% {t('common.of')} {t('reports.conversion')}")
        
        for factor in factors_analysis:
            st.markdown(f"- {factor}")
        
    except Exception as e:
        st.error(f"{t('reports.error_generating_conversion')}: {e}")
        logger.error(f"Conversion report error: {e}")

def render_temporal_analysis_report(config):
    """Render temporal analysis report."""
    bilingual_subheader("reports.temporal_analysis", "⏰")
    
    try:
        calls_df = get_calls_data((config['start_date'], config['end_date']), limit=10000)
        
        if calls_df.empty or 'call_date' not in calls_df.columns:
            st.info(t("reports.no_temporal_data"))
            return
        
        calls_df['call_date'] = pd.to_datetime(calls_df['call_date'])
        
        # Time-based analysis
        st.markdown(f"#### 📅 {t('reports.temporal_patterns')}")
        
        # Daily patterns
        daily_stats = calls_df.groupby(calls_df['call_date'].dt.date).agg({
            'id': 'count',
            'call_status': lambda x: (x == 'completed').sum() if 'call_status' in calls_df.columns else 0
        })
        daily_stats.columns = ['total_calls', 'successful_calls']
        daily_stats['conversion_rate'] = (daily_stats['successful_calls'] / daily_stats['total_calls'] * 100).round(2)
        
        col1, col2 = st.columns(2)
        
        with col1:
            best_day = daily_stats['total_calls'].idxmax()
            best_volume = daily_stats['total_calls'].max()
            st.metric(t("reports.highest_volume_day"), f"{best_day}", f"{best_volume:,} {t('reports.calls')}")
        
        with col2:
            best_conversion_day = daily_stats['conversion_rate'].idxmax()
            best_conversion_rate = daily_stats['conversion_rate'].max()
            st.metric(t("reports.best_conversion_day"), f"{best_conversion_day}", f"{best_conversion_rate:.1f}%")
        
        # Hourly and weekly patterns
        if config.get('include_charts', True):
            calls_df['hour'] = calls_df['call_date'].dt.hour
            calls_df['weekday'] = calls_df['call_date'].dt.day_name()
            
            col1, col2 = st.columns(2)
            
            with col1:
                hourly_volume = calls_df['hour'].value_counts().sort_index()
                fig = px.bar(
                    x=hourly_volume.index,
                    y=hourly_volume.values,
                    title=t("reports.volume_by_hour"),
                    labels={'x': t('reports.hour'), 'y': t('reports.number_of_calls')}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                weekday_volume = calls_df['weekday'].value_counts()
                fig = px.bar(
                    x=weekday_volume.index,
                    y=weekday_volume.values,
                    title=t("reports.volume_by_weekday"),
                    labels={'x': t('reports.day'), 'y': t('reports.number_of_calls')}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Heatmap of activity
            calls_df['weekday_num'] = calls_df['call_date'].dt.dayofweek
            heatmap_data = calls_df.groupby(['weekday_num', 'hour']).size().reset_index(name='count')
            heatmap_pivot = heatmap_data.pivot(index='weekday_num', columns='hour', values='count').fillna(0)
            
            fig = px.imshow(
                heatmap_pivot,
                title=t("reports.activity_heatmap"),
                labels={'x': t('reports.hour_of_day'), 'y': t('reports.day_of_week'), 'color': t('reports.number_of_calls')},
                aspect="auto"
            )
            
            # Update y-axis labels
            weekday_labels = [t('reports.mon'), t('reports.tue'), t('reports.wed'), t('reports.thu'), t('reports.fri'), t('reports.sat'), t('reports.sun')]
            fig.update_yaxes(tickvals=list(range(7)), ticktext=weekday_labels)
            
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"{t('reports.error_generating_temporal')}: {e}")
        logger.error(f"Temporal analysis report error: {e}")

def render_custom_report(config):
    """Render custom report based on user configuration."""
    bilingual_subheader("reports.custom_report", "🔧")
    
    st.info(t("reports.custom_functionality_development"))
    
    # Show a combination of different analyses
    render_executive_report(config)
    render_conversion_report(config)

def render_export_options(config):
    """Render export options for the report."""
    st.markdown("---")
    bilingual_subheader("reports.export_options", "📥")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button(f"📄 {t('reports.export_pdf')}", key="export_pdf"):
            st.info(t("reports.pdf_export_development"))
    
    with col2:
        if st.button(f"📊 {t('reports.export_excel')}", key="export_excel"):
            # Generate Excel export
            try:
                excel_data = generate_excel_export(config)
                st.download_button(
                    label=t("reports.download_excel"),
                    data=excel_data,
                    file_name=f"reporte_{config['type'].lower().replace(' ', '_')}_{config['start_date']}_to_{config['end_date']}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"{t('reports.error_generating_excel')}: {e}")
    
    with col3:
        if st.button(f"📋 {t('reports.export_csv')}", key="export_csv"):
            # Generate CSV export
            try:
                csv_data = generate_csv_export(config)
                st.download_button(
                    label=t("reports.download_csv"),
                    data=csv_data,
                    file_name=f"reporte_{config['type'].lower().replace(' ', '_')}_{config['start_date']}_to_{config['end_date']}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"{t('reports.error_generating_csv')}: {e}")

def generate_excel_export(config):
    """Generate Excel export data."""
    try:
        # Get data based on report type
        metrics = get_dashboard_metrics((config['start_date'], config['end_date']))
        agents_df = get_agents_performance((config['start_date'], config['end_date']))
        calls_df = get_calls_data((config['start_date'], config['end_date']), limit=5000)
        
        # Create Excel file in memory
        output = io.BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Summary sheet
            summary_data = {
                t('reports.metric'): [t('dashboard.total_calls'), t('reports.successful_calls'), f"{t('reports.conversion_rate')} (%)", f"{t('reports.avg_duration')} (min)", t('dashboard.unique_agents')],
                t('reports.value'): [metrics['total_calls'], metrics['successful_calls'], metrics['conversion_rate'], metrics['avg_duration'], metrics['unique_agents']]
            }
            pd.DataFrame(summary_data).to_excel(writer, sheet_name=t('reports.summary'), index=False)
            
            # Agents data
            if not agents_df.empty:
                agents_df.to_excel(writer, sheet_name=t('reports.agents'), index=False)
            
            # Calls data (sample)
            if not calls_df.empty:
                calls_sample = calls_df.head(1000)  # Limit to avoid large files
                calls_sample.to_excel(writer, sheet_name=t('reports.calls'), index=False)
        
        output.seek(0)
        return output.getvalue()
        
    except Exception as e:
        logger.error(f"Excel export error: {e}")
        raise

def generate_csv_export(config):
    """Generate CSV export data."""
    try:
        # Get calls data for CSV export
        calls_df = get_calls_data((config['start_date'], config['end_date']), limit=5000)
        
        if calls_df.empty:
            return t("reports.no_data_export")
        
        return calls_df.to_csv(index=False)
        
    except Exception as e:
        logger.error(f"CSV export error: {e}")
        raise