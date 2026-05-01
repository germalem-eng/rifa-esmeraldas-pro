import streamlit as st
import pandas as pd
import random
import base64
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN Y ESTILO LIMPIO ---
st.set_page_config(page_title="Rifa Esmeraldas", page_icon="💎", layout="wide")

def set_background(image_file):
    if os.path.exists(image_file):
        with open(image_file, "rb") as f:
            data = f.read()
        base64_image = base64.b64encode(data).decode()
        st.markdown(
            f"""
            <style>
            .stApp {{
                background-image: url("data:image/jpge;base64,{base64_image}");
                background-size: cover;
                background-attachment: fixed;
            }}
            /* Elimina títulos amontonados y espacios extra arriba */
            .block-container {{padding-top: 2rem;}}
            header {{visibility: hidden;}}
            #brilla-con-suerte-sorteo-set-de-esmeraldas {{display: none;}}
            
            .stForm {{
                background-color: rgba(255, 255, 255, 0.9);
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

set_background('fondo_rifa.jpeg')

# --- 2. BASE DE DATOS LOCAL ---
archivo_datos = 'base_datos_rifa.csv'

def cargar_datos():
    if os.path.exists(archivo_datos):
        return pd.read_csv(archivo_datos)
    return pd.DataFrame(columns=["Fecha", "Vendedor", "Cliente", "WhatsApp", "Combinaciones", "Moneda", "Metodo Pago", "Estado", "Valor Total"])

df_existente = cargar_datos()

# Lógica de números
todos_los_numeros = [f"{i:03d}" for i in range(1000)]
numeros_ocupados = []
for combo in df_existente["Combinaciones"].astype(str):
    if combo != 'nan':
        numeros_ocupados.extend([n.strip() for n in combo.split(",")])
disponibles = [n for n in todos_los_numeros if n not in numeros_ocupados]

# --- 3. FORMULARIO DE REGISTRO ---
# Espacio para que se vea el logo de tu imagen de fondo
st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

with st.form("formulario_rifa", clear_on_submit=True):
    st.subheader("📝 Registro de Nueva Venta")
    
    col_a, col_b = st.columns(2)
    with col_a:
        # Nombres corregidos según tu instrucción
        vendedor = st.selectbox("👤 ¿Quién vende?", ["Mafe", "Ricardo", "Pablo", "Gerardo"])
        nombre = st.text_input("👤 Nombre del Cliente")
        whatsapp = st.text_input("📱 WhatsApp / Contacto")
        
    with col_b:
        moneda = st.selectbox("💵 Moneda de Pago", ["COP", "MXN", "USD"])
        metodo = st.selectbox("💳 Medio de Recepción", ["Nequi", "Daviplata", "Efectivo", "Transferencia"])
        pago_estado = st.selectbox("📌 Estado del Pago", ["Pagado", "Abono", "Debe"])
    
    num_manual = st.text_input("🔢 Número preferido (000-999) - Opcional", max_chars=3)

    if st.form_submit_button("✅ GUARDAR VENTA"):
        if nombre and whatsapp:
            final_nums = []
            if num_manual:
                num_m = num_manual.zfill(3)
                if num_m in disponibles:
                    final_nums.append(num_m)
                    disponibles.remove(num_m)
            
            random.shuffle(disponibles)
            while len(final_nums) < 4:
                final_nums.append(disponibles.pop())
            
            precios = {"COP": 25000, "MXN": 110, "USD": 6.30}
            
            nueva_venta = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Vendedor": vendedor,
                "Cliente": nombre,
                "WhatsApp": whatsapp,
                "Combinaciones": ", ".join(final_nums),
                "Moneda": moneda,
                "Metodo Pago": metodo,
                "Estado": pago_estado,
                "Valor Total": precios[moneda]
            }])
            
            df_final = pd.concat([df_existente, nueva_venta], ignore_index=True)
            df_final.to_csv(archivo_datos, index=False)
            
            st.success(f"¡Venta de {vendedor} guardada! Números: {', '.join(final_nums)}")
            st.balloons()
            st.rerun()
        else:
            st.warning("⚠️ Completa el nombre y contacto.")

# --- 4. TABLA DE CONTROL ---
st.markdown("### 📊 Ventas Registradas")
st.dataframe(df_existente, use_container_width=True)

csv = df_existente.to_csv(index=False).encode('utf-8')
st.download_button("📥 Descargar Reporte para Nequi/Daviplata", data=csv, file_name="ventas_rifa.csv", mime="text/csv")
