import streamlit as st
import pandas as pd
import random

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILO
st.set_page_config(page_title="Rifa Viaje a Colombia 🇨🇴", page_icon="✈️")

# Estilo para el fondo (usando tu imagen joya rifa.jpeg)
st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url("https://raw.githubusercontent.com/TU_USUARIO/TU_REPO/main/joya%20rifa.jpeg");
        background-size: cover;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

st.title("💎 Rifa: Set Esmeraldas de Chivor")
st.subheader("Propósito: Viaje de México a Colombia ✈️")

# 2. LÓGICA DE NÚMEROS
if 'ventas' not in st.session_state:
    st.session_state.ventas = []
    st.session_state.disponibles = [f"{i:03d}" for i in range(1000)]
    random.shuffle(st.session_state.disponibles)

# 3. FORMULARIO DE VENTA MULTI-DIVISA
with st.expander("📝 REGISTRAR NUEVA VENTA", expanded=True):
    with st.form("venta"):
        nombre = st.text_input("Nombre del Comprador")
        moneda = st.selectbox("Moneda de Pago", ["COP (Colombia)", "MXN (México)", "USD (USA)"])
        
        col1, col2 = st.columns(2)
        pago_estado = col1.radio("Estado", ["Pagado", "Abono", "Debe"])
        modo_num = col2.radio("Números", ["Aleatorios (Baloto)", "Elegir uno manual"])
        
        num_manual = ""
        if modo_num == "Elegir uno manual":
            num_manual = st.text_input("Número de 3 cifras que desea el cliente (ej: 520)")

        if st.form_submit_button("💎 GENERAR 4 COMBINACIONES"):
            if nombre:
                final_nums = []
                # Si eligió uno manual, lo ponemos de primero
                if num_manual and num_manual.zfill(3) in st.session_state.disponibles:
                    final_nums.append(num_manual.zfill(3))
                    st.session_state.disponibles.remove(num_manual.zfill(3))
                
                # Completar hasta tener 4 números de 3 cifras
                while len(final_nums) < 4:
                    final_nums.append(st.session_state.disponibles.pop())
                
                # Precios según moneda del volante
                precios = {"COP (Colombia)": 25000, "MXN (México)": 110, "USD (USA)": 6.30}
                
                st.session_state.ventas.append({
                    "Cliente": nombre,
                    "Moneda": moneda,
                    "Estado": pago_estado,
                    "Números": " - ".join(final_nums),
                    "Valor Total": precios[moneda]
                })
                st.success(f"¡Éxito! Combinaciones: {', '.join(final_nums)}")
            else:
                st.error("Falta el nombre del cliente.")

# 4. TABLERO DE CONTROL FAMILIAR
st.divider()
st.write("### 📊 Control de Recaudo General")
if st.session_state.ventas:
    df = pd.DataFrame(st.session_state.ventas)
    st.dataframe(df)
    
    # Resumen por moneda
    c1, c2, c3 = st.columns(3)
    c1.metric("Recaudo COP", f"${df[df['Moneda']=='COP (Colombia)']['Valor Total'].sum():,.0f}")
    c2.metric("Recaudo MXN", f"${df[df['Moneda']=='MXN (México)']['Valor Total'].sum():,.2f}")
    c3.metric("Recaudo USD", f"${df[df['Moneda']=='USD (USA)']['Valor Total'].sum():,.2f}")
else:
    st.info("Aún no hay ventas registradas.")
