from datetime import datetime
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import hashlib

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
# VALIDACIÓN Y LIMPIEZA
# ----------------------------
compras.dropna(subset=["numero_factura", "fecha_emision", "proveedor_id", "monto_total"], inplace=True)
compras["estado_factura"] = compras["estado_factura"].str.lower().str.strip()
compras["valida_estado"] = compras["estado_factura"] != "anulada"

# ----------------------------
# MARCAR DUPLICADOS
# ----------------------------
compras["duplicado_numero"] = compras.duplicated(subset=["numero_factura"], keep=False)
compras["duplicado_fecha_prov_monto"] = compras.duplicated(subset=["fecha_emision", "proveedor_id", "monto_total"], keep=False)
compras["duplicado_campos_clave"] = compras.duplicated(subset=["numero_factura", "monto_total", "proveedor_id"], keep=False)

# Comparación cruzada entre archivos
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
# MOSTRAR RESUMEN
# ----------------------------
st.markdown("### 📊 Resumen de hallazgos:")
for k, v in resumen.items():
    st.markdown(f"- **{k}**: {v} registros")

# ----------------------------
# MOSTRAR DETALLES DE FACTURAS SOSPECHOSAS
# ----------------------------
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
# REGISTRO DE LOGS
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

# ----------------------------
# MOSTRAR LOG ACTUAL
# ----------------------------
st.markdown("### 🧾 Log de esta ejecución:")
for k, v in registro_log.items():
    st.markdown(f"- **{k}**: {v}")

# ----------------------------
# MOSTRAR HISTORIAL DE LOGS
# ----------------------------
st.markdown("### 📁 Historial de ejecuciones anteriores:")
st.dataframe(log)

# ----------------------------
# VERIFICACIÓN DE INTEGRIDAD (SHA-256)
# ----------------------------
def calcular_hash_csv(nombre_archivo):
    with open(nombre_archivo, "rb") as f:
        contenido = f.read()
        return hashlib.sha256(contenido).hexdigest()

st.markdown("### 🧪 Verificación de integridad de archivos:")
hash_compras = calcular_hash_csv("facturas_compras.csv")
hash_contabilidad = calcular_hash_csv("facturas_contabilidad.csv")

st.code(f"SHA-256 facturas_compras.csv: {hash_compras}")
st.code(f"SHA-256 facturas_contabilidad.csv: {hash_contabilidad}")

# ----------------------------
# RANKING DE USUARIOS CON MÁS DUPLICADOS
# ----------------------------
st.markdown("### 🥇 Ranking de usuarios con más facturas sospechosas:")
ranking = sospechosas["usuario_registro"].value_counts().reset_index()
ranking.columns = ["usuario_registro", "cantidad_duplicados"]
st.dataframe(ranking)
