import streamlit as st
import pandas as pd
import plotly.express as px
import mysql.connector


st.set_page_config(
    page_title="Aroma Café — Panel de Control",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "db_status" not in st.session_state:
    st.session_state["db_status"] = "Desconectado"
if "db_success" not in st.session_state:
    st.session_state["db_success"] = False

st.markdown("""
    <style>
        .block-container { padding-top: 2rem; padding-bottom: 2rem; }
        .stMetric { background-color: #1e1e24; padding: 1.5rem; border-radius: 0.5rem; border-left: 5px solid #ff4d4d; }
        div[data-testid="stExpander"] { border: none; background-color: #1e1e24; }
        
        /* Estilos UX Profesionales para las Alertas en HTML */
        .custom-alert {
            padding: 1.25rem;
            border-radius: 0.5rem;
            margin-bottom: 1.5rem;
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        .alert-success {
            background-color: rgba(46, 125, 50, 0.15);
            border: 1px solid rgb(46, 125, 50);
            color: #4caf50;
        }
        .alert-error {
            background-color: rgba(211, 47, 47, 0.15);
            border: 1px solid rgb(211, 47, 47);
            color: #f44336;
        }
        .alert-info {
            background-color: rgba(2, 136, 209, 0.15);
            border: 1px solid rgb(2, 136, 209);
            color: #29b6f6;
        }
    </style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=30, show_spinner=False)
def obtener_datos_negocio():
    datos_defecto = {
        "Producto": ["Capuchino", "Café Latte", "Pastel de Chocolate", "Tostadas Gourmet"],
        "Cantidad Mensual": [600, 500, 400, 350],
        "Precio (USD)": [3.75, 3.50, 4.50, 5.00]
    }
    df_respaldo = pd.DataFrame(datos_defecto)
    
    try:
        conexion = mysql.connector.connect(
            host="localhost",
            user="root",        
            password="root1234", 
            database="aroma_cafe"
        )
       
        query = "SELECT nombre_producto AS 'Producto', stock AS 'Cantidad Mensual', precio_producto_unitario AS 'Precio (USD)' FROM producto;"
        df_sql = pd.read_sql(query, conexion)
        conexion.close()
        
        if not df_sql.empty:
            return df_sql, "ok", None
        return df_respaldo, "vacio", None
    except Exception as e:
        return df_respaldo, "error", str(e)


df_base = None
resultado_db = "error"
detalle_error = "Error al conectar con la infraestructura"

# Ejecución segura
df_base, resultado_db, detalle_error = obtener_datos_negocio()


if resultado_db == "ok":
    st.session_state["db_status"] = "Conectado de forma local a MySQL ('aroma_cafe')"
    st.session_state["db_success"] = True
elif resultado_db == "vacio":
    st.session_state["db_status"] = "Conectado "
    st.session_state["db_success"] = True
else:
    st.session_state["db_status"] = "Desconectado"
    st.session_state["db_success"] = False
    st.session_state["db_error"] = detalle_error


st.sidebar.header("🚀 Centro de Simulación")
st.sidebar.markdown("Ajusta los parámetros operativos para auditar el comportamiento financiero en tiempo real.")

slider_demanda = st.sidebar.slider(
    "Variación del Volumen de Ventas (%)", 
    min_value=50, 
    max_value=150, 
    value=100, 
    step=5
)
factor_demanda = slider_demanda / 100.0

df_dinamico = df_base.copy()
df_dinamico["Cantidad Mensual"] = (df_dinamico["Cantidad Mensual"] * factor_demanda).astype(int)
df_dinamico["Total (USD)"] = df_dinamico["Cantidad Mensual"] * df_dinamico["Precio (USD)"]

st.sidebar.markdown("---")
st.sidebar.markdown("### 🖥️ Infraestructura TI")
if st.session_state["db_success"]:
    st.sidebar.success(f"● {st.session_state['db_status']}")
else:
    st.sidebar.error(f"○ {st.session_state['db_status']}")
    if "db_error" in st.session_state and st.session_state["db_error"]:
        with st.sidebar.expander("Detalle del error técnico"):
            st.sidebar.code(st.session_state["db_error"])

st.title("☕ Cafetería Aroma & Café")
st.markdown("##### *Sistema Integrado de Gestión Financiera, Control Interno y TI *")
st.markdown("---")

ingresos_totales = df_dinamico["Total (USD)"].sum()
costos_fijos_cuenta = 3350.00 
costos_variables_cuenta = 3550.00 * factor_demanda  
gastos_totales_calculados = costos_fijos_cuenta + costos_variables_cuenta
utilidad_neta_calculada = ingresos_totales - gastos_totales_calculados
punto_equilibrio_fijo = 6300.00  

m1, m2, m3 = st.columns(3)
with m1:
    st.metric(
        label="Ingresos Totales Proyectados", 
        value=f"${ingresos_totales:,.2f}",
        delta=f"{slider_demanda - 100:+.0f}% de rendimiento" if slider_demanda != 100 else None
    )
with m2:
    st.metric(
        label="Costos Operativos Totales (Fijos + Variables)", 
        value=f"${gastos_totales_calculados:,.2f}"
    )
with m3:
    status_rentable = "Zona de Ganancia" if ingresos_totales >= punto_equilibrio_fijo else "Margen Deficitario"
    st.metric(
        label="Utilidad Neta Estimada", 
        value=f"${utilidad_neta_calculada:,.2f}",
        delta=status_rentable,
        delta_color="normal" if ingresos_totales >= punto_equilibrio_fijo else "inverse"
    )

st.markdown("---")

st.subheader("Análisis de Estructura de Ingresos y Ventas")
c1, c2 = st.columns(2)

with c1:
    fig_bar = px.bar(
        df_dinamico, 
        x="Producto", 
        y="Total (USD)", 
        title="Ingresos Mensuales Estimados por Categoría de Producto",
        color="Producto",
        text_auto='.2f',
        template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.Reds_r
    )
    fig_bar.update_layout(showlegend=False, margin=dict(t=40, b=20, l=20, r=20))
    st.plotly_chart(fig_bar, use_container_width=True)

with c2:
    fig_pie = px.pie(
        df_dinamico, 
        values="Cantidad Mensual", 
        names="Producto", 
        title="Distribución de Volumen de Ventas (Unidades Vendidas)",
        hole=0.4,
        template="plotly_dark",
        color_discrete_sequence=px.colors.sequential.Reds
    )
    fig_pie.update_layout(margin=dict(t=40, b=20, l=20, r=20))
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

st.subheader("Informes de Control Interno y Gestión de Riesgos Financieros")
col_alertas, col_tabla = st.columns([1.2, 1])

with col_alertas:
    if ingresos_totales < punto_equilibrio_fijo:
        st.html(f"""
            <div class="custom-alert alert-error">
                <strong>⚠️ Alerta Crítica de Riesgo</strong><br><br>
                Las ventas proyectadas actuales de <strong>${ingresos_totales:,.2f}</strong> se encuentran por debajo del punto de equilibrio operativo establecido de <strong>$6,300.00</strong>. Se recomienda revisar la estrategia de precios o reducir costos variables.
            </div>
        """)
    else:
        st.html(f"""
            <div class="custom-alert alert-success">
                <strong>✅ Umbral de Estabilidad Alcanzado</strong><br><br>
                El nivel operativo actual de <strong>${ingresos_totales:,.2f}</strong> supera con éxito el punto de equilibrio mínimo de <strong>$6,300.00</strong>, validando la viabilidad económica del negocio.
            </div>
        """)
        
    st.markdown("#### 📝 Diagnóstico Contable Integrado ")
    
    st.html(f"""
        <div class="custom-alert alert-info">
            <strong>Solución a la Debilidad de Depreciación:</strong><br><br>
            Se ha notificado la necesidad de incluir una tabla de amortización para la inversión inicial en activos fijos de <strong>$14,400.00</strong> a fin de no sobreestimar las utilidades reales netas en futuros periodos.
        </div>
    """)

with col_tabla:
    st.markdown("#### Resumen del Inventario de Menú Objetivo")
    st.dataframe(df_dinamico[["Producto", "Cantidad Mensual", "Precio (USD)"]], use_container_width=True)
    st.caption("Los datos reflejados cambian dinámicamente según las variaciones del Centro de Simulación lateral.")