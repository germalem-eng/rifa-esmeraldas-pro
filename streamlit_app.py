import streamlit as st
import pandas as pd
import random
import base64
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN VISUAL Y FONDO ---
st.set_page_config(page_title="Gestión de Rifa", page_icon="💎")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        return base64.b64encode(f.read()).decode()

def set_background(png_file):
    try:
        bin_str = get_base64(png_file)
        st.markdown(f'''
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{bin_str}");
            background-size: cover;
            background-attachment: fixed;
        }}
        .stForm, .stDataFrame {{
            background-color: rgba(255, 255, 255, 0.85);
            padding: 20px;
            border-radius: 15px;
        }}
        header {{visibility: hidden;}}
        </style>
        ''', unsafe_allow_html=True)
    except: pass

set_background('fondo_rifa.jpeg')

# --- 2. GESTIÓN DE DATOS (PLAN B: ARCHIVO LOCAL) ---
archivo_datos = 'base_datos_rifa.csv'

# Función para cargar datos
def cargar_datos():
    if os.path.exists(archivo_datos):
        return pd.read_csv(archivo_datos)
    return pd.DataFrame(columns=["Fecha", "Cliente", "WhatsApp", "Combinaciones", "Moneda", "Estado", "Valor Total"])

df_existente = cargar_datos()

# Lógica de números disponibles
todos_los_numeros = [f"{i:03d}" for i in range(1000)]
numeros_ocupados = []
for combo in df_existente["Combinaciones"].astype(str):
    numeros_ocupados.extend([n.strip() for n in combo.split(",")])
disponibles = [n for n in todos_los_numeros if n not in numeros_ocupados]

# --- 3. FORMULARIO ---
st.markdown("<br><br><br><br><br>", unsafe_allow_html=True)
with st.form("formulario_rifa"):
    st.markdown("### 📝 Registro de Boletas")
    nombre = st.text_input("Nombre del Cliente")
    whatsapp = st.text_input("WhatsApp / Contacto")
    
    c1, c2 = st.columns(2)
    moneda = c1.selectbox("Moneda", ["COP", "MXN", "USD"])
    pago_estado = c2.selectbox("Estado", ["Pagado", "Abono", "Debe"])
    
    modo_num = st.radio("Asignación", ["4 Aleatorios", "1 Manual + 3 Aleatorios"])
    num_manual = st.text_input("Número manual (3 cifras)", max_chars=3) if "Manual" in modo_num else ""

    if st.form_submit_button("💎 GUARDAR VENTA"):
        if nombre and whatsapp:
            final_nums = []
            if num_manual and num_manual.zfill(3) in disponibles:
                final_nums.append(num_manual.zfill(3))
            
            random.shuffle(disponibles)
            while len(final_nums) < 4:
                final_nums.append(disponibles.pop())
            
            precios = {"COP": 25000, "MXN": 110, "USD": 6.30}
            
            nueva_venta = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Cliente": nombre,
                "WhatsApp": whatsapp,
                "Combinaciones": ", ".join(final_nums),
                "Moneda": moneda,
                "Estado": pago_estado,
                "Valor Total": precios[moneda]
            }])
            
            df_final = pd.concat([df_existente, nueva_venta], ignore_index=True)
            # GUARDADO FÍSICO
            df_final.to_csv(archivo_datos, index=False)
            
            st.success(f"✅ ¡Guardado! Números: {', '.join(final_nums)}")
            st.balloons()
            st.rerun() # Para actualizar la tabla abajo
        else:
            st.warning("⚠️ Completa los datos.")

# --- 4. TABLA DE CONTROL ---
st.divider()
st.write("### 📊 Ventas Registradas")
st.dataframe(df_existente, use_container_width=True)

# Botón para que tu hija descargue el reporte desde la web
csv = df_existente.to_csv(index=False).encode('utf-8')
st.download_button("📥 Descargar Reporte Excel (CSV)", data=csv, file_name="ventas_rifa.csv", mime="text/csv")
