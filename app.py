from datetime import datetime
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# ----------------------------
# CONFIGURACIÓN DE LA APP
# ----------------------------
st.set_page_config(page_title="CAAT - Detección de Facturas Duplicadas", layout="wide")
st.title("🔎 CAAT - Detección de Facturas Duplicadas")
st.markdown("Versión automática con datos internos precargados para pruebas de auditoría.")

# ----------------------------
# CARGA DE DATOS
# ----------------------------
compras = pd.read_csv("facturas_compras.csv")
contabilidad = pd.read_csv("facturas_contabilidad.csv")

# ----------------------------
# PREPROCESAMIENTO
# ----------------------------
compras["estado_factura"] = compras["estado_factura"].str.lower().str.strip()
compras["valida_estado"] = compras["estado_factura"] != "anulada"

# Reglas de duplicación
compras["duplicado_numero"] = compras.duplicated(subset=["numero_factura"], keep=False)
compras["duplicado_fecha_prov_monto"] = compras.duplicated(subset=["fecha_emision", "proveedor_id", "monto_total"], keep=False)
compras["duplicado_campos_clave"] = compras.duplicated(subset=["numero_factura", "monto_total", "proveedor_id"], keep=False)

# Duplicados entre compras y contabilidad
duplicados_entre_archivos = pd.merge(
    compras, contabilidad, on="clave_unica_interna", how="inner"
)

# ----------------------------
# RESUMEN DE HALLAZGOS
# ----------------------------
resumen = {
    "Duplicados por número de factura": compras["duplicado_numero"].sum(),
    "Duplicados por fecha-proveedor-monto": compras["duplicado_fecha_prov_monto"].sum(),
    "Duplicados por campos clave": compras["duplicado_campos_clave"].sum(),
    "Duplicados entre compras y contabilidad": len(duplicados_entre_archivos),
    "Facturas válidas (no anuladas)": compras["valida_estado"].sum()
}

# ----------------------------
# VISUALIZACIÓN EN STREAMLIT
# ----------------------------
st.markdown("### 📊 Resumen de hallazgos:")
for k, v in resumen.items():
    st.markdown(f"- **{k}**: {v} registros")

# Mostrar detalles de facturas sospechosas
sospechosas = compras[
    compras["duplicado_numero"] | compras["duplicado_fecha_prov_monto"] | compras["duplicado_campos_clave"]
]

st.markdown("### 🔎 Facturas sospechosas detectadas:")
st.dataframe(sospechosas.drop(columns=[
    "duplicado_numero", "duplicado_fecha_prov_monto", "duplicado_campos_clave", "valida_estado"
]))

# ----------------------------
# GRÁFICO DE BARRAS
# ----------------------------
st.markdown("### 📈 Gráfico de distribución de hallazgos")
fig, ax = plt.subplots()
ax.bar(resumen.keys(), resumen.values(), color="skyblue")
ax.set_ylabel("Cantidad de registros")
ax.set_xticklabels(resumen.keys(), rotation=45, ha='right')
st.pyplot(fig)

# ----------------------------
# LOG DE EJECUCIÓN
# ----------------------------
usuario = "auditor_streamlit"
hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
registro_log = {
    "usuario": usuario,
    "fecha_ejecucion": hora,
    **resumen
}

try:
    log = pd.read_csv("log_ejecuciones.csv")
    log = pd.concat([log, pd.DataFrame([registro_log])], ignore_index=True)
except FileNotFoundError:
    log = pd.DataFrame([registro_log])

log.to_csv("log_ejecuciones.csv", index=False)

# Mostrar log de esta ejecución
st.markdown("### 🗒️ Log de esta ejecución:")
for clave, valor in registro_log.items():
    st.write(f"- **{clave}**: {valor}")

# Mostrar historial de últimas ejecuciones
st.markdown("### 📁 Historial de ejecuciones anteriores:")
st.dataframe(log.tail(10))
