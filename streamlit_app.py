import streamlit as st
import pandas as pd
import random
import base64
import os
from datetime import datetime

# --- 1. CONFIGURACIÓN ---
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
            .block-container {{padding-top: 2rem;}}
            header {{visibility: hidden;}}
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

# --- 2. BASE DE DATOS ---
archivo_datos = 'base_datos_rifa.csv'

def cargar_datos():
    if os.path.exists(archivo_datos):
        return pd.read_csv(archivo_datos)
    return pd.DataFrame(columns=["Fecha", "Vendedor", "Cliente", "WhatsApp", "Combinaciones", "Moneda", "Metodo Pago", "Estado", "Valor Total"])

if 'df_ventas' not in st.session_state:
    st.session_state.df_ventas = cargar_datos()

todos_los_numeros = [f"{i:03d}" for i in range(1000)]
ocupados = []
for c in st.session_state.df_ventas["Combinaciones"].astype(str):
    if c != 'nan':
        ocupados.extend([n.strip() for n in c.split(",")])
disponibles = [n for n in todos_los_numeros if n not in ocupados]

# --- 3. INTERFAZ ---
st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

with st.form("registro_venta", clear_on_submit=True):
    st.subheader("📝 Registro de Nueva Venta")
    
    col1, col2 = st.columns(2)
    with col1:
        vendedor = st.selectbox("👤 ¿Quién vende?", ["Mafe", "Ricardo", "Pablo", "Gerardo"])
        nombre = st.text_input("👤 Nombre del Cliente")
        whatsapp = st.text_input("📱 WhatsApp / Contacto")
    with col2:
        moneda = st.selectbox("💵 Moneda", ["COP", "MXN", "USD"])
        metodo = st.selectbox("💳 Medio", ["Nequi", "Daviplata", "Efectivo", "Transferencia"])
        estado = st.selectbox("📌 Estado", ["Pagado", "Abono", "Debe"])
    
    st.write("---")
    st.info("🎰 **Opciones de números:** Escribe uno que el cliente quiera (000-999) o deja vacío para sistema automático (Tipo Baloto).")
    num_preferido = st.text_input("🔢 Número Manual (Opcional)", value="", max_chars=3)
    
    if st.form_submit_button("✅ GENERAR Y GUARDAR VENTA"):
        if nombre and whatsapp:
            nums_asignados = []
            
            # Caso 1: El cliente eligió un número manual
            if num_preferido and num_preferido.isdigit():
                n_man = num_preferido.zfill(3)
                if n_man in disponibles:
                    nums_asignados.append(n_man)
                    disponibles.remove(n_man)
                else:
                    st.warning(f"El número {n_man} ya está vendido. Se asignarán todos automáticos.")

            # Caso 2 y completado: El sistema elige lo que falte hasta llegar a 4
            random.shuffle(disponibles)
            while len(nums_asignados) < 4:
                if disponibles:
                    nums_asignados.append(disponibles.pop())
            
            precios = {"COP": 25000, "MXN": 110, "USD": 6.30}
            
            nueva_fila = {
                "Fecha": datetime.now().strftime("%d/%m/%Y %H:%M"),
                "Vendedor": vendedor,
                "Cliente": nombre,
                "WhatsApp": whatsapp,
                "Combinaciones": ", ".join(nums_asignados),
                "Moneda": moneda,
                "Metodo Pago": metodo,
                "Estado": estado,
                "Valor Total": precios[moneda]
            }
            
            st.session_state.df_ventas = pd.concat([st.session_state.df_ventas, pd.DataFrame([nueva_fila])], ignore_index=True)
            st.session_state.df_ventas.to_csv(archivo_datos, index=False)
            
            st.success(f"✅ Venta registrada por {vendedor}. Números asignados: {', '.join(nums_asignados)}")
            st.balloons()
            st.rerun()
        else:
            st.error("⚠️ Falta el nombre o el contacto del cliente.")

# --- 4. TABLA DE CONTROL ---
st.markdown("### 📊 Historial de Ventas")
st.dataframe(st.session_state.df_ventas, use_container_width=True)

csv = st.session_state.df_ventas.to_csv(index=False).encode('utf-8')
st.download_button("📥 Descargar Reporte", data=csv, file_name="ventas_rifa.csv", mime="text/csv")
