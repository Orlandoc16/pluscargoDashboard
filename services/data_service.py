"""
Data service simplificado para Call Analytics Dashboard.
Enfocado exclusivamente en leads_pluscargo_basic y call_results_pluscargo_basic
"""
import pandas as pd
import streamlit as st
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
import logging
from services.supabase_client import execute_query
from config.settings import LEADS_TABLE, CALL_RESULTS_TABLE, CACHE_TTL

logger = logging.getLogger(__name__)

class DataService:
    """Service class simplificado para operaciones de datos."""
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL)
    def get_leads_summary() -> Dict[str, Any]:
        """Get summary of leads data."""
        try:
            # Get all leads
            result = execute_query(
                table=LEADS_TABLE,
                columns="estado_lead",
                filters={}
            )
            
            if result["error"]:
                logger.error(f"Error fetching leads summary: {result['error']}")
                return {"total_active_leads": 0, "converted_leads": 0}
            
            df = pd.DataFrame(result["data"])
            
            if df.empty:
                return {"total_active_leads": 0, "converted_leads": 0}
            
            # Calculate metrics
            total_active_leads = len(df[df["estado_lead"] != "no_interesado"])
            converted_leads = len(df[df["estado_lead"].isin(["calificado", "cotizacion_gratis"])])
            
            return {
                "total_active_leads": total_active_leads,
                "converted_leads": converted_leads
            }
            
        except Exception as e:
            logger.error(f"Error in get_leads_summary: {e}")
            return {"total_active_leads": 0, "converted_leads": 0}
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL)
    def get_calls_summary(date_range: Tuple) -> Dict[str, Any]:
        """Get summary of calls data for date range."""
        try:
            start_date = date_range[0].strftime("%Y-%m-%d")
            end_date = date_range[1].strftime("%Y-%m-%d")
            
            # Get calls data
            calls_result = execute_query(
                table=CALL_RESULTS_TABLE,
                columns="resultado_llamada, lead_id",
                filters={"fecha_llamada": {"gte": start_date, "lte": end_date}}
            )
            
            # Get leads data for proper calculations
            leads_result = execute_query(
                table=LEADS_TABLE,
                columns="id, estado_lead",
                filters={}
            )
            
            if calls_result["error"] or leads_result["error"]:
                logger.error(f"Error fetching data: calls={calls_result.get('error')}, leads={leads_result.get('error')}")
                return {"total_calls": 0, "contact_rate": 0, "conversion_rate": 0, "calls_per_lead": 0}
            
            calls_df = pd.DataFrame(calls_result["data"])
            leads_df = pd.DataFrame(leads_result["data"])
            
            if calls_df.empty or leads_df.empty:
                return {"total_calls": 0, "contact_rate": 0, "conversion_rate": 0, "calls_per_lead": 0}
            
            # Basic metrics
            total_calls = len(calls_df)
            total_leads = len(leads_df)
            
            # Contact rate: percentage of leads that have been contacted (have at least one call)
            contacted_leads = calls_df['lead_id'].nunique() if 'lead_id' in calls_df.columns else 0
            contact_rate = (contacted_leads / total_leads * 100) if total_leads > 0 else 0
            
            # Conversion rate: percentage of leads that are converted (calificado or cotizacion_gratis)
            converted_leads = len(leads_df[leads_df["estado_lead"].isin(["calificado", "cotizacion_gratis"])])
            conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
            
            # Calls per lead: average number of calls per lead
            calls_per_lead = (total_calls / total_leads) if total_leads > 0 else 0
            
            # Success rate for calls (for the "Éxito en Llamadas" metric)
            successful_calls = len(calls_df[calls_df["resultado_llamada"] == "exitosa"])
            success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
            
            return {
                "total_calls": total_calls,
                "contact_rate": round(contact_rate, 1),
                "conversion_rate": round(conversion_rate, 1),
                "calls_per_lead": round(calls_per_lead, 1),
                "success_rate": round(success_rate, 1),
                "contacted_leads": contacted_leads,
                "converted_leads": converted_leads
            }
            
        except Exception as e:
            logger.error(f"Error in get_calls_summary: {e}")
            return {"total_calls": 0, "contact_rate": 0, "conversion_rate": 0, "calls_per_lead": 0}
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL)
    def get_leads_evolution(date_range: Tuple) -> pd.DataFrame:
        """Get leads evolution by status over time."""
        try:
            # For now, return empty DataFrame - would need created_at or similar timestamp
            # This would require analyzing the actual data structure
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error in get_leads_evolution: {e}")
            return pd.DataFrame()
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL)
    def get_daily_calls_volume(date_range: Tuple) -> pd.DataFrame:
        """Get daily calls volume."""
        try:
            start_date = date_range[0].strftime("%Y-%m-%d")
            end_date = date_range[1].strftime("%Y-%m-%d")
            
            result = execute_query(
                table=CALL_RESULTS_TABLE,
                columns="fecha_llamada",
                filters={"fecha_llamada": {"gte": start_date, "lte": end_date}}
            )
            
            if result["error"] or not result["data"]:
                return pd.DataFrame()
            
            df = pd.DataFrame(result["data"])
            df['fecha_llamada'] = pd.to_datetime(df['fecha_llamada'])
            
            # Group by date
            daily_volume = df.groupby(df['fecha_llamada'].dt.date).size().reset_index(name='total_llamadas')
            daily_volume['fecha'] = pd.to_datetime(daily_volume['fecha_llamada'])
            
            return daily_volume
            
        except Exception as e:
            logger.error(f"Error in get_daily_calls_volume: {e}")
            return pd.DataFrame()
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL)
    def get_calls_by_result(date_range: Tuple) -> pd.DataFrame:
        """Get calls distribution by result."""
        try:
            start_date = date_range[0].strftime("%Y-%m-%d")
            end_date = date_range[1].strftime("%Y-%m-%d")
            
            result = execute_query(
                table=CALL_RESULTS_TABLE,
                columns="resultado_llamada",
                filters={"fecha_llamada": {"gte": start_date, "lte": end_date}}
            )
            
            if result["error"] or not result["data"]:
                return pd.DataFrame()
            
            df = pd.DataFrame(result["data"])
            
            # Group by result
            result_counts = df['resultado_llamada'].value_counts().reset_index()
            result_counts.columns = ['resultado_llamada', 'cantidad']
            
            return result_counts
            
        except Exception as e:
            logger.error(f"Error in get_calls_by_result: {e}")
            return pd.DataFrame()
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL)
    def get_conversion_funnel(date_range: Tuple) -> Dict[str, int]:
        """Get conversion funnel data."""
        try:
            # Get leads data
            leads_result = execute_query(
                table=LEADS_TABLE,
                columns="estado_lead",
                filters={}
            )
            
            if leads_result["error"] or not leads_result["data"]:
                return {}
            
            df = pd.DataFrame(leads_result["data"])
            
            # Create funnel stages
            funnel = {
                "Total Leads": len(df),
                "Contactados": len(df[df["estado_lead"] != "no_contactado"]),
                "Interesados": len(df[df["estado_lead"].isin(["interesado", "calificado", "cotizacion_gratis"])]),
                "Calificados": len(df[df["estado_lead"] == "calificado"]),
                "Convertidos": len(df[df["estado_lead"] == "cotizacion_gratis"])
            }
            
            return funnel
            
        except Exception as e:
            logger.error(f"Error in get_conversion_funnel: {e}")
            return {}
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL)
    def get_executive_summary(date_range: Tuple) -> Dict[str, Any]:
        """Get executive summary data."""
        try:
            # Get leads distribution
            leads_result = execute_query(
                table=LEADS_TABLE,
                columns="estado_lead",
                filters={}
            )
            
            # Get calls performance
            start_date = date_range[0].strftime("%Y-%m-%d")
            end_date = date_range[1].strftime("%Y-%m-%d")
            
            calls_result = execute_query(
                table=CALL_RESULTS_TABLE,
                columns="resultado_llamada, duracion_segundos, fecha_llamada",
                filters={"fecha_llamada": {"gte": start_date, "lte": end_date}}
            )
            
            summary = {}
            
            # Process leads distribution
            if not leads_result["error"] and leads_result["data"]:
                leads_df = pd.DataFrame(leads_result["data"])
                summary["leads_distribution"] = leads_df["estado_lead"].value_counts().to_dict()
            
            # Process calls performance
            if not calls_result["error"] and calls_result["data"]:
                calls_df = pd.DataFrame(calls_result["data"])
                
                total_calls = len(calls_df)
                successful_calls = len(calls_df[calls_df["resultado_llamada"] == "exitosa"])
                success_rate = (successful_calls / total_calls * 100) if total_calls > 0 else 0
                
                avg_duration = calls_df["duracion_segundos"].mean() / 60 if "duracion_segundos" in calls_df.columns else 0
                
                # Find best hour (simplified)
                calls_df['fecha_llamada'] = pd.to_datetime(calls_df['fecha_llamada'])
                best_hour = calls_df['fecha_llamada'].dt.hour.mode().iloc[0] if not calls_df.empty else "N/A"
                
                summary["calls_performance"] = {
                    "success_rate": round(success_rate, 1),
                    "avg_duration": round(avg_duration, 1),
                    "best_hour": f"{best_hour}:00" if best_hour != "N/A" else "N/A"
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error in get_executive_summary: {e}")
            return {}
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL)
    def get_lead_statuses() -> List[str]:
        """Get list of available lead statuses."""
        try:
            result = execute_query(
                table=LEADS_TABLE,
                columns="estado_lead",
                filters={}
            )
            
            if result["error"] or not result["data"]:
                logger.error(f"Error fetching lead statuses: {result.get('error')}")
                return ["nuevo", "contactado", "interesado", "calificado", "cotizacion_gratis", "no_interesado"]
            
            df = pd.DataFrame(result["data"])
            if df.empty or "estado_lead" not in df.columns:
                return ["nuevo", "contactado", "interesado", "calificado", "cotizacion_gratis", "no_interesado"]
            
            # Get unique statuses and sort them
            statuses = df["estado_lead"].dropna().unique().tolist()
            return sorted(statuses)
            
        except Exception as e:
            logger.error(f"Error in get_lead_statuses: {e}")
            return ["nuevo", "contactado", "interesado", "calificado", "cotizacion_gratis", "no_interesado"]
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL)
    def get_industries() -> List[str]:
        """Get list of available industries."""
        try:
            result = execute_query(
                table=LEADS_TABLE,
                columns="rubro",
                filters={}
            )
            
            if result["error"] or not result["data"]:
                logger.error(f"Error fetching industries: {result.get('error')}")
                return ["tecnologia", "servicios", "manufactura", "comercio", "salud", "educacion"]
            
            df = pd.DataFrame(result["data"])
            if df.empty or "rubro" not in df.columns:
                return ["tecnologia", "servicios", "manufactura", "comercio", "salud", "educacion"]
            
            # Get unique industries and sort them
            industries = df["rubro"].dropna().unique().tolist()
            return sorted(industries)
            
        except Exception as e:
            logger.error(f"Error in get_industries: {e}")
            return ["tecnologia", "servicios", "manufactura", "comercio", "salud", "educacion"]
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL)
    def get_leads_count(estado_filter: Optional[str] = None, rubro_filter: Optional[str] = None, fecha_filter: Optional[Tuple] = None) -> int:
        """Get count of leads with optional filters."""
        try:
            query_filters = {}
            
            # Apply filters
            if estado_filter:
                query_filters["estado_lead"] = estado_filter
            
            if rubro_filter:
                query_filters["rubro"] = rubro_filter
            
            if fecha_filter and len(fecha_filter) == 2:
                start_date = fecha_filter[0].strftime("%Y-%m-%d") if hasattr(fecha_filter[0], 'strftime') else str(fecha_filter[0])
                end_date = fecha_filter[1].strftime("%Y-%m-%d") if hasattr(fecha_filter[1], 'strftime') else str(fecha_filter[1])
                query_filters["created_at"] = {"gte": start_date, "lte": end_date}
            
            result = execute_query(
                table=LEADS_TABLE,
                columns="id",
                filters=query_filters
            )
            
            if result["error"]:
                logger.error(f"Error fetching leads count: {result['error']}")
                return 0
            
            return len(result["data"]) if result["data"] else 0
            
        except Exception as e:
            logger.error(f"Error in get_leads_count: {e}")
            return 0

    @staticmethod
    @st.cache_data(ttl=CACHE_TTL)
    def get_leads_data(estado_filter: Optional[str] = None, rubro_filter: Optional[str] = None, fecha_filter: Optional[Tuple] = None, limit: int = 100, offset: int = 0) -> pd.DataFrame:
        """Get leads data with optional filters - compatible with _leads.py usage."""
        try:
            query_filters = {}
            
            # Apply filters
            if estado_filter:
                query_filters["estado_lead"] = estado_filter
            
            if rubro_filter:
                query_filters["rubro"] = rubro_filter
            
            if fecha_filter and len(fecha_filter) == 2:
                start_date = fecha_filter[0].strftime("%Y-%m-%d") if hasattr(fecha_filter[0], 'strftime') else str(fecha_filter[0])
                end_date = fecha_filter[1].strftime("%Y-%m-%d") if hasattr(fecha_filter[1], 'strftime') else str(fecha_filter[1])
                query_filters["created_at"] = {"gte": start_date, "lte": end_date}
            
            result = execute_query(
                table=LEADS_TABLE,
                columns="*",
                filters=query_filters,
                limit=limit,
                order_by="-created_at"
            )
            
            if result["error"]:
                logger.error(f"Error fetching leads data: {result['error']}")
                return pd.DataFrame()
            
            df = pd.DataFrame(result["data"])
            
            # Add calculated fields that _leads.py expects
            if not df.empty:
                # Map database column names to expected names
                if 'created_at' in df.columns and 'fecha_creacion' not in df.columns:
                    df['fecha_creacion'] = df['created_at']
                
                # Add intentos_llamada column if not present
                if "intentos_llamada" not in df.columns:
                    df["intentos_llamada"] = 0
                
                # Add ultima_llamada column if not present
                if "ultima_llamada" not in df.columns:
                    df["ultima_llamada"] = None
                
                # Ensure numeric columns are properly typed
                if "intentos_llamada" in df.columns:
                    df["intentos_llamada"] = pd.to_numeric(df["intentos_llamada"], errors='coerce').fillna(0)
            
            return df
            
        except Exception as e:
            logger.error(f"Error in get_leads_data: {e}")
            return pd.DataFrame()
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL)
    def get_calls_data(date_range: Tuple, filters: Optional[Dict] = None, limit: int = 100) -> pd.DataFrame:
        """Get calls data with optional filters and lead names."""
        try:
            start_date = date_range[0].strftime("%Y-%m-%d")
            end_date = date_range[1].strftime("%Y-%m-%d")
            
            query_filters = {"fecha_llamada": {"gte": start_date, "lte": end_date}}
            if filters:
                query_filters.update(filters)
            
            # Get calls data
            result = execute_query(
                table=CALL_RESULTS_TABLE,
                columns="*",
                filters=query_filters,
                limit=limit,
                order_by="-fecha_llamada"
            )
            
            if result["error"]:
                logger.error(f"Error fetching calls data: {result['error']}")
                return pd.DataFrame()
            
            calls_df = pd.DataFrame(result["data"])
            
            if calls_df.empty:
                return calls_df
            
            # Get leads data to join with calls
            leads_result = execute_query(
                table=LEADS_TABLE,
                columns="id,nombre,apellido,nombre_empresa",
                filters={}
            )
            
            if leads_result["error"]:
                logger.error(f"Error fetching leads data for join: {leads_result['error']}")
                return calls_df
            
            leads_df = pd.DataFrame(leads_result["data"])
            
            if not leads_df.empty:
                # Create nombre_lead column combining nombre, apellido and nombre_empresa
                leads_df['nombre_lead'] = leads_df.apply(
                    lambda row: f"{row['nombre']} {row['apellido']} ({row['nombre_empresa']})" 
                    if pd.notna(row['nombre']) and pd.notna(row['apellido']) and pd.notna(row['nombre_empresa'])
                    else row['nombre_empresa'] if pd.notna(row['nombre_empresa'])
                    else f"{row['nombre']} {row['apellido']}" if pd.notna(row['nombre']) and pd.notna(row['apellido'])
                    else 'Lead sin nombre',
                    axis=1
                )
                
                # Join calls with leads data
                calls_df = calls_df.merge(
                    leads_df[['id', 'nombre_lead']], 
                    left_on='lead_id', 
                    right_on='id', 
                    how='left',
                    suffixes=('', '_lead')
                )
                
                # Fill missing lead names
                calls_df['nombre_lead'] = calls_df['nombre_lead'].fillna('Lead no encontrado')
                
                # Drop the extra id column from the join
                if 'id_lead' in calls_df.columns:
                    calls_df = calls_df.drop('id_lead', axis=1)
            
            return calls_df
            
        except Exception as e:
            logger.error(f"Error in get_calls_data: {e}")
            return pd.DataFrame()
    
    @staticmethod
    @st.cache_data(ttl=CACHE_TTL)
    def get_table_counts() -> Dict[str, Any]:
        """Get record counts for all tables."""
        try:
            counts = {"status": "success"}
            
            # Count leads
            try:
                leads_result = execute_query(
                    table=LEADS_TABLE,
                    columns="id",
                    filters={}
                )
                counts["leads_count"] = len(leads_result["data"]) if not leads_result["error"] else 0
                counts["leads_error"] = leads_result["error"]
            except Exception as e:
                counts["leads_count"] = 0
                counts["leads_error"] = str(e)
            
            # Count calls
            try:
                calls_result = execute_query(
                    table=CALL_RESULTS_TABLE,
                    columns="id",
                    filters={}
                )
                counts["calls_count"] = len(calls_result["data"]) if not calls_result["error"] else 0
                counts["calls_error"] = calls_result["error"]
            except Exception as e:
                counts["calls_count"] = 0
                counts["calls_error"] = str(e)
            
            # Agents count (set to 0 since we're not using agents table)
            counts["agents_count"] = 0
            counts["agents_error"] = None
            
            return counts
            
        except Exception as e:
            logger.error(f"Error in get_table_counts: {e}")
            return {
                "status": "error",
                "error": str(e),
                "leads_count": 0,
                "calls_count": 0,
                "agents_count": 0
            }

