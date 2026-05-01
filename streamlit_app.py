import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import base64
from datetime import datetime

# --- 1. CONFIGURACIÓN VISUAL Y FONDO ---
st.set_page_config(page_title="Gestión de Rifa", page_icon="💎")

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    try:
        bin_str = get_base64(png_file)
        page_bg_img = '''
        <style>
        .stApp {
            background-image: url("data:image/png;base64,%s");
            background-size: cover;
            background-attachment: fixed;
        }
        /* Ajuste de transparencia para los formularios y tablas */
        .stForm, .stDataFrame {
            background-color: rgba(255, 255, 255, 0.85);
            padding: 20px;
            border-radius: 15px;
            border: 1px solid #ddd;
        }
        /* Ocultar el header predeterminado de Streamlit para más limpieza */
        header {visibility: hidden;}
        </style>
        ''' % bin_str
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ Sube 'fondo_rifa.jpeg' a GitHub para ver el diseño.")

set_background('fondo_rifa.jpeg')

# --- 2. CONEXIÓN A GOOGLE SHEETS ---
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_existente = conn.read(ttl="0s")
except Exception:
    st.error("Error de conexión a Google Sheets. Verifica los Secrets en Streamlit Cloud.")
    df_existente = pd.DataFrame()

# --- 3. LÓGICA DE NÚMEROS ---
todos_los_numeros = [f"{i:03d}" for i in range(1000)]
if not df_existente.empty:
    numeros_ocupados = []
    # Asegurarnos de limpiar la lista de números ocupados
    for combo in df_existente["Combinaciones"].astype(str):
        numeros_ocupados.extend([n.strip() for n in combo.split(",")])
    disponibles = [n for n in todos_los_numeros if n not in numeros_ocupados]
else:
    disponibles = todos_los_numeros

# --- 4. INTERFAZ DE REGISTRO (SIN TEXTOS DE VIAJE) ---
# Espacio superior para que se vea el logo del fondo
st.markdown("<br><br><br><br><br><br>", unsafe_allow_html=True)

with st.form("formulario_rifa"):
    st.markdown("### 📝 Registro de Boletas")
    nombre = st.text_input("Nombre del Cliente")
    whatsapp = st.text_input("WhatsApp / Contacto")
    
    c1, c2 = st.columns(2)
    moneda = c1.selectbox("Moneda", ["COP", "MXN", "USD"])
    pago_estado = c2.selectbox("Estado", ["Pagado", "Abono", "Debe"])
    
    modo_num = st.radio("Asignación de números", ["4 Aleatorios (Automático)", "1 Manual + 3 Aleatorios"])
    num_manual = ""
    if "Manual" in modo_num:
        num_manual = st.text_input("Número manual (3 cifras):", max_chars=3)

    if st.form_submit_button("💎 GENERAR Y GUARDAR"):
        if nombre and whatsapp:
            final_nums = []
            
            if "Manual" in modo_num and num_manual:
                n_man = num_manual.zfill(3)
                if n_man in disponibles:
                    final_nums.append(n_man)
                    disponibles.remove(n_man)
            
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
            conn.update(data=df_final)
            
            st.success(f"✅ ¡Guardado! Números: {', '.join(final_nums)}")
            st.balloons()
        else:
            st.warning("⚠️ Completa los datos del cliente.")

# --- 5. TABLA DE CONTROL ---
st.divider()
if not df_existente.empty:
    st.write("### 📊 Control General")
    st.dataframe(df_existente, use_container_width=True)
    
    # Resumen rápido
    r1, r2, r3 = st.columns(3)
    r1.metric("Recaudo COP", f"${df_existente[df_existente['Moneda']=='COP']['Valor Total'].sum():,.0f}")
    r2.metric("Recaudo MXN", f"${df_existente[df_existente['Moneda']=='MXN']['Valor Total'].sum():,.2f}")
    r3.metric("Recaudo USD", f"${df_existente[df_existente['Moneda']=='USD']['Valor Total'].sum():,.2f}")
