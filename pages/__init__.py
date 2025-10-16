"""
Módulo de páginas para la aplicación Call Analytics.
Proporciona funciones para cargar y gestionar las diferentes páginas de la aplicación.
"""

from . import dashboard_analisis, gestion_completa, reportes, configuracion
from utils.i18n_helpers import t

# Configuración de páginas disponibles
PAGES_CONFIG = {
    "Dashboard_Analisis": {
        "module": dashboard_analisis,
        "icon": "📊",
        "description": t("dashboard_unified_description", "common")
    },
    "Gestion_Completa": {
        "module": gestion_completa,
        "icon": "👥",
        "description": t("complete_management_description", "common")
    },
    "Reportes": {
        "module": reportes,
        "icon": "📋",
        "description": t("reports_generation_description", "common")
    },
    "Configuración": {
        "module": configuracion,
        "icon": "⚙️",
        "description": t("application_configuration_description", "common")
    }
}

def get_page_config():
    """
    Retorna la configuración de páginas disponibles.
    
    Returns:
        dict: Diccionario con la configuración de páginas
    """
    return PAGES_CONFIG

def get_page_module(page_name):
    """
    Obtiene el módulo de una página específica.
    
    Args:
        page_name (str): Nombre de la página
        
    Returns:
        module: Módulo de la página o None si no existe
    """
    page_info = PAGES_CONFIG.get(page_name)
    return page_info["module"] if page_info else None

def get_page_list():
    """
    Obtiene la lista de nombres de páginas disponibles.
    
    Returns:
        list: Lista de nombres de páginas
    """
    return list(PAGES_CONFIG.keys())

def get_page_info(page_name):
    """
    Obtiene la información completa de una página.
    
    Args:
        page_name (str): Nombre de la página
        
    Returns:
        dict: Información de la página o None si no existe
    """
    return PAGES_CONFIG.get(page_name)