# Legacy functions for backward compatibility
@st.cache_data(ttl=CACHE_TTL)
def get_dashboard_metrics(date_range: Tuple[str, str], agent_filter: Optional[List[str]] = None) -> Dict[str, Any]:
    """Legacy function - use DataService.get_calls_summary instead."""
    try:
        # Convert string dates to date objects for DataService
        start_date = datetime.strptime(date_range[0], "%Y-%m-%d").date()
        end_date = datetime.strptime(date_range[1], "%Y-%m-%d").date()
        
        calls_data = DataService.get_calls_summary((start_date, end_date))
        
        return {
            "total_calls": calls_data.get("total_calls", 0),
            "successful_calls": int(calls_data.get("total_calls", 0) * calls_data.get("contact_rate", 0) / 100),
            "conversion_rate": calls_data.get("contact_rate", 0),
            "avg_duration": 0,  # Not available in simplified version
            "total_duration": 0,
            "unique_agents": 0,
            "status": "success"
        }
    except Exception as e:
        logger.error(f"Error in legacy get_dashboard_metrics: {e}")
        return {
            "total_calls": 0,
            "successful_calls": 0,
            "conversion_rate": 0,
            "avg_duration": 0,
            "total_duration": 0,
            "unique_agents": 0,
            "status": "error"
        }

