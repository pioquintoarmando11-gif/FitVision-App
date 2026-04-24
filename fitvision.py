import streamlit as st
import sqlite3
import google.generativeai as genai
from PIL import Image

# --- 1. CONFIGURACIÓN IA (GEMINI) ---
# REEMPLAZA EL TEXTO DE ABAJO CON TU CLAVE REAL
genai.configure(api_key="AIzaSyC5IhoVE1Bd8QUITjTHTWCnkZHfvBGNygg")
model = genai.GenerativeModel('gemini-1.5-flash')
st.set_page_config(page_title="FitVision AI", page_icon="🏋️‍♂️", layout="wide")

# --- 2. BASE DE DATOS ---
def crear_db():
    conn = sqlite3.connect('usuarios_fitness.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS usuarios (nombre TEXT, usuario TEXT PRIMARY KEY, clave TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS historial (usuario TEXT, fecha DATE, info TEXT)')
    conn.commit()
    conn.close()

crear_db()

# --- 3. ESTADO DE SESIÓN ---
if 'pantalla' not in st.session_state:
    st.session_state.pantalla = "Inicio"
    st.session_state.user = None

def cambiar_pantalla(nombre):
    st.session_state.pantalla = nombre
    st.rerun()

# --- PANTALLAS DE ACCESO (Inicio, Registro, Login) ---
if st.session_state.pantalla == "Inicio":
    st.title("🏋️‍♂️ FitVision AI")
    st.subheader("Tu asistente personal con Inteligencia Artificial")
    col1, col2 = st.columns(2)
    if col1.button("Iniciar Sesión", use_container_width=True): cambiar_pantalla("Login")
    if col2.button("Crear Cuenta", use_container_width=True): cambiar_pantalla("Registro")

elif st.session_state.pantalla == "Registro":
    st.title("📝 Crear Cuenta")
    nombre = st.text_input("Nombre completo")
    user = st.text_input("Usuario")
    pw = st.text_input("Contraseña", type="password")
    if st.button("Registrarme"):
        conn = sqlite3.connect('usuarios_fitness.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO usuarios VALUES (?,?,?)', (nombre, user, pw))
            conn.commit()
            st.success("¡Registro exitoso!")
            cambiar_pantalla("Login")
        except: st.error("El usuario ya existe.")
        conn.close()
    if st.button("Volver"): cambiar_pantalla("Inicio")

elif st.session_state.pantalla == "Login":
    st.title("🔑 Entrar")
    user = st.text_input("Usuario")
    pw = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        conn = sqlite3.connect('usuarios_fitness.db')
        c = conn.cursor()
        c.execute('SELECT * FROM usuarios WHERE usuario=? AND clave=?', (user, pw))
        if c.fetchone():
            st.session_state.user = user
            cambiar_pantalla("Menu")
        else: st.error("Datos incorrectos")
        conn.close()
    if st.button("Volver"): cambiar_pantalla("Inicio")

# --- 4. MENÚ PRINCIPAL (PANTALLA 3) ---
elif st.session_state.pantalla == "Menu":
    st.sidebar.title(f"Bienvenido, {st.session_state.user} 👋")
    opcion = st.sidebar.radio("Elige una opción:", ["🏠 Inicio", "🍎 Escáner de Comida", "💪 Mi Rutina", "📸 Mi Progreso", "💡 Consejos Fitness"])
    
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        cambiar_pantalla("Inicio")

    if opcion == "🏠 Inicio":
        st.header("🎯 Objetivo de hoy")
        st.write("Usa el menú de la izquierda para empezar a registrar tus avances.")

    elif opcion == "🍎 Escáner de Comida":
        st.header("📸 Analizador de Nutrientes")
        foto = st.camera_input("Toma una foto a tu plato")
        if foto:
            img = Image.open(foto)
            with st.spinner("La IA está analizando tu plato..."):
                prompt = f"Soy un usuario que pesa {peso}kg y mide {altura}cm. Analiza esta comida, estima calorías y proteínas, y dime si me conviene para mantenerme saludable. Sé breve."
                response = model.generate_content([prompt, img])
                st.markdown("### Resultado:")
                st.write(response.text)

    elif opcion == "💪 Mi Rutina":
        st.header("📋 Tu Entrenamiento Personalizado")
        
        # 1. Aquí eliges qué parte del cuerpo trabajar
        enfoque = st.selectbox("¿Qué te toca entrenar hoy?", ["Cuerpo Completo (Full Body)", "Torso (Pecho/Espalda)", "Pierna", "Brazo y Hombro", "Cardio e Abdominales"])

        # 2. El botón que activa a la IA
        if st.button("Generar mi rutina de hoy"):
            with st.spinner(f"El Coach IA está preparando tu rutina de {enfoque}..."):
                
                # 3. Le pedimos a Gemini que invente los ejercicios
                prompt_rutina = f"Crea una rutina de 5 ejercicios para {enfoque}. Para cada ejercicio dime: nombre, series, repeticiones y un consejo breve de técnica. Sé motivador."
                
                res = model.generate_content(prompt_rutina)
                st.markdown(f"### 🔥 Rutina para {enfoque}")
                st.write(res.text)

    elif opcion == "💡 Consejos Fitness":
        st.header("🧠 Pregúntale al Coach IA")
        pregunta = st.text_input("¿Qué duda tienes hoy?")
        if pregunta:
            res = model.generate_content(pregunta)
            st.write(res.text)

elif opcion == "📸 Mi Progreso":
        st.header("⚖️ Mi Perfil Físico")
        
        col1, col2 = st.columns(2)
        with col1:
            peso = st.number_input("Peso actual (kg):", min_value=10.0, max_value=200.0, value=70.0)
            altura = st.number_input("Altura (cm):", min_value=100, max_value=250, value=170)
        with col2:
            edad = st.number_input("Edad:", min_value=5, max_value=100, value=17)
            genero = st.selectbox("Género:", ["Hombre", "Mujer"])

        if st.button("Calcular mi estado físico"):
            # Fórmula del IMC
            altura_m = altura / 100
            imc = peso / (altura_m ** 2)
            
            st.metric("Tu IMC es:", f"{imc:.2f}")
            
            if imc < 18.5: st.warning("Bajo peso")
            elif 18.5 <= imc < 25: st.success("Peso normal (Saludable)")
            else: st.error("Sobrepeso")
            
            # Fórmula de Calorías Base (Harris-Benedict)
            tmb = (10 * peso) + (6.25 * altura) - (5 * edad) + 5
            st.write(f"🔥 Tu cuerpo quema **{tmb:.0f} calorías** al día solo por existir.")