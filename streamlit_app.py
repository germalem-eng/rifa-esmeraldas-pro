import streamlit as st
import pandas as pd
import random
import base64
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Control de Rifa - Esmeraldas", page_icon="💎", layout="wide")

# Función para el fondo (Simplificada para evitar errores de carga)
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
            .stForm {{
                background-color: rgba(255, 255, 255, 0.9);
                padding: 30px;
                border-radius: 15px;
                box-shadow: 0px 4px 15px rgba(0,0,0,0.3);
            }}
            .stDataFrame {{
                background-color: rgba(255, 255, 255, 0.9);
                border-radius: 10px;
            }}
            h1, h2, h3 {{
                color: #1a472a;
                text-shadow: 1px 1px 2px white;
            }}
            </style>
            """,
            unsafe_allow_html=True
        )

set_background('fondo_rifa.jpeg')

# --- 2. GESTIÓN DE BASE DE DATOS (CSV LOCAL) ---
archivo_datos = 'base_datos_rifa.csv'

def cargar_datos():
    if os.path.exists(archivo_datos):
        return pd.read_csv(archivo_datos)
    # Columnas nuevas para tu control de Nequi/Daviplata
    return pd.DataFrame(columns=["Fecha", "Vendedor", "Cliente", "WhatsApp", "Combinaciones", "Moneda", "Metodo Pago", "Estado", "Valor Total"])

df_existente = cargar_datos()

# Lógica de números (000 al 999)
todos_los_numeros = [f"{i:03d}" for i in range(1000)]
numeros_ocupados = []
for combo in df_existente["Combinaciones"].astype(str):
    if combo != 'nan':
        numeros_ocupados.extend([n.strip() for n in combo.split(",")])
disponibles = [n for n in todos_los_numeros if n not in numeros_ocupados]

# --- 3. INTERFAZ DE REGISTRO ---
st.title("💎 Brilla con Suerte: Sorteo Set de Esmeraldas")
st.write(f"🎟️ Números disponibles: **{len(disponibles)}** de 1000")

with st.form("formulario_rifa", clear_on_submit=True):
    st.subheader("📝 Registro de Nueva Venta")
    
    col_a, col_b = st.columns(2)
    with col_a:
        vendedor = st.selectbox("👤 ¿Quién vende?", ["Hija (México)", "Hermano 1", "Hermano 2", "Gerardo"])
        nombre = st.text_input("👤 Nombre del Cliente")
        whatsapp = st.text_input("📱 WhatsApp / Contacto")
        
    with col_b:
        moneda = st.selectbox("💵 Moneda de Pago", ["COP", "MXN", "USD"])
        metodo = st.selectbox("💳 Medio de Recepción", ["Nequi", "Daviplata", "Efectivo", "Transferencia"])
        pago_estado = st.selectbox("📌 Estado del Pago", ["Pagado", "Abono", "Debe"])
    
    st.info("💡 Cada boleta asigna 4 números (1 manual opcional + 3 aleatorios).")
    num_manual = st.text_input("🔢 Número preferido (000-999) - Opcional", max_chars=3)

    if st.form_submit_button("✅ GUARDAR VENTA Y GENERAR NÚMEROS"):
        if nombre and whatsapp:
            final_nums = []
            
            # Validar número manual
            if num_manual:
                num_m = num_manual.zfill(3)
                if num_m in disponibles:
                    final_nums.append(num_m)
                    disponibles.remove(num_m)
                else:
                    st.error(f"El número {num_m} ya está vendido. Se asignarán 4 aleatorios.")

            # Completar hasta 4 números
            random.shuffle(disponibles)
            while len(final_nums) < 4:
                final_nums.append(disponibles.pop())
            
            # Precios fijos según moneda
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
            
            st.success(f"¡Venta Guardada! Números asignados: {', '.join(final_nums)}")
            st.balloons()
            st.rerun()
        else:
            st.warning("⚠️ Por favor ingresa el nombre y el contacto del cliente.")

# --- 4. TABLA DE CONTROL PARA GERARDO ---
st.divider()
st.subheader("📊 Consolidado de Ventas (Verificación Nequi/Daviplata)")
st.dataframe(df_existente, use_container_width=True)

# Botón de Descarga para respaldo
csv = df_existente.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar Reporte de Seguridad (Excel/CSV)",
    data=csv,
    file_name=f"reporte_rifa_{datetime.now().strftime('%Y%m%d')}.csv",
    mime="text/csv",
)
