import streamlit as st
import google.generativeai as genai
from PIL import Image
import firebase_admin
from firebase_admin import credentials, firestore

if not firebase_admin._apps:
    cred_info = st.secrets["firebase_credentials"]
    cred = credentials.Certificate(dict(cred_info))
    firebase_admin.initialize_app(cred)

db = firestore.client()
# --- 1. CONFIGURACIÓN IA (GEMINI) ---
# REEMPLAZA EL TEXTO DE ABAJO CON TU CLAVE REAL
genai.configure(api_key="AIzaSyC5IhoVE1Bd8QUITjTHTWCnkZHfvBGNygg")
model = genai.GenerativeModel('gemini-1.5-flash')
st.set_page_config(page_title="FitVision AI", page_icon="🏋️‍♂️", layout="wide")

def registrar_usuario(usuario, password, nombre_real):
    try:
        user_ref = db.collection("usuarios").document(usuario)
        user_ref.set({
            "password": password,
            "nombre": nombre_real,
            "puntos": 0
        })
        st.success(f"¡Usuario {usuario} creado con éxito! ✅")
        st.session_state.pantalla = "Login"
    except Exception as e:
        st.error(f"Error al guardar en la nube: {e}")

def validar_usuario(usuario, password):
    try:
        user_ref = db.collection("usuarios").document(usuario)
        doc = user_ref.get()
        if doc.exists:
            datos = doc.to_dict()
            if datos["password"] == password:
                return True
        return False
    except Exception as e:
        st.error(f"Error al conectar con la nube: {e}")
        return False


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
            if nombre and user and pw:
                registrar_usuario(user, pw, nombre)
            else:
                st.warning("Por favor, llena todos los campos ⚠️")
        
        # Este es el botón de la línea 81, ahora bien alineado
        if st.button("Volver"):
            st.session_state.pantalla = "Login"
            st.rerun()
           
         

elif st.session_state.pantalla == "Login":
    st.title("🔑 Entrar")
    user = st.text_input("Usuario")
    pw = st.text_input("Contraseña", type="password")
    if st.button("Ingresar"):
        # Verificamos los datos en la nube de Google
        if validar_usuario(user, pw):
            st.success(f"¡Bienvenido de nuevo, {user}! 👋")
            st.session_state.user = user
            st.session_state.logueado = True
            st.session_state.pantalla = "Menu"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos ❌")
        
       
        if st.button("Volver"):
            st.session_state.pantalla = "Inicio"
            st.rerun()

# --- 4. MENÚ PRINCIPAL (PANTALLA 3) ---
elif st.session_state.pantalla == "Menu":
    st.sidebar.title(f"Bienvenido, {st.session_state.user} 👋")
    opcion = st.sidebar.radio("Elige una opción:", ["🏠 Inicio", "🍎 Escáner de Comida", "💪 Mi Rutina", "📸 Mi Progreso", "💡 Consejos Fitness"])
    
   # Bloque 1: Cerrar Sesión
    if st.sidebar.button("Cerrar Sesión"):
        st.session_state.user = None
        cambiar_pantalla("Inicio")

    # Bloque 2: Eliminar Cuenta (FUERA del bloque anterior)
    st.sidebar.markdown("---") 
    if st.sidebar.button("⚠️ Eliminar Cuenta", type="primary"):
        try:
            db.collection("usuarios").document(st.session_state.user).delete()
            st.session_state.user = None
            # Agregamos esta línea para asegurar que se limpie el acceso
            st.session_state.logueado = False 
            cambiar_pantalla("Inicio")
            st.rerun()
        except Exception as e:
            st.sidebar.error(f"Error: {e}")

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

        # El diccionario debe tener esta sangría (8 espacios desde el borde)
        RUTINAS_AUTO = {
            "Pecho": ["Lagartijas - 4x12", "Press con mancuernas - 4x10", "Aperturas - 3x15"],
            "Pierna": ["Sentadillas - 4x12", "Desplantes - 3x15", "Peso muerto - 4x10"],
            "Espalda": ["Dominadas - 4x10", "Remo con mancuerna - 4x12", "Jalón al pecho - 3x10"],
            "Cuerpo Completo": ["Burpees - 3x10", "Sentadillas - 3x15", "Plancha - 3x45s"]
        }

        # Estas líneas TAMBIÉN deben estar hacia la derecha
        opcion_entrenamiento = st.selectbox("¿Qué quieres entrenar hoy?", ["Cuerpo Completo", "Pecho", "Pierna", "Espalda"])

        if st.button("Generar mi rutina de hoy"):
            rutina_lista = RUTINAS_AUTO.get(opcion_entrenamiento, [])
            if rutina_lista:
                st.markdown(f"### 🔥 Rutina para {opcion_entrenamiento}")
                for ejercicio in rutina_lista:
                    st.write(f"✅ {ejercicio}")
       
                
                
    elif opcion == "💡 Consejos Fitness":
        st.header("🧠 Pregúntale al Coach IA")
        
      # 1. Catálogo de consejos (Alineado con el header)
    CONSEJOS_FIT = {
        "Pierde Grasa": [
            "Mantén un déficit calórico ligero.",
            "Prioriza el consumo de proteínas.",
            "Camina al menos 10,000 pasos al día."
        ],
        "Gana Músculo": [
            "Entrena con pesas 3-4 veces por semana.",
            "Come suficiente proteína (1.5g por kilo).",
            "El descanso es cuando el músculo crece."
        ],
        "Mantener Forma": [
            "Bebe al menos 2-3 litros de agua al día.",
            "Busca un equilibrio entre cardio y pesas.",
            "La constancia es más importante que la intensidad."
        ]
    }

    # 2. Selección del objetivo
    objetivo = st.selectbox("¿Cuál es tu objetivo?", ["Pierde Grasa", "Gana Músculo", "Mantener Forma"])

    # 3. Botón para mostrar el consejo
    if st.button("Obtener mi consejo de hoy"):
        lista_consejos = CONSEJOS_FIT.get(objetivo, [])
        if lista_consejos:
            st.markdown(f"### ✨ Consejos para {objetivo}:")
            for consejo in lista_consejos:
                st.write(f"🔹 {consejo}")

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
