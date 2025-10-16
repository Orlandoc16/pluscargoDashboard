"""
Supabase client service with stable connections and retry logic.
"""
import logging
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import streamlit as st
from config.settings import (
    SUPABASE_URL, 
    SUPABASE_ANON_KEY, 
    SUPABASE_SERVICE_ROLE_KEY,
    MAX_RETRIES,
    TIMEOUT
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SupabaseClient:
    """Enhanced Supabase client with connection pooling and retry logic."""
    
    def __init__(self):
        self._client: Optional[Client] = None
        self._service_client: Optional[Client] = None
        self._connection_status = "disconnected"
        
    @property
    def client(self) -> Client:
        """Get or create the main Supabase client."""
        if self._client is None:
            try:
                self._client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
                self._connection_status = "connected"
                logger.info("Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase client: {e}")
                self._connection_status = "error"
                raise
        return self._client
    
    @property
    def service_client(self) -> Client:
        """Get or create the service role client for admin operations."""
        if self._service_client is None and SUPABASE_SERVICE_ROLE_KEY:
            try:
                self._service_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
                logger.info("Supabase service client initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Supabase service client: {e}")
                raise
        return self._service_client
    
    @retry(
        stop=stop_after_attempt(MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    def execute_query(self, table: str, query_type: str = "select", 
                     columns: str = "*", filters: Optional[Dict] = None,
                     limit: Optional[int] = None, order_by: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a database query with retry logic.
        
        Args:
            table: Table name to query
            query_type: Type of query (select, insert, update, delete)
            columns: Columns to select (for select queries)
            filters: Dictionary of filters to apply
            limit: Maximum number of rows to return
            order_by: Column to order by
            
        Returns:
            Query result as dictionary
        """
        try:
            # Build query
            query = self.client.table(table)
            
            if query_type == "select":
                query = query.select(columns)
                
                # Apply filters
                if filters:
                    for key, value in filters.items():
                        if isinstance(value, list):
                            query = query.in_(key, value)
                        elif isinstance(value, dict) and 'gte' in value:
                            query = query.gte(key, value['gte'])
                        elif isinstance(value, dict) and 'lte' in value:
                            query = query.lte(key, value['lte'])
                        elif isinstance(value, dict) and 'like' in value:
                            query = query.like(key, value['like'])
                        else:
                            query = query.eq(key, value)
                
                # Apply ordering
                if order_by:
                    if order_by.startswith('-'):
                        query = query.order(order_by[1:], desc=True)
                    else:
                        query = query.order(order_by)
                
                # Apply limit
                if limit:
                    query = query.limit(limit)
            
            # Execute query
            result = query.execute()
            
            logger.info(f"Query executed successfully on table {table}")
            return {
                "data": result.data,
                "count": len(result.data) if result.data else 0,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Query execution failed on table {table}: {e}")
            return {
                "data": [],
                "count": 0,
                "error": str(e)
            }
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5)
    )
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the Supabase connection.
        
        Returns:
            Connection test result
        """
        try:
            # Simple query to test connection
            result = self.client.table("leads_pluscargo_simple").select("id").limit(1).execute()
            
            return {
                "status": "success",
                "message": "Connection successful",
                "data_available": len(result.data) > 0
            }
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return {
                "status": "error",
                "message": f"Connection failed: {str(e)}",
                "data_available": False
            }
    
    def get_connection_status(self) -> str:
        """Get current connection status."""
        return self._connection_status
    
    def reset_connection(self):
        """Reset the connection clients."""
        self._client = None
        self._service_client = None
        self._connection_status = "disconnected"
        logger.info("Supabase connections reset")

# Global instance
@st.cache_resource
def get_supabase_client() -> SupabaseClient:
    """Get cached Supabase client instance."""
    return SupabaseClient()

# Convenience functions
def execute_query(table: str, **kwargs) -> Dict[str, Any]:
    """Execute a query using the global client."""
    client = get_supabase_client()
    return client.execute_query(table, **kwargs)

def test_connection() -> Dict[str, Any]:
    """Test connection using the global client."""
    client = get_supabase_client()
    return client.test_connection()

def reset_connection():
    """Reset the global client connection."""
    client = get_supabase_client()
    client.reset_connection()