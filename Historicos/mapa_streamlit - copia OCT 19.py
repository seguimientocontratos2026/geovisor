import streamlit as st
import geopandas as gpd #validar si se puede solo con folium

import folium
from folium.plugins import HeatMap, MarkerCluster, Fullscreen
from streamlit_folium import st_folium #para que streamliet pueda mostar lo hecho con folium

from PIL import Image
import pandas as pd

#import numpy as np
import plotly.express as px


from st_aggrid import AgGrid, GridOptionsBuilder

# -----------------------------
# PARAMETROS
# -----------------------------
caracteres_mostrar = 50  # Número de caracteres a mostrar en el tooltip para 'OBJETO' y 'OBSERVACIONES'
url_datos_csv = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vSfilaqDNJez3zoMqcok02nDBjZhfEwDA5PXBWfx5fOj-QJSk1C4Wb1aoQ4q0gPgQEPzgfq5tUpgsif/pub?gid=228759331&single=true&output=csv'
#Codificacion del archivo CSV. Si hay problemas con acentos, probar 'latin-1'
encoding='utf-8' 

# Listado de variables a convertir de string con formato moneda a float
variables_convertir_pesos_a_float = ['VALOR INICIAL','VALOR FINAL','VALOR TOTAL ADICIONES $', 'TotalCobrado($)', 'PLAZO o DURACION (en meses)']

variables_convertir_entero = ['VIGENCIA']

# Valor por defecto para los NaN o nulos en las columnas que no son numéricas
valor_defecto_para_nulos = "Nulo"

# Si el CSV tiene filas duplicadas y se quieren eliminar, poner este booleano en True
eliminar_duplicados  =True

# Tamao de fuente en el tooltip del mapa
tamano_fuente_tooltip = 10 

#asignar coordenadas por defecto a los contratos sin coordenadas
asignar_coordenadas_a_contratos_sin_coordenadas = True

# Coordenadas iniciales del mapa PEAJE PESCADERO para aquellos que NO tienen coordenadas
latitud_default= 6.803415882902774
longitud_default = -73.00977362782183

# coordenadas para centrar el mapa, zoom inicial
coodenadas_centrar_mapa=[6.95, -73.0]
zoom_inicial_mapa=10

# Paleta de colores para los estados
paleta_colores = {
        'En ejecución': '#FFD700',  # Amarillo
        'Terminado-sin liquidar': '#FF0000',  # Rojo
        'Terminado-Liquidado': '#008000',  # Verde
        'Cerrado': '#008000',  # Verde
        'Desierto': '#800080',  # Morado
        'Firmado': '#0000FF',  # Azul
        'Sin Contrato': '#000000',  # Negro
        'Suspendido': '#808080'  # Gris
    }

# -----------------------------
# Funciones
# -----------------------------

def generar_html_tooltip(row, caracteres_mostrar=caracteres_mostrar, tamano_fuente_tooltip=tamano_fuente_tooltip):
        return f"""
                    <div style="font-size:{tamano_fuente_tooltip}px;">
                        <b>{row['SUPERVISOR DE APOYO']} </b> </br>
                        <b>Proceso</b>: {row['NUMERO DE PROCESO']}</br>
                        <b>Tipo</b>: {row['TIPO DE CONTRATO']}</br>
                        <b>Estado</b>: {estado_a_boton_html(row['ESTADO'])}</br>
                        <b>Plazo</b>: {int(row['PLAZO o DURACION (en meses)'])} meses</br>
                        <b>Inicio</b>: {row['FECHA ACTA DE INICIO']} <b>Fin</b>: {row['FECHA PROGRAMADA TERMINACION actualizada']} </br>      
                        <b>Valor inicial</b>: ${row['VALOR INICIAL']:,.2f} </br>
                        <b>Adiciones</b>: ${row['VALOR TOTAL ADICIONES $']:,.2f}  </br>
                        <b>Valor final</b>: ${row['VALOR FINAL']:,.2f} </br>
                        <b>Total cobrado</b>: ${row['TotalCobrado($)']:,.2f} </br>
                        <b>Objeto</b>: {row['OBJETO'][:caracteres_mostrar]}...</br>
                        <b>Observaciones</b>: {row['OBSERVACIONES'][:caracteres_mostrar]}...</br>
                    </div>
                        """



def estado_a_boton_html(estado: str, tamano_fuente_tooltip= tamano_fuente_tooltip, colores=paleta_colores) -> str:
    colores = paleta_colores #mvb no se requiere entonces el parametro?

    color = colores.get(estado, '#CCCCCC')  # Color por defecto si no se encuentra
    html = f'''
    <button style="
        background-color: {color};
        color: white;
        border: none;
        padding: 0px 0px;
        border-radius: 0px;
        font-size: {tamano_fuente_tooltip}px;
        cursor: default;
    ">
        {estado}
    </button>
    '''
    return html
def generar_estadisticas_basicas(selected_df):
    # Calcular métricas
    cantidad_contratos = len(selected_df)
    valor_inicial_suma = selected_df['VALOR INICIAL'].sum()
    valor_inicial_prom = selected_df['VALOR INICIAL'].mean()
    valor_adiciones_suma = selected_df['VALOR TOTAL ADICIONES $'].sum()
    valor_adiciones_prom = selected_df['VALOR TOTAL ADICIONES $'].mean()
    valor_total_suma = selected_df['TotalCobrado($)'].sum()
    valor_total_prom = selected_df['TotalCobrado($)'].mean()

    
    # Mostrar resumen formateado
    st.markdown(f"""
    #### 📋 Resumen de Contratos Seleccionados

    - **Cantidad de contratos:** {cantidad_contratos}
    - **Valor Inicial (Suma):** ${valor_inicial_suma:,.2f}
    - **Valor Inicial (Promedio):** ${valor_inicial_prom:,.2f}
    - **Valor Adiciones (Suma):** ${valor_adiciones_suma:,.2f}
    - **Valor Adiciones (Promedio):** ${valor_adiciones_prom:,.2f}
    - **Valor Total (Suma):** ${valor_total_suma:,.2f}
    - **Valor Total (Promedio):** ${valor_total_prom:,.2f}
    """)

def clean_money(value):
    try:
        return float(value.replace("$", "").replace(".", "").replace(",", "."))
    except:
        return 0.0
    
@st.cache_data # Streamlit, ejecuta la función una vez con los argumentos dados y guarda el resultado en la caché. La próxima vez que se llame la función con los mismos argumentos, no se ejecuta de nuevo: se devuelve el resultado guardado. Si los argumentos cambian, o el código de la función cambia, se ejecuta de nuevo y se actualiza la caché.
def cargar_datos(url_datos_csv=url_datos_csv, eliminar_duplicados=eliminar_duplicados):
    # Cargar el archivo CSV con datos de contratos
    df = pd.read_csv(url_datos_csv, encoding=encoding)
    if eliminar_duplicados:
        df = df.drop_duplicates()
    return df

def generar_poligono_piedecuesta():
    #Generar el poligono del contorno del municipio de Piedecuesta, para agregar a un mapa

    # Cargar el archivo GeoJSON con todos los municipios de Colombia
    gdf = gpd.read_file("gadm41_COL_2.json")

    # Verifica cómo se llama la columna del municipio (puede ser NAME_2 o similar)
    print(gdf.columns)  # Solo la primera vez para revisar

    # Filtra el municipio de Piedecuesta
    piedecuesta = gdf[gdf['NAME_2'].str.lower() == 'piedecuesta']

    # Verifica que lo haya encontrado
    if piedecuesta.empty:
        print("No se encontró el municipio de Piedecuesta.")
        exit()

    # Obtener el centro del municipio para centrar el mapa
    centro = piedecuesta.geometry.centroid.iloc[0]
    lat, lon = centro.y, centro.x

    # Crear el mapa centrado en Piedecuesta
    mapa = folium.Map(location=[lat, lon], zoom_start=11)

    # Añadir el polígono del municipio al mapa
    # folium.GeoJson(piedecuesta, name="Piedecuesta").add_to(mapa)
    return folium.GeoJson(piedecuesta, name="Piedecuesta")

    # Guardar el mapa como archivo HTML
    #mapa.save("mapa_piedecuesta.html")
    #print("Mapa guardado como 'mapa_piedecuesta.html'")



# -----------------------------
# Cargar datos y limpiar
# -----------------------------
# Cargar datos. Se ejecuta solo una vez y se cachea. Solo se "re-ejecuta" cuando se refresca completamente la pagina.
df = cargar_datos()

# Limpiar la columna de valores como 'TotalCobrado($)' y convertir a float
for var in variables_convertir_pesos_a_float:
    df[var] = df[var].fillna("$0,00")
    df[var] = df[var].apply(clean_money)
    df[var] = df[var].astype(float) #mvb esto estaría repetido porque lo hace en clean_money?

#Asignar coordenadas decimales standar a los contratos sin coordenadas
df.Latitud_decimal = df.Latitud_decimal.fillna("0,000")
df.Longitud_decimal = df.Longitud_decimal.fillna("0,000")
#df.Latitud_decimal = df.Latitud_decimal.astype(str).str.replace("0,000", "6.9010")
#df.Longitud_decimal = df.Longitud_decimal.astype(str).str.replace("0,000", "-72.9010")
#Convertir a float los string de las coordenadas
df['Latitud_decimal'] = df['Latitud_decimal'].astype(str).str.replace(',', '.').astype(float)
df['Longitud_decimal'] = df['Longitud_decimal'].astype(str).str.replace(',', '.').astype(float)

#Convertir los NaN DE OTRAS COLUMNAS o nulos a string
df = df.fillna(valor_defecto_para_nulos)

#asignar coordenadas por defecto a los contratos sin coordenadas
if asignar_coordenadas_a_contratos_sin_coordenadas:
    df['Latitud_decimal'] = df['Latitud_decimal'].replace(0.0, latitud_default)
    df['Longitud_decimal'] = df['Longitud_decimal'].replace(0.0, longitud_default)

# Convertir a entero las columnas que deben ser enteros
for var in variables_convertir_entero:
    df[var] = pd.to_numeric(df[var], errors='coerce').fillna(0).astype(int)


# -----------------------------
# Configuracion de la página 
# -----------------------------
st.set_page_config(
    page_title="Geovisor Contratos - Secretaría Infraestructura. Mayerling Vila",
    page_icon="📊",  
    layout="wide"
)


# -----------------------------
# Logo y Título en el sidebar
# -----------------------------
with st.sidebar:
    # LOGO
    # Crear tres columnas: la primera y la tercera para el espacio vacío,  para centrar, la segunda para la imagen
    col1, col2, col3 = st.columns([2, 4, 2])
    # Cargar la imagen
    image = Image.open("logo.png")
    # Colocar la imagen en la columna del medio
    with col2:
        st.image(image, width=80)
        #st.image(image, use_column_width=True) ... YA NO SE USA
    # (Opcional) Usar las otras columnas para otros elementos
    with col1:
        pass
    with col3:
        pass
    # Inyectamos directamente HTML para tener todo el control. 
    st.markdown(
        """
            <div style="text-align: center;">
                <h2 style="color: #2E86C1; margin-bottom: 0;">Alcaldía de Piedecuesta</h2>
                <h5 style="color: gray; margin-top: 0;">Secretaría Infraestructura</h5>
            </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("---")

# -----------------------------
# Definición de Tabs con Botones
# -----------------------------    
tab_names = ["🗺️ Mapa Calor", "🗺️ Mapa Sitio", "📊 Datos", "🏗️ Dashboard", "ℹ️ Acerca de"]
#Activamos la tab por defecto: 0 es Mapa Calor
if "active_tab" not in st.session_state:
    st.session_state.active_tab = tab_names[0]

tab_cols = st.columns(len(tab_names)) #Divide el espacio horizontal en tantas columnas como pestañas haya.
for i, name in enumerate(tab_names):
    if tab_cols[i].button(name):
        st.session_state.active_tab = name #mvb: no me queda claro si esto maneja el cambio entre tabs... y entonces cada vez que cambia crea los botones?

tab = st.session_state.active_tab

# -----------------------------
# Comportamiento dinámico del sidebar según la tab seleccionada
# -----------------------------
with st.sidebar:
    if tab == "🗺️ Mapa Calor" or tab == "🗺️ Mapa Sitio":
        
        # Filtro por ESTADO, VIGENCIA, TIPO DE CONTRATO, SUPERVISOR DE APOYO 

        # Crear lista de opciones con "Todos" al inicio
        estado = st.selectbox(
            "Selecciona el estado:",
            options= ['Todos'] + sorted(df['ESTADO'].unique().tolist()),
            index=0  # Esto selecciona el primer valor como predeterminado
        )

        vigencia = st.selectbox(
            "Selecciona la vigencia:",
            options= ['Todas'] + sorted(df['VIGENCIA'].unique().tolist(), reverse=True),
            index=0  # Esto selecciona el primer valor como predeterminado
        )

        tipo_contrato = st.selectbox(
            "Selecciona el tipo de contrato:",
            options= ['Todos'] + sorted(df['TIPO DE CONTRATO'].unique().tolist()),
            index=0  # Esto selecciona el primer valor como predeterminado
        )

        supervisor = st.selectbox(
            "Selecciona el supervisor:",
            options= ['Todos'] + sorted(df['SUPERVISOR DE APOYO'].unique().tolist()),
            index=0  # Esto selecciona el primer valor como predeterminado
        )



    elif tab == "📊 Datos":
        # Filtro por COLUMNAS 
        columnas = st.sidebar.multiselect(
        "Columnas a mostrar:",
        options=df.columns.tolist(),
        default=df.columns.tolist()
        )        

    elif tab == "🏗️ Dashboard":
        st.subheader("Opciones de Reportes")
        report_type = st.radio("Tipo de reporte", ["PDF", "Excel"])

    elif tab == "ℹ️ Acerca de":
        st.subheader("Información")
        st.markdown("""
<div style="font-size:13px; color: #2E86C1; line-height: 1.5;">
    <strong>Aplicación desarrollada por:</strong><br>
    Ing. Mayerling Vila &copy; 2025–2026<br>
    Todos los derechos reservados.<br>
    <a href="mailto:mayevila@hotmail.com">Envíanos un correo</a>
</div>
""", unsafe_allow_html=True)



# -----------------------------
# Comportamiento dinámico del cuerpo principal según la tab seleccionada
# -----------------------------
if tab == "🗺️ xxMapa Calor":
    #if true: pass
    #else:
    # Filtrar datos según selección - Datos completos df se pasan a df_filtrado
    df_filtrado = df.copy()
    if 'estado' in globals():
        if estado != 'Todos':
            df_filtrado = df_filtrado[(df_filtrado['ESTADO']==estado)]        
    
    if 'vigencia' in globals():
        if vigencia != 'Todas':
            df_filtrado = df_filtrado[(df_filtrado['VIGENCIA']==vigencia)]
    
    if 'tipo_contrato' in globals():
        if tipo_contrato != 'Todos':
            df_filtrado = df_filtrado[(df_filtrado['TIPO DE CONTRATO']==tipo_contrato)]
    
    if 'supervisor' in globals():
        if supervisor != 'Todos':
            df_filtrado = df_filtrado[(df_filtrado['SUPERVISOR DE APOYO']==supervisor)]
    
    #print("======== df_filtrado ========", df_filtrado.shape, "==  estado:", estado, "vigencia", vigencia, "tipo_contrato", tipo_contrato, "supervisor", supervisor)

    # Mostrar el mapa en Streamlit
    st.subheader("🗺️ Contratos Georeferenciados [Mapa Calor]")

    # Crear el mapa centrado
    m = folium.Map(location=coodenadas_centrar_mapa, zoom_start=zoom_inicial_mapa)

    # Agregar botón de pantalla completa
    Fullscreen(position='topright').add_to(m)

    # Crear lista de puntos para el heatmap: [latitud, longitud, peso]
    heat_data = [
        [row['Latitud_decimal'], row['Longitud_decimal'], row['TotalCobrado($)']]
        for _, row in df_filtrado.iterrows()
    ]

    # Agregar el heatmap al mapa
    HeatMap(heat_data, radius=15, blur=10, max_zoom=1).add_to(m)

    # Crear un cluster de marcadores con tooltips
    marker_cluster = MarkerCluster().add_to(m)

    
    for _, row in df_filtrado.iterrows():
        tooltip_text = generar_html_tooltip(row)
        folium.Marker(
            location=[row['Latitud_decimal'], row['Longitud_decimal']],
            tooltip=tooltip_text
        ).add_to(marker_cluster)

    st_folium(m, width="100%", height=500)



elif tab == "🗺️ Mapa Sitio":
    # Filtrar datos según selección - Datos completos df se pasan a df_filtrado
    df_filtrado = df.copy()
    if 'estado' in globals():
        if estado != 'Todos':
            df_filtrado = df_filtrado[(df_filtrado['ESTADO']==estado)]        
    
    if 'vigencia' in globals():
        if vigencia != 'Todas':
            df_filtrado = df_filtrado[(df_filtrado['VIGENCIA']==vigencia)]
    
    if 'tipo_contrato' in globals():
        if tipo_contrato != 'Todos':
            df_filtrado = df_filtrado[(df_filtrado['TIPO DE CONTRATO']==tipo_contrato)]
    
    if 'supervisor' in globals():
        if supervisor != 'Todos':
            df_filtrado = df_filtrado[(df_filtrado['SUPERVISOR DE APOYO']==supervisor)]
    
    #print("======== df_filtrado ========", df_filtrado.shape, "==  estado:", estado, "vigencia", vigencia, "tipo_contrato", tipo_contrato, "supervisor", supervisor)

    # Mostrar el mapa en Streamlit
    st.subheader("🗺️ Contratos Georeferenciados [Mapa Sitio]")

    # Crear el mapa centrado
    m = folium.Map(location=coodenadas_centrar_mapa, zoom_start=zoom_inicial_mapa)



    # Añadir el polígono del municipio de Piedecuesta al mapa
    poligono_piedecuesta = generar_poligono_piedecuesta()
    poligono_piedecuesta.add_to(m)



    # Agregar botón de pantalla completa
    Fullscreen(position='topright').add_to(m)

    #color_map para los estados
    color_map = paleta_colores
    

    # Normalizar población para ajustar el tamaño de los círculos
    min_radius = 10
    max_radius = 120

    # Evitar división por cero
    max_total_cobrado = max(df_filtrado['TotalCobrado($)'].abs().max(), 1)
    #max_total_cobrado = df_filtrado['TotalCobrado($)'].max()

    for _, row in df_filtrado.iterrows():
        color = color_map.get(row['ESTADO'], 'blue')
        # Normalizar el radio entre min_radius y max_radius
        radio = min_radius + (abs(row['TotalCobrado($)']) / max_total_cobrado) * (max_radius - min_radius)
        
        folium.CircleMarker(
            location=[row['Latitud_decimal'], row['Longitud_decimal']],
            radius=radio,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.3,
            tooltip=folium.Tooltip(generar_html_tooltip(row))
        ).add_to(m)

    # Mostrar el mapa en Streamlit
    st_folium(m, width="100%", height=500)



elif tab == "📊 Datos":
    if 'columnas' in globals():
        df_filtrado = df[columnas].copy()
    else:
        df_filtrado = df.copy()

    st.subheader(f"📊 Detalle de los contratos [Datos]")
    
    # Configurar opciones de la tabla
    gb = GridOptionsBuilder.from_dataframe(df[columnas])
    
    # Permitir mostrar/ocultar columnas
    gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)

    # Habilitar filtros por columna
    gb.configure_default_column(filter=True, resizable=True, minWidth=180)

    # Habilitar selección de filas
    gb.configure_selection('multiple', use_checkbox=True)

    # Construir opciones
    grid_options = gb.build()

    # Mostrar tabla interactiva
    grid_response = AgGrid(
        df[columnas],
        gridOptions=grid_options,
        enable_enterprise_modules=True,
        update_mode='MODEL_CHANGED',
        fit_columns_on_grid_load=True,
        height=400,
        theme='alpine',  # Puedes cambiar el tema si quieres
        allow_unsafe_jscode=False  # Necesario para autoSizeAllColumns
    )

    
    # Mostrar filas seleccionadas
    selected = grid_response['selected_rows']
    selected_df = pd.DataFrame(selected)     

    if not selected_df.empty:
        #Resumen
        generar_estadisticas_basicas(selected_df)

elif tab == "🏗️ xxDashboard":

    # Limpiar datos 
    df = df.dropna(subset=['ESTADO'])

    # --- Widgets por estado de contrato ---
    estado_counts = df['ESTADO'].value_counts().reset_index()
    estado_counts.columns = ['Estado', 'Cantidad']

    colors = px.colors.qualitative.Set3

    st.markdown("### 🏗️ Seguimiento de Contratos")


    # Obtener conteo por estado
    estado_counts = df['ESTADO'].value_counts().reset_index()
    estado_counts.columns = ['Estado', 'Cantidad']

    # Mostrar en una sola fila
    cols = st.columns(len(estado_counts))

    for i, (col, row) in enumerate(zip(cols, estado_counts.itertuples())):
        color = paleta_colores.get(row.Estado, '#999999')  # Color por defecto si no está en el diccionario
        col.markdown(f"""
        <div style='background-color:{color}; padding:12px; border-radius:10px; text-align:center; color:white;'>
            <div style='font-size:24px; font-weight:bold;'>{int(row.Cantidad)}</div>
            <div style='font-size:8px;'>{row.Estado}</div>
        </div>
        """, unsafe_allow_html=True)


    st.markdown("---")

    # --- Dashboard con 2 columnas y 6 gráficos ---
    col1, col2 = st.columns(2)
    



    # Gráfico 1: Valor inicial por tipo de contrato
    with col1:
        fig1 = px.bar(df, x='TIPO DE CONTRATO', y='VALOR INICIAL', color='TIPO DE CONTRATO',
                    title='💰 Valor Inicial por Tipo de Contrato')
        st.plotly_chart(fig1)



    # Gráfico 2: Total cobrado por estado
    with col1:
        fig2 = px.pie(df, names='ESTADO', values='TotalCobrado($)', title='📊 Distribución de Total Cobrado por Estado')
        st.plotly_chart(fig2)


    st.markdown("---")


    # Gráfico 3: Valor inicial vs Total cobrado
    with col2:
        fig3 = px.scatter(df, x='VALOR INICIAL', y='TotalCobrado($)', color='ESTADO',
                        title='🔍 Comparación Valor Inicial vs Total Cobrado')
        st.plotly_chart(fig3)

    # Gráfico 4: Contratos por supervisor
    with col2:
        supervisor_counts = df['SUPERVISOR DE APOYO'].value_counts().reset_index()
        supervisor_counts.columns = ['SUPERVISOR DE APOYO', 'Cantidad']
        fig4 = px.bar(supervisor_counts, x='SUPERVISOR DE APOYO', y='Cantidad', color='SUPERVISOR DE APOYO',
                    title='👷‍♀️ Contratos por Supervisor de Apoyo')
        st.plotly_chart(fig4)

    # Gráfico 5: Valor total de adiciones por tipo de contrato
    fig5 = px.bar(df, x='TIPO DE CONTRATO', y='VALOR TOTAL ADICIONES $', color='TIPO DE CONTRATO',
                title='➕ Valor Total de Adiciones por Tipo de Contrato')
    st.plotly_chart(fig5)

    
    st.markdown("---")


elif tab == "ℹ️ Acerca de":
    st.markdown("### Geovisor Contratos - Secretaría de Infraestructura")
    st.write("Esta aplicación permite realizar un seguimiento detallado y georreferenciado de los contratos gestionados por la Secretaría de Infraestructura.")
    st.write("Gracias a su interfaz interactiva, los usuarios pueden visualizar la ubicación de cada contrato en el mapa, acceder a información clave como el estado, tipo, valor, fechas y observaciones, y aplicar filtros dinámicos para facilitar el análisis.")
    st.write(" Una herramienta poderosa para la gestión transparente, eficiente y visual de la inversión pública en infraestructura.")

    st.markdown("""
    <div style="font-size:14px; color: #2E86C1; line-height: 1.5;" align="center">
        <strong>Aplicación desarrollada por:</strong><br>
        Ing. Mayerling Vila &copy; 2025–2026<br>
        Secretaría de Infraestructura - Alcaldía de Piedecuesta<br><br>
    </div>
    """, unsafe_allow_html=True)





# -----------------------------
# Fin
# -----------------------------