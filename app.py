
import streamlit as st
import pandas as pd

st.set_page_config(page_title="CAAT - Facturas Duplicadas", layout="wide")

st.title("🔍 CAAT - Detección de Facturas Duplicadas")
st.markdown("Versión automática con datos internos precargados para pruebas de auditoría.")

@st.cache_data
def cargar_datos():
    compras = pd.read_csv("https://raw.githubusercontent.com/cristinasalcedo02/CAAT-facturas-duplicadas/main/facturas_compras.csv")
    contabilidad = pd.read_csv("https://raw.githubusercontent.com/cristinasalcedo02/CAAT-facturas-duplicadas/main/facturas_contabilidad.csv")
    return compras, contabilidad

compras, contabilidad = cargar_datos()

# Pruebas CAAT
compras["duplicado_numero"] = compras.duplicated(subset=["numero_factura"])
compras["duplicado_fecha_prov_monto"] = compras.duplicated(subset=["fecha_emision", "proveedor_id", "monto_total"])
compras["duplicado_campos_clave"] = compras.duplicated(subset=["proveedor_id", "monto_total", "detalle_productos"])
compras["valida_estado"] = compras["estado_factura"].str.lower() != "anulada"
duplicados_entre = pd.merge(compras, contabilidad, on="numero_factura", how="inner")

# Resultados sospechosos
resultados = compras[
    compras["duplicado_numero"] |
    compras["duplicado_fecha_prov_monto"] |
    compras["duplicado_campos_clave"]
]

st.subheader("📋 Facturas sospechosas detectadas")
st.dataframe(resultados)

# Resumen
resumen = {
    "Duplicados por número de factura": compras['duplicado_numero'].sum(),
    "Duplicados por fecha-proveedor-monto": compras['duplicado_fecha_prov_monto'].sum(),
    "Duplicados por campos clave": compras['duplicado_campos_clave'].sum(),
    "Duplicados entre compras y contabilidad": len(duplicados_entre),
    "Facturas válidas (no anuladas)": compras['valida_estado'].sum()
}

st.subheader("📊 Resumen de hallazgos")
for clave, valor in resumen.items():
    st.write(f"- {clave}: {valor} registros")
