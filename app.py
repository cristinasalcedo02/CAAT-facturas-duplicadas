import pandas as pd
import streamlit as st

# Título e introducción
st.set_page_config(page_title="CAAT - Detección de Facturas Duplicadas", layout="wide")
st.title("🔍 CAAT - Detección de Facturas Duplicadas")
st.write("Versión automática con datos internos precargados para pruebas de auditoría.")

# Cargar datos desde archivos locales
try:
    compras = pd.read_csv("facturas_compras.csv")
    contabilidad = pd.read_csv("facturas_contabilidad.csv")
except FileNotFoundError:
    st.error("❌ No se encontraron los archivos CSV requeridos. Verifica que estén en el mismo repositorio.")
    st.stop()

# --- FUNCIONALIDAD 1: Detección por número de factura ---
compras["duplicado_numero"] = compras.duplicated(subset="numero_factura", keep=False)

# --- FUNCIONALIDAD 2: Duplicados por combinación fecha + proveedor + monto ---
compras["duplicado_fecha_prov_monto"] = compras.duplicated(subset=["fecha_emision", "proveedor_id", "monto_total"], keep=False)

# --- FUNCIONALIDAD 3: Duplicados por múltiples campos clave ---
compras["duplicado_campos_clave"] = compras.duplicated(
    subset=["numero_factura", "fecha_emision", "proveedor_id", "monto_total", "detalle_productos"], keep=False
)

# --- FUNCIONALIDAD 4: Comparación entre compras y contabilidad ---
duplicados_entre_archivos = pd.merge(compras, contabilidad, how="inner", on="numero_factura")

# --- FUNCIONALIDAD 5: Verificar facturas anuladas ---
compras["valida_estado"] = compras["estado_factura"].str.lower().fillna("") != "anulada"

# --- Mostrar resumen de hallazgos ---
st.subheader("📊 Resumen de hallazgos:")

resumen = {
    "Duplicados por número de factura": compras["duplicado_numero"].sum(),
    "Duplicados por fecha-proveedor-monto": compras["duplicado_fecha_prov_monto"].sum(),
    "Duplicados por campos clave": compras["duplicado_campos_clave"].sum(),
    "Duplicados entre compras y contabilidad": len(duplicados_entre_archivos),
    "Facturas válidas (no anuladas)": compras["valida_estado"].sum()
}

for clave, valor in resumen.items():
    st.write(f"- **{clave}**: {valor} registros")

# --- Mostrar registros sospechosos ---
st.subheader("🔎 Facturas sospechosas detectadas:")
sospechosas = compras[
    compras["duplicado_numero"] | 
    compras["duplicado_fecha_prov_monto"] | 
    compras["duplicado_campos_clave"]
]

st.dataframe(sospechosas, use_container_width=True)

# --- Gráfico opcional ---
import matplotlib.pyplot as plt

st.subheader("📈 Gráfico de distribución de hallazgos")
fig, ax = plt.subplots()
ax.bar(resumen.keys(), resumen.values(), color='skyblue')
plt.xticks(rotation=45, ha='right')
st.pyplot(fig)

# --- Mensaje final ---
st.success("✅ Análisis completo. Si deseas actualizar los datos, sube nuevos archivos al repositorio.")
