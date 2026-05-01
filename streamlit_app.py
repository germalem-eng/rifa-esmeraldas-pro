import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import base64
from datetime import datetime

# --- 1. CONFIGURACIÓN VISUAL Y FONDO ---

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
        /* Hacer los contenedores legibles sobre el fondo */
        .stForm, .stDataFrame {
            background-color: rgba(255, 255, 255, 0.9);
            padding: 20px;
            border-radius: 10px;
        }
        </style>
        ''' % bin_str
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ No se encontró 'fondo_rifa.jpeg'. Sube la imagen a GitHub.")

set_background('fondo_rifa.jpeg')

# --- 2. CONEXIÓN A BASE DE DATOS (GOOGLE SHEETS) ---
# Se conecta usando la configuración de 'Secrets' en Streamlit Cloud
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    df_existente = conn.read(ttl="0s")
except Exception:
    st.error("Error de conexión a Google Sheets. Verifica los Secrets.")
    df_existente = pd.DataFrame()

# --- 3. LÓGICA DE NÚMEROS DISPONIBLES ---
# Generamos todos los números posibles (000-999) y quitamos los ya vendidos
todos_los_numeros = [f"{i:03d}" for i in range(1000)]
if not df_existente.empty:
    numeros_ocupados = []
    for combo in df_existente["Combinaciones"].astype(str):
        numeros_ocupados.extend([n.strip() for n in combo.split(",")])
    disponibles = [n for n in todos_los_numeros if n not in numeros_ocupados]
else:
    disponibles = todos_los_numeros

# --- 4. INTERFAZ DE REGISTRO ---
st.title("💎 Rifa: Set Esmeraldas de Chivor")
st.markdown("### Apoya el viaje de México a Colombia ✈️")

with st.form("formulario_rifa"):
    st.write("#### 📝 Registrar Venta")
    nombre = st.text_input("Nombre del Cliente")
    whatsapp = st.text_input("WhatsApp")
    
    col1, col2 = st.columns(2)
    moneda = col1.selectbox("Moneda de Pago", ["COP", "MXN", "USD"])
    pago_estado = col2.selectbox("Estado", ["Pagado", "Abono", "Debe"])
    
    modo_num = st.radio("Asignación de números", ["4 Aleatorios (Baloto)", "1 Manual + 3 Aleatorios"])
    num_manual = ""
    if modo_num == "1 Manual + 3 Aleatorios":
        num_manual = st.text_input("Escriba su número de la suerte (3 cifras):", max_chars=3)

    if st.form_submit_button("💎 GENERAR 4 COMBINACIONES Y GUARDAR"):
        if nombre and whatsapp:
            final_nums = []
            
            # Lógica para número manual
            if modo_num == "1 Manual + 3 Aleatorios" and num_manual:
                n_man = num_manual.zfill(3)
                if n_man in disponibles:
                    final_nums.append(n_man)
                    disponibles.remove(n_man)
                else:
                    st.error(f"El número {n_man} ya está vendido. Se asignarán 4 aleatorios.")

            # Completar hasta 4 combinaciones
            random.shuffle(disponibles)
            while len(final_nums) < 4:
                final_nums.append(disponibles.pop())
            
            # Precios definidos en el volante
            precios = {"COP": 25000, "MXN": 110, "USD": 6.30}
            
            # Crear nueva fila para Google Sheets
            nueva_venta = pd.DataFrame([{
                "Fecha": datetime.now().strftime("%d/%m/%Y"),
                "Cliente": nombre,
                "WhatsApp": whatsapp,
                "Combinaciones": ", ".join(final_nums),
                "Moneda": moneda,
                "Estado": pago_estado,
                "Valor Total": precios[moneda]
            }])
            
            # Actualizar base de datos
            df_final = pd.concat([df_existente, nueva_venta], ignore_index=True)
            conn.update(data=df_final)
            
            st.success(f"✅ ¡Venta Guardada! Números para {nombre}: {', '.join(final_nums)}")
            st.balloons()
        else:
            st.warning("⚠️ Por favor completa el nombre y WhatsApp.")

# --- 5. VISUALIZACIÓN DE DATOS ---
st.divider()
st.write("### 📊 Control General (Google Sheets)")
if not df_existente.empty:
    st.dataframe(df_existente, use_container_width=True)
    
    # Resumen de dinero por moneda
    c1, c2, c3 = st.columns(3)
    c1.metric("Total COP", f"${df_existente[df_existente['Moneda']=='COP']['Valor Total'].sum():,.0f}")
    c2.metric("Total MXN", f"${df_existente[df_existente['Moneda']=='MXN']['Valor Total'].sum():,.2f}")
    c3.metric("Total USD", f"${df_existente[df_existente['Moneda']=='USD']['Valor Total'].sum():,.2f}")
else:
    st.info("Aún no hay ventas registradas en la hoja de Google.")
