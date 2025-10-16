# Call Analytics Streamlit App

Una aplicación de análisis de llamadas construida con Streamlit y Supabase.

## Características

- 📊 Análisis completo de llamadas telefónicas
- 📈 Reportes y visualizaciones interactivas
- 🔧 Panel de configuración integrado
- 📱 Interfaz responsive y moderna
- 🔒 Autenticación segura con Supabase

## Despliegue en Streamlit Cloud

### Prerrequisitos

1. Una cuenta en [Streamlit Cloud](https://share.streamlit.io/)
2. Un proyecto en [Supabase](https://supabase.com/)
3. Un repositorio en GitHub con este código

### Pasos para el despliegue

1. **Preparar el repositorio**
   - Asegúrate de que tu código esté en un repositorio de GitHub
   - El archivo principal debe ser `app.py`

2. **Configurar Supabase**
   - Ve a tu proyecto en Supabase Dashboard
   - Navega a Settings > API
   - Copia la URL del proyecto y las API keys (anon key y service role key)

3. **Desplegar en Streamlit Cloud**
   - Ve a [share.streamlit.io](https://share.streamlit.io/)
   - Haz clic en "New app"
   - Conecta tu repositorio de GitHub
   - Selecciona la rama principal (main/master)
   - Especifica `app.py` como el archivo principal

4. **Configurar Secrets**
   - En la configuración de tu app en Streamlit Cloud, ve a "Advanced settings"
   - En la sección "Secrets", pega el siguiente contenido:

   ```toml
   [supabase]
   url = "https://tu-proyecto.supabase.co"
   anon_key = "tu_anon_key_aqui"
   service_role_key = "tu_service_role_key_aqui"
   ```

   - Reemplaza los valores con tus credenciales reales de Supabase

5. **Finalizar despliegue**
   - Haz clic en "Deploy!"
   - Espera a que la aplicación se construya y despliegue
   - Tu app estará disponible en una URL como `https://tu-app.streamlit.app`

### Estructura del proyecto

```
call-analytics-streamlit/
├── app.py                 # Archivo principal de la aplicación
├── pages/                 # Páginas de la aplicación
│   ├── _analisis.py      # Página de análisis
│   ├── _llamadas.py      # Gestión de llamadas
│   ├── configuracion.py  # Configuración
│   ├── gestion_completa.py # Gestión completa
│   └── reportes.py       # Reportes
├── .streamlit/           # Configuración de Streamlit
│   └── secrets.toml.example # Ejemplo de secrets
├── requirements.txt      # Dependencias de Python
└── README.md            # Este archivo
```

### Configuración local

Para ejecutar la aplicación localmente:

1. Clona el repositorio
2. Instala las dependencias: `pip install -r requirements.txt`
3. Copia `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml`
4. Completa tus credenciales de Supabase en `secrets.toml`
5. Ejecuta: `streamlit run app.py`

### Solución de problemas

- **Error de conexión a Supabase**: Verifica que las credenciales en secrets sean correctas
- **Módulos no encontrados**: Asegúrate de que `requirements.txt` incluya todas las dependencias
- **Error de permisos**: Verifica que las API keys de Supabase tengan los permisos necesarios

### Soporte

Si encuentras problemas, verifica:
1. Los logs de la aplicación en Streamlit Cloud
2. La configuración de secrets
3. La conectividad con Supabase
4. Los permisos de las tablas en tu base de datos