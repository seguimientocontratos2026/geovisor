# Geovisor Contratos - Secretaría de Infraestructura

Aplicación desarrollada por:  
**Ing. Mayerling Vila © 2025–2026**  
Secretaría de Infraestructura - Alcaldía de Piedecuesta

---

## Descripción

Esta aplicación permite realizar un seguimiento detallado y georreferenciado de los contratos gestionados por la Secretaría de Infraestructura. Gracias a su interfaz interactiva, los usuarios pueden visualizar la ubicación de cada contrato en el mapa, acceder a información clave como el estado, tipo, valor, fechas y observaciones, y aplicar filtros dinámicos para facilitar el análisis.

Una herramienta poderosa para la gestión transparente, eficiente y visual de la inversión pública en infraestructura.

---

## Fuente de Datos

La aplicación importa los datos automáticamente desde una hoja de cálculo alojada en Google Sheets, en formato CSV.  
**Dirección del archivo CSV:**  
https://docs.google.com/spreadsheets/d/e/2PACX-1vSfilaqDNJez3zoMqcok02nDBjZhfEwDA5PXBWfx5fOj-QJSk1C4Wb1aoQ4q0gPgQEPzgfq5tUpgsif/pub?gid=228759331&single=true&output=csv

Esto permite que los datos estén siempre actualizados y centralizados.

---

## Instalación

1. **Clona el repositorio o descarga los archivos.**
2. **Crea un entorno virtual (opcional pero recomendado):**
   ```bash
   python -m venv env
   source env/bin/activate  # En Linux/Mac
   .\env\Scriptsctivate   # En Windows
   ```
3. **Instala las dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Ejecuta la aplicación:**
   ```bash
   streamlit run mapa_streamlit.py
   ```

---

## Parámetros Personalizables

La aplicación cuenta con varios parámetros que pueden ser modificados directamente en el código para adaptar el comportamiento y la visualización:

- `caracteres_mostrar`: Número de caracteres a mostrar en los tooltips para los campos 'OBJETO' y 'OBSERVACIONES'.
- `url_datos_csv`: URL del archivo CSV en Google Sheets. Puedes cambiarla para usar otra fuente de datos.
- `encoding`: Codificación del archivo CSV. Por defecto es 'utf-8', pero puedes probar 'latin-1' si tienes problemas con acentos.
- `variables_convertir_pesos_a_float`: Lista de columnas que se convierten de formato moneda a float.
- `variables_convertir_entero`: Lista de columnas que se convierten a enteros.
- `valor_defecto_para_nulos`: Valor por defecto para los NaN o nulos en las columnas no numéricas.
- `eliminar_duplicados`: Si es `True`, elimina filas duplicadas del CSV.
- `tamano_fuente_tooltip`: Tamaño de fuente en los tooltips del mapa.
- `asignar_coordenadas_a_contratos_sin_coordenadas`: Si es `True`, asigna coordenadas por defecto a los contratos sin coordenadas.
- `latitud_default` / `longitud_default`: Coordenadas por defecto para contratos sin ubicación.
- `coodenadas_centrar_mapa` / `zoom_inicial_mapa`: Coordenadas y nivel de zoom inicial del mapa.
- `paleta_colores`: Diccionario que asigna colores a los diferentes estados de los contratos.

**Ejemplo de personalización:**
```python
caracteres_mostrar = 100
zoom_inicial_mapa = 12
paleta_colores = {
    'En ejecución': '#FFD700',
    'Terminado-sin liquidar': '#FF0000',
    # ... otros estados
}
```

---

## Estructura de la Aplicación

La interfaz principal está dividida en cinco pestañas (tabs):

### 1. 🗺️ Mapa Calor
- Visualiza los contratos georreferenciados como un mapa de calor.
- Permite filtrar por estado, vigencia, tipo de contrato y supervisor de apoyo.
- Cada punto muestra información relevante en un tooltip.

### 2. 🗺️ Mapa Sitio
- Muestra los contratos como círculos en el mapa, donde el tamaño representa el valor total cobrado y el color el estado del contrato.
- Permite los mismos filtros que el mapa de calor.
- Tooltips detallados para cada contrato.

### 3. 📊 Datos
- Tabla interactiva con todos los datos de los contratos.
- Permite seleccionar columnas a mostrar y filtrar filas.
- Al seleccionar filas, muestra estadísticas básicas (cantidad, sumas y promedios de valores).

### 4. 🏗️ Dashboard
- Panel de visualización con gráficos interactivos:
  - Valor inicial por tipo de contrato.
  - Distribución de total cobrado por estado.
  - Comparación valor inicial vs total cobrado.
  - Contratos por supervisor de apoyo.
  - Valor total de adiciones por tipo de contrato.
- Muestra conteos por estado y permite exportar reportes en PDF o Excel.

### 5. ℹ️ Acerca de
- Generalidades de la aplicación.
- Créditos de la creadora: **Ing. Mayerling Vila**.
- Información de contacto: mayevila@hotmail.com.

---

## Créditos

Aplicación desarrollada por:  
**Ing. Mayerling Vila © 2025–2026**  
Secretaría de Infraestructura - Alcaldía de Piedecuesta

---

## Contacto

¿Dudas, sugerencias o comentarios?  
mayevila@hotmail.com

---

## Licencia

Todos los derechos reservados.