@st.cache_data(ttl=CACHE_TTL)
def get_calls_data(date_range: Tuple[str, str], limit: int = 1000) -> pd.DataFrame:
    """Legacy function - use DataService.get_calls_data instead."""
    try:
        start_date = datetime.strptime(date_range[0], "%Y-%m-%d").date()
        end_date = datetime.strptime(date_range[1], "%Y-%m-%d").date()
        
        return DataService.get_calls_data((start_date, end_date), limit=limit)
    except Exception as e:
        logger.error(f"Error in legacy get_calls_data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=CACHE_TTL)
def get_agents_performance(date_range: Tuple[str, str]) -> pd.DataFrame:
    """Get agent performance metrics for the specified date range."""
    try:
        start_date, end_date = date_range
        
        # Get calls data for the date range
        result = execute_query(
            table=CALL_RESULTS_TABLE,
            columns="agent_id, resultado_llamada, duracion_segundos, fecha_llamada",
            filters={"fecha_llamada": f"gte.{start_date},lte.{end_date}"}
        )
        
        if result["error"]:
            logger.error(f"Error fetching agent performance data: {result['error']}")
            return pd.DataFrame()
        
        calls_df = pd.DataFrame(result["data"])
        
        if calls_df.empty or 'agent_id' not in calls_df.columns:
            return pd.DataFrame()
        
        # Convert date column
        calls_df['fecha_llamada'] = pd.to_datetime(calls_df['fecha_llamada'], errors='coerce')
        
        # Convert duration to minutes
        calls_df['duracion_minutos'] = pd.to_numeric(calls_df['duracion_segundos'], errors='coerce') / 60
        calls_df['duracion_minutos'] = calls_df['duracion_minutos'].fillna(0)
        
        # Group by agent and calculate metrics
        agent_metrics = calls_df.groupby('agent_id').agg({
            'agent_id': 'count',  # Total calls (using agent_id as counter)
            'resultado_llamada': lambda x: (x == 'exitosa').sum(),  # Successful calls
            'duracion_minutos': ['mean', 'sum'],  # Duration stats
            'fecha_llamada': ['min', 'max']  # Date range
        }).reset_index()
        
        # Flatten column names
        agent_metrics.columns = [
            'agent_id', 'total_calls', 'successful_calls', 
            'avg_duration', 'total_duration', 'first_call', 'last_call'
        ]
        
        # Calculate conversion rate
        agent_metrics['conversion_rate'] = (
            agent_metrics['successful_calls'] / agent_metrics['total_calls'] * 100
        ).round(2)
        
        # Calculate calls per day
        agent_metrics['days_active'] = (
            (agent_metrics['last_call'] - agent_metrics['first_call']).dt.days + 1
        ).fillna(1)
        agent_metrics['calls_per_day'] = (
            agent_metrics['total_calls'] / agent_metrics['days_active']
        ).round(2)
        
        # Add agent name (using agent_id as name for now)
        agent_metrics['name'] = 'Agente ' + agent_metrics['agent_id'].astype(str)
        
        # Sort by conversion rate
        agent_metrics = agent_metrics.sort_values('conversion_rate', ascending=False)
        
        logger.info(f"Calculated performance for {len(agent_metrics)} agents")
        return agent_metrics
        
    except Exception as e:
        logger.error(f"Error in get_agents_performance: {e}")
        return pd.DataFrame